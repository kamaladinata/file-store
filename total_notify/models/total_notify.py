#coding: utf-8

import base64
import calendar
import logging
import tempfile

from calendar import monthrange
from calendar import monthcalendar
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import  _, api, fields, models
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.warning("Cannot import xlsxwriter")

@api.model
def _lang_get(self):
    languages = self.env['res.lang'].search([])
    return [(language.code, language.name) for language in languages]

def _calc_month_day_byday_and_weekday(next_month_day, byday, week_list):
    """
    Method to return month day based on week day and the number of month week
    Zero might be returned only in case the number of week is too big, e.g fith Sunday might not exists

    Args:
     * next_month_day - date.date
     * byday - the number of week in a month [1-4; -1], where 1 is the first week
     * weeklist - the weekday [0-6]

    Returns:
     * integer

    Extra info:
     * 5th and bigger byday is not supported!
    """
    monthcal = monthcalendar(year=next_month_day.year, month=next_month_day.month)
    if byday != -1:
        byday -= 1
    these_days = list(filter(bool, [week_ca[week_list] for week_ca in monthcal]))
    new_day = these_days[byday]
    return new_day


class total_notify(models.Model):
    """
    The model to prepare and forward a list of records
    """
    _name = "total.notify"
    _inherit = "mail.thread"
    _description = 'List Reminder'

    @api.model
    def _return_model(self):
        """
        The method to return available models
        """
        self._cr.execute("SELECT model, name FROM ir_model ORDER BY name")
        return self._cr.fetchall()

    @api.model
    def _return_year_month(self):
        """
        The method to return year months
        """
        month = 1
        months = []
        while month < 13:
            months.append((str(month), calendar.month_name[month]))
            month += 1
        return months

    @api.depends("period_ids", "period_ids.field_id", "period_ids.period_value",
                 "period_ids.period_type", "period_ids.inclusive_this")
    def _compute_period_title(self):
        """
        Compute method for period_title & period_domain

        Methods:
         * _return_translation_for_field_label
        """
        for notify in self:
            merged_periods = {}
            for period in notify.period_ids:
                field = notify._return_translation_for_field_label(field=period.field_id)
                if merged_periods.get(field):
                    or_str = _("or")
                    merged_periods[field] = {
                        "domain": ['|'] + merged_periods[field]["domain"] + safe_eval(period.domain),
                        "title": u"{} {} {}".format(merged_periods[field]["title"], or_str,  period.title)
                    }
                else:
                    merged_periods[field] = {
                        "domain": safe_eval(period.domain),
                        "title": period.title,
                    }
            domain = []
            title = ""
            for field, values in merged_periods.items():
                domain += values["domain"]
                title += "{}: {}; ".format(field, values["title"])
            notify.period_domain = domain
            notify.period_title = title

    @api.onchange("model")
    def _onchange_model(self):
        """
        Onchange method for model to raise warning if a user doesn't have access to it
        Clean previously selected periods, columns, domain

        Methods:
         * check of ir.model.access

        Returns:
         * Warning if a user doesn't have access to a related model
        """
        for notify in self:
            model = notify.model
            if model:
                res = self.env['ir.model.access'].check(model, "read", raise_exception=False)
                if not res:
                    notify.model = False
                    return {
                        "warning":{
                            "title": _("Access Error"),
                            "message": _(u"Sorry, you are not allowed to access the model {}".format(model))
                        }
                    }
            notify.period_ids = False
            notify.column_ids = False
            notify.domain = "[]"

    @api.onchange("include_table_in_message", "send_by_xls")
    def _onchange_send_by_xls(self):
        """
        Onchange method for include_table_in_message, send_by_xls

        Returns:
         * Warning if a both flags are not checked
        """
        for notify in self:
            if not notify.include_table_in_message and not notify.send_by_xls:
                return {
                    "warning":{
                        "title": _("Warning"),
                        "message": _(u"""
                            Select to include this list in a message or in an xls table. Otherwise,
                            an email would contain only greetings
                        """)
                    }
                }

    name = fields.Char(
        string='Reference',
        required=True,
    )
    model = fields.Selection(
        _return_model,
        string='Model',
        required=True,
    )
    domain = fields.Text(
        string="Filters",
        default="[]",
        required=True,
    )
    period_ids = fields.One2many(
        "relative.period",
        "total_notify_id",
        string="Periods",
    )
    period_domain  = fields.Char(
        string="Domain by periods",
        compute=_compute_period_title,
    )
    period_title = fields.Char(
        string="If the remider is sent today, the periods would be",
        compute=_compute_period_title,
    )
    column_ids = fields.One2many(
        'fields.line',
        'total_notify_id',
        string='Columns to show',
    )
    lang = fields.Selection(
        _lang_get,
        'Language',
        default=api.model(lambda self: self.env.lang),
    )
    include_table_in_message = fields.Boolean(
        string="List in Mail Body",
        default=True,
        help="""
            If checked, this list would be inside a message body,
            If not checked, do not forget to turn on the XLS table. Otherwise, the email
            would contain only greetings.
        """,
    )
    send_by_xls = fields.Boolean(
        string="Attach Excel Table",
        default=False,
        help="""
            If checked, the reminder would have the .xlsx table
            with all found records attached
        """,
    )
    url_included = fields.Boolean(
        string="Provide Links",
        default=True,
        help="""
            If checked, the message and the xls table would have the reference
            in each row for source Odoo record.
            If you sent this reminder for your partners, links would not have any
            use for them
        """,
    )
    extra_message = fields.Html(
        string="Message introduction",
        help="""
            This text would be included into the beginning of
            the sent message
        """,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this reminder",
    )
    # To the needs of proper recurrency (as it is done in calendar)
    last_sent_date = fields.Date(string="Last Sent Date")
    next_sent_date = fields.Date(
        string="Next To Send Date",
        default=fields.Date.today(),
    )
    interval = fields.Integer(
        string="Interval",
        default=1,
    )
    periodicity = fields.Selection(
        [
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('yearly', 'Year(s)')
        ],
        string="Repeat Every",
        default="monthly",
    )
    mo = fields.Boolean('Mon')
    tu = fields.Boolean('Tue')
    we = fields.Boolean('Wed')
    th = fields.Boolean('Thu')
    fr = fields.Boolean('Fri')
    sa = fields.Boolean('Sat')
    su = fields.Boolean('Sun')
    month_by = fields.Selection(
        [
            ('the_first_date', 'The first day'),
            ('the_last_date', 'The last day'),
            ('date', 'Date of month'),
            ('day', 'Day of month')
        ],
        string='Option',
        default='date',
    )
    day = fields.Integer('Day of month', default=1)
    year_day = fields.Integer('Month Day', default=1)
    year_month = fields.Selection(
        _return_year_month,
        string="Month",
        default="1",
    )
    week_list = fields.Selection(
        [
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday')
        ],
        string='Weekday',
    )
    byday = fields.Selection(
        [
            ('1', 'First'),
            ('2', 'Second'),
            ('3', 'Third'),
            ('4', 'Fourth'),
            ('-1', 'Last')
        ],
        string='By day',
    )

    _sql_constraints = [
        ('interval_check', 'check (interval>0)', _('Repeat interval should be positive!')),
    ]

    def read(self, fields=None, load='_classic_read'):
        """
        Rewrite to add the extra check for model

        Methods:
         * check_reminder_model_access()
        """
        res = super(total_notify, self).read(fields=fields, load=load)
        for notify in self:
            check_access = notify.check_reminder_model_access()
            if not check_access:
                raise AccessError(_("Sorry, you are not allowed to access the model {}".format(notify.model)))
        return res

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        Rewrite to exlude not allowed reminders accoriding to the model

        Methods:
         * check_reminder_model_access()

        Extra info:
         * self.browse(ids) - do not use sudo() here, hence check would be under SuperUser
        """
        ids = super(total_notify, self)._search(
            args=args, offset=offset, limit=limit, order=order, count=False, access_rights_uid=access_rights_uid,
        )
        notify_ids = self.browse(ids)
        for notify in notify_ids:
            check_access = notify.check_reminder_model_access()
            if not check_access:
                ids.remove(notify.id)
        return count and len(ids) or ids

    def check_reminder_model_access(self):
        """
        Method to check whether a user has access to this reminder according to the model specified

        Returns:
         * Boolean

        Extra info:
         * sudo() in self.sudo().model is absolutely necessary, since it itself make 'read()'
         * Expected singleton
        """
        self.ensure_one()
        res = True
        model = self.sudo().model
        if model:
            res = self.env['ir.model.access'].check(model, "read", raise_exception=False)
        return res

    def _return_records_filtered(self):
        """
        The method to find instances by filters and restrictions indicated in the record

        Returns:
         * recordset of defined model

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        domain = safe_eval(self.period_domain) + safe_eval(self.domain)
        res = self.env[self.model].search(domain)
        return res

    def _prepare_values(self):
        """
        The method to prepare values for rendering in email temlates and xls

        1. For selection options we need the value, not the key
        2. For date and datetime we should parse to string according to lang format
        3. For not relational field we just retrieve the value from field
        4. For relational fields without complementary fields we use the object name
        5. For relational fields with complementary field of selection type we should also retrieve value
        6. For relational fields with complementary field of m2o type we get name of complementary field
        7. For relational fields with complementary field of not m2o type we get complementary value
        8. O2m & M2m fields are not possible here, but for sudden cases we check it
        9. Find totals

        Methods:
         * _return_records_filtered
         * _prepare_string_on_x2m_values
         * _prepare_record_url
         * _description_selection of 'Selection'
         * _parse_selection_value

        Returns:
         * column_names - list
         * columns - list of lists.
         * group_operators - list

        Extra info:
         * We do not use in return list of dicts, since a single column name might be introduced a few times
         * Expected singleton
        """
        self.ensure_one()
        self = self.with_context(lang=self.lang) # Since we are under admin, we use lang of total.notify object
        record_lang = self.env['res.lang'].search([("code", "=", self.lang)], limit=1)
        lang_date_format = record_lang and record_lang.date_format or "%m/%d/%Y"
        lang_datetime_format = record_lang and "{} {}".format(lang_date_format, record_lang.time_format) \
                               or "%m/%d/%Y %H:%M:%S"
        records = self._return_records_filtered()
        column_names = [" "] + [column.field_label for column in self.column_ids]
        columns = []
        row_number = 0
        for record in records:
            row_number += 1
            record_url = self.url_included and self._prepare_record_url(record=record) or row_number
            values = [record_url]
            for column in self.column_ids:
                column_name = column.field_id.name
                field = record[column_name]
                field_type = column.field_id.ttype
                related_field = column.related_field
                if field_type in ["selection"]:
                    # 1
                    try:
                        column_value = dict((record._fields[column_name]._description_selection(self.env)))[field]
                    except:
                        column_value = field
                elif field_type in ["date"]:
                    # 2
                    column_value = field and field.strftime(lang_date_format) or False
                elif field_type in ["datetime"]:
                    # 2
                    column_value = field and field.strftime(lang_datetime_format) or False
                elif field_type not in ['many2one', 'one2many', 'many2many']:
                    # 3
                    column_value = field
                else:
                    if not column.related_field:
                        # 4
                        column_value = field_type in ['many2one'] \
                                       and field.name \
                                       or self._prepare_string_on_x2m_values(field=field)
                    else:
                        if related_field.ttype in ["selection"]:
                            # 5
                            column_value = field_type in ['many2one'] \
                                           and self._parse_selection_value(field=field, field_name=related_field.name)\
                                           or self._prepare_string_on_x2m_values(
                                                                                field=field,
                                                                                relational_field=related_field.name,
                                                                                selection_field=True,
                                                                            )
                        elif related_field.ttype in ["many2one"]:
                            # 6
                            column_value = field_type in ['many2one'] \
                                           and field[related_field.name].name \
                                           or self._prepare_string_on_x2m_values(
                                                                                field=field,
                                                                                relational_field=related_field.name,
                                                                                relational_m2o=True,
                                                                            )
                        elif related_field.ttype not in ["many2many", "one2many"]:
                            # 7
                            column_value = field_type in ['many2one'] \
                                           and field[related_field.name] \
                                           or self._prepare_string_on_x2m_values(
                                                                                field=field,
                                                                                relational_field=related_field.name,
                                                                            )
                        else:
                            # 8
                            raise UserError(_(u"Many2many and One2many fields are not supported as complementaries"))
                if column_value != 0 and (not column_value or column_value == "False"):
                    column_value = "-----"
                values.append(column_value)
            columns.append(values)
        # 9
        group_operators = [" "]
        for column in self.column_ids:
            if column.group_operator:
                new_value = 0
                column_name = column.field_id.name
                related_field_name = column.related_field and column.related_field.name or False
                for record in records:
                    if related_field_name:
                        new_value += record[column_name][related_field_name] or 0
                    else:
                        new_value += record[column_name] or 0
                if column.group_operator == "sum":
                    new_value = round(new_value, 2)
                elif column.group_operator == "average":
                    new_value = round(new_value / len(records), 2)   
                else:
                    new_value = " "            
            else:
                new_value = " "
            group_operators.append(new_value)
        
        total_need = [operator for operator in group_operators if operator != " "]
        group_operators = total_need and group_operators or False
        return column_names, columns, group_operators

    @api.model
    def _get_default_xlsx_styles(self, workbook):
        """
        Return dict with default workbook.style for xlsx printouts
        """
        styles = {
            'main_header_style': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'border': 1,
            }),
            'main_data_style': workbook.add_format({
                'font_size': 11,
                'border': 1,
            }),
        }
        return styles

    def _prepare_xls_table(self, columns, instances, group_operators):
        """
        Method to generate an attachment if necessary

        1. Prepare workbook and styles
        2. Prepare header row
          2.1 Get column name like 'A' or 'S' (ascii char depends on counter)
          2.2 Calculate column widt based on value inside. The min is 20
        3. Prepare each row of instances
        4. Prepare total line
        5. Create an attachment

        Args:
         * columns - list of column names
         * instances - list of lists of each row values
         * group_operators - list

        Methods:
         * _get_default_xlsx_styles

        Returns:
         * ir.attachment object

        Extra info:
         * There should be proper lang in context
         * Expected singleton
        """
        self.ensure_one()
        # 1
        file_path = tempfile.mktemp(suffix='.xlsx')
        workbook = xlsxwriter.Workbook(file_path)
        styles = self._get_default_xlsx_styles(workbook)
        worksheet = workbook.add_worksheet(self.name)
        # 2
        cur_column = 0
        for column in columns:
            column = cur_column == 0 and "#" or column
            worksheet.write(0, cur_column, column, styles.get("main_header_style"))
            # 2.1
            col_letter = chr(cur_column + 97).upper()
            # 2.2
            column_width = len(column) + 2 > 20 and len(column) + 2 or 20
            worksheet.set_column('{c}:{c}'.format(c=col_letter), column_width)
            cur_column += 1
        # 3
        row = 1
        for instance in instances:
            for counter, column in enumerate(instance):
                value = column
                worksheet.write(
                    row,
                    counter,
                    value,
                    styles.get("main_data_style")
                )
            row += 1
        # 4
        if group_operators:
            for counter, group_operator in enumerate(group_operators):
                value = group_operator
                worksheet.write(
                    row,
                    counter,
                    value,
                    styles.get("main_header_style")
                )                
        workbook.close()
        # 5
        with open(file_path, 'rb') as r:
            xls_file = base64.b64encode(r.read())
        att_vals = {
            'name':  u"{}#{}.xls".format(self.name, self.period_title),
            'type': 'binary',
            'datas': xls_file,
        }
        attachment_id = self.env['ir.attachment'].create(att_vals)
        return attachment_id

    def _prepare_and_send_email(self, attachment_id=False):
        """
        The method to render template and sent message

        Args:
         * attachment_id - ir.attachment object

        Methods:
         * message_post of mail.thread
         * _prepare_xls_table
         * unlink of ir.attachment - not to keep useless files
         * _calc_the_next_sent_date

        Attrs update:
         * last_sent_date

        Extra info:
         * There should be proper lang in context
         * Expected singleton
        """
        self.ensure_one()
        template_id = self.env.ref("total_notify.total_notify_template")
        body_html = template_id._render_template(
            template_id.body_html,
            'total.notify',
            self.id,
        )
        subject = "{}: {}".format(self.name, self.period_title)
        if self.send_by_xls:
            attachment_id = self._prepare_xls_table(
                columns=self._context.get("columns"),
                instances=self._context.get("instances"),
                group_operators=self._context.get("group_operators"), 
            )
            self.with_context(has_button_access=False).message_post(
                body=body_html,
                subject=subject,
                subtype="mail.mt_comment",
                attachments=[(attachment_id['name'], base64.b64decode(attachment_id['datas']))],
            )
            attachment_id.unlink()
        else:
            self.message_post(
                body=body_html,
                subject=subject,
                subtype="mail.mt_comment",
            )
        self.last_sent_date = fields.Date.today()
        self.next_sent_date = self._calc_the_next_sent_date()

    def action_make_notification(self):
        """
        Method to find the objects and send a correct reminder


        Methods:
         * _prepare_values
         * _prepare_and_send_email

        Extra info:
         * We are under sudo() to find all documents disregarding current user accesses
        """
        self = self.sudo()
        for notify in self:
            lang = notify.lang or self.env.user.lang
            columns, instances, group_operators = notify.with_context(lang=lang)._prepare_values()
            if instances:
                notify.with_context(
                    columns=columns,
                    instances=instances,
                    group_operators=group_operators,
                    title=notify.period_title,
                    lang=lang,
                )._prepare_and_send_email()
            else:
                _logger.info(u"For the reminder {} ({}) no instances are found".format(notify.name, notify.id))

    @api.model
    def _parse_selection_value(self, field, field_name):
        """
        The method to parse seleciton value for given field and key

        Args:
         * field - ir.models.fields object
         * field_name - char

        Methods:
        * _description_selection of 'Selection'

        Returns:
         * char
        """
        try:
            selection_value = dict((field._fields[field_name]._description_selection(self.env)))[field[field_name]]
        except:
            selection_value = field[field_name]
        return selection_value

    @api.model
    def _prepare_string_on_x2m_values(self, field, relational_field=False, relational_m2o=False, selection_field=False):
        """
        Method to make string from x2m fields

        Args:
         * field - xm2 ir.model.fields object
         * relational_field - name of related field if exist, False otherwise
         * relational_m2o - in case relation is of m2o type
         * selection_field - in case relation is of selection type

        Methods:
         * _parse_selection_value

        Returns:
         * char
        """
        res = ""
        if not relational_field:
            res = ', '.join([instance.name_get()[0][1] for instance in field])
        else:
            if selection_field:
                res = ', '.join(
                    [str(self._parse_selection_value(field=instance, field_name=relational_field)) for instance
                    in field]
                )
            elif relational_m2o:
                res = ', '.join(
                  [str(instance[relational_field] and instance[relational_field].name_get()[0][1] or False) for instance
                   in field]
                )
            else:
                res = ', '.join([str(instance[relational_field]) for instance in field])
        return res

    @api.model
    def _prepare_record_url(self, record):
        """
        The method to retrieve record backend url

        Args:
         * record - instance of some Odoo model

        Returns:
         * Char
        """
        ICPSudo = self.env['ir.config_parameter'].sudo()
        base_url = ICPSudo.get_param('web.base.url', default='http://localhost:8069')
        dbname = self.env.cr.dbname
        url = "{}/web?db={}#id={}&view_type=form&model={}".format(base_url, dbname, record.id, record._name)
        return url

    def _return_translation_for_field_label(self, field):
        """
        The method to return translation for field label

        Args:
         * ir.model.fields object

        Returns:
         * char

        Extra info:
         * Expected singleton or empty recordset
        """
        lang = self.lang or self.env.user.lang
        return  field.with_context(lang=lang).field_description

    def _calc_the_next_sent_date(self):
        """
        Method to find the next date by the setting
         1. We are from today not from the last_sent_date no to make excess repeats
         2. Althoug the period is weekly, it might be this week by days. If the days are not define, it just a week dif
         3. In case a day is not found (e.g. 30th in February, we get the last month day)

        Returns:
         * date.date()

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        periodicity = self.periodicity
        interval = self.interval
        # 1
        today = fields.Date.from_string(fields.Date.today())
        res_date = False
        if periodicity == "daily":
            res_date = today + relativedelta(days=interval)
        elif periodicity == "weekly":
            current_week_day = today.weekday()
            wd_ids = ["mo", "tu", "we", "th", "fr", "sa", "su"]
            time_delta = 7 * interval
            # 2
            for wd in wd_ids[current_week_day+1:7]:
                # Firstly search in this week days
                if self[wd]:
                    time_delta = wd_ids.index(wd) - current_week_day
                    break
            if time_delta == 7 * interval:
                # Then search in the next week
                for wd in wd_ids[0:current_week_day]:
                    if self[wd]:
                        time_delta = (7 * interval) + (wd_ids.index(wd) - current_week_day)
                        break
            # if no other days, just go to the next interval
            res_date = today + relativedelta(days=time_delta)
        elif periodicity == "monthly":
            month_by = self.month_by
            next_month_day = today + relativedelta(months=interval)
            first_month_date = date(
                year=next_month_day.year,
                month=next_month_day.month,
                day=1
            )
            last_month_date = date(
                year=next_month_day.year,
                month=next_month_day.month,
                day=monthrange(next_month_day.year, next_month_day.month)[1],
            )
            if month_by in ["the_first_date"]:
                res_date = first_month_date
            elif month_by in ["the_last_date"]:
                res_date = last_month_date
            elif month_by in ["day"]:
                byday = int(self.byday)
                week_list = int(self.week_list)
                new_day = _calc_month_day_byday_and_weekday(
                    next_month_day=next_month_day,
                    byday=byday,
                    week_list=week_list,
                )
                res_date = date(
                    year=next_month_day.year,
                    month=next_month_day.month,
                    day=new_day,
                )
            elif month_by in ["date"]:
                # 3
                try:
                    res_date = date(
                        year=next_month_day.year,
                        month=next_month_day.month,
                        day=self.day,
                    )
                except:
                    next_month_day = last_month_date
        elif periodicity == "yearly":
            the_next_year_day = today + relativedelta(years=interval)
            try:
                res_date = date(
                    year=the_next_year_day.year,
                    month=int(self.year_month),
                    day=self.year_day,
                )
            except:
                res_date = date(
                    year=the_next_year_day.year,
                    month=int(self.year_month),
                    day=monthrange(the_next_year_day.year, int(self.year_month))[1],
                )
        return res_date

    @api.model
    def send_reminders(self):
        """
        Method to find reminders to send based on recurrence and send them

        Methods:
         * action_make_notification
        """
        today = fields.Date.today()
        reminders = self.search(["|", ("next_sent_date", "<=", today), ("next_sent_date", "=", False)])
        _logger.info("Notifications job for reminders {} are started to be prepared".format(reminders))
        for reminder in reminders:
            # We are in loop to make commit after each reminder is sent
            reminder.action_make_notification()
            self.env.cr.commit()

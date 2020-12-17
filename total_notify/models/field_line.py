#coding: utf-8

from odoo import  api, fields, models


class field_line(models.Model):
    """
    The model to keep a list column
    """
    _name = "fields.line"
    _description = 'Field Line'

    @api.depends("field_id", "related_field")
    def _compute_model_from_field_id(self):
        """
        Compute method for model_from_field_id and for field_ttype

        Attrs update:
         * model_from_field_id - as model of linked field if exist
        """
        for line in self:
            model_from_field_id = False
            field = line.field_id
            if field and field.ttype in ["many2one", "one2many", "many2many"]:
                model_from_field_id = self.env['ir.model'].search(
                    [('model', '=', field.relation)],
                    limit=1,
                )
            line.model_from_field_id = model_from_field_id
            field = line.related_field or line.field_id or False
            line.field_ttype = field and field.ttype or False

    @api.onchange('field_id', 'related_field')
    def onchange_field_id(self):
        """
        Onchange method for field_id and related_field
        The goal is to take translated version of field (field_description doesn't have own)
        To forbid inviable fields

        Methods:
         * _return_translation_for_field_label of total.notify
        """
        for line in self:
            field = line.related_field or line.field_id or False
            if line.related_field and line.related_field.model_id != line.model_from_field_id:
                line.related_field = False
            if field:
                line.field_label = line.total_notify_id._return_translation_for_field_label(field=field)         
            if not field or field.ttype not in ['float', 'integer', 'monetary']:
                line.group_operator = False

    sequence = fields.Integer(string='Sequence')
    total_notify_id = fields.Many2one(
        'total.notify',
        string='Notification',
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        string='Column',
        required=True,
    )
    field_label = fields.Char(
        string='Label',
        required=True
    )
    model_from_field_id = fields.Many2one(
        "ir.model",
        string="Model",
        compute=_compute_model_from_field_id,
        store=True,
        help="""
            Technical field to restrict selection of fields related only to this many2one model
        """,
    )
    field_ttype = fields.Char(
        compute=_compute_model_from_field_id,
        store=True,
        string="Field Type",
    )
    related_field = fields.Many2one(
        'ir.model.fields',
        string=u"Complementary",
        required=False,
    )
    group_operator = fields.Selection(
        [
            ("sum", "Sum"),
            ("average", "Average")
        ],
        string="Total Operator",
        help="What to show as a table total. Available only for numbers",
    )

    _order = "sequence, id"

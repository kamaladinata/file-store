# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	send_overdue_statement = fields.Boolean(related='company_id.send_overdue_statement',string="Send Overdue Customer Statement",readonly=False)
	overdue_days = fields.Integer(related='company_id.overdue_days',string="Overdue Date",readonly=False)
	overdue_statement_template_id = fields.Many2one('mail.template', 'Overdue Statement  Template', related='company_id.overdue_statement_template_id', readonly=False)

	send_statement = fields.Boolean(related='company_id.send_statement',string="Send Customer Statement",readonly=False)
	
	auto_monthly_statement = fields.Boolean(related='company_id.auto_monthly_statement',readonly=False,string="Auto Monthly Statement")
	auto_weekly_statement = fields.Boolean(related='company_id.auto_weekly_statement',readonly=False,string="Auto Weekly Statement")

	weekly_days = fields.Selection([
		('0', 'Monday'),
		('1', 'Tuesday'),
		('2', 'Wednesday'),
		('3', 'Thursday'),
		('4', 'Friday'),
		('5', 'Saturday'),
		('6', 'Sunday'),
	],related='company_id.weekly_days',string="Weekly Send Day",readonly=False)
	statement_days = fields.Integer(related='company_id.statement_days',string="Monthly Send Day",readonly=False)
	
	weekly_template_id = fields.Many2one('mail.template', string='Weekly Statement  Template', related='company_id.weekly_template_id', readonly=False)
	monthly_template_id = fields.Many2one('mail.template', string='Monthly Statement  Template', related='company_id.monthly_template_id', readonly=False)
	
	# period = fields.Selection([('weekly', 'Weekly'),('monthly', 'Monthly'),('all', "All")],'Period',related='company_id.period',readonly=False)
	# filter_statement = fields.Selection([('filter_only','View Only Filter Statements'),('all_statement','View All Statements Along With Filter Statements')],string="Filter Statement",related='company_id.filter_statement')
	

	@api.constrains ('statement_days')
	def _check_statement_days(self):
		if self.send_statement:
			if self.statement_days > 31 or self.statement_days <= 0:
				raise ValidationError(_('Enter Valid Statement Date Range'))
	
	@api.constrains('overdue_days')
	def _check_overdue_days(self):
		if self.send_overdue_statement:
			if self.overdue_days > 31 or self.overdue_days <= 0:
				raise ValidationError(_('Enter Valid Overdue Statement Date Range'))

	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		res.update(
			auto_weekly_statement = self.company_id.auto_weekly_statement,
			auto_monthly_statement = self.company_id.auto_monthly_statement,
			send_statement=self.company_id.send_statement,
			statement_days=self.company_id.statement_days,
			overdue_days=self.company_id.overdue_days,
			weekly_days=self.company_id.weekly_days,
			send_overdue_statement=self.company_id.send_overdue_statement,
			weekly_template_id = self.company_id.weekly_template_id.id,
			monthly_template_id = self.company_id.monthly_template_id.id,
			overdue_statement_template_id = self.company_id.overdue_statement_template_id.id,
		)
		return res
	
	def set_values(self):
		super(ResConfigSettings, self).set_values()
		
		self.company_id.send_statement = self.send_statement
		self.company_id.send_overdue_statement = self.send_overdue_statement
		self.company_id.statement_days = self.statement_days
		self.company_id.overdue_days = self.overdue_days
		self.company_id.weekly_days = self.weekly_days
		self.company_id.auto_monthly_statement = self.auto_monthly_statement
		self.company_id.auto_weekly_statement = self.auto_weekly_statement

		self.company_id.weekly_template_id = self.weekly_template_id.id
		self.company_id.monthly_template_id = self.monthly_template_id.id
		self.company_id.overdue_statement_template_id = self.overdue_statement_template_id.id

		if self.send_overdue_statement:
			overdue_cron = self.env['ir.model.data'].xmlid_to_object('bi_customer_overdue_statement.autometic_send_overdue_statement_cron')
			overdue_cron.active = self.send_overdue_statement
			cron_datetime = self.change_cron_time(self.overdue_days)
			overdue_cron.nextcall = str(cron_datetime)
		
		if self.send_statement:
			if self.auto_monthly_statement:
				statement_cron = self.env['ir.model.data'].xmlid_to_object('bi_customer_overdue_statement.autometic_send_monthly_statement_cron')
				statement_cron.active = self.auto_monthly_statement
				cron_datetime = self.change_cron_time(self.statement_days)
				statement_cron.nextcall = str(cron_datetime)

	def change_cron_time(self,days):
		now = datetime.now()
		
		current_month = now.month
		current_date = now.day
		current_year = now.year
		expected_date = datetime(now.year, now.month, days,now.hour, now.minute, now.second)
		
		cron_datetime = expected_date
		
		if current_date>days:
			cron_datetime = expected_date + relativedelta(months=+1)
		return cron_datetime
	
	

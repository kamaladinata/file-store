# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
# Developed By: Jahangir
#################################################################################


from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)


class EmailVerificationConfig (models.TransientModel):
	_name = 'email.verification.config'
	_inherit = 'webkul.website.addons'


	token_validity = fields.Integer(
		string='Token Validity In Days',
		help="Validity of the token in days sent in email. If validity is 0 it means infinite.",
		
	  )
	restrict_unverified_users = fields.Boolean(
		string='Restrict Unverified Users From Checkout',
		help="If enabled unverified users can not proceed to checkout untill they verify their emails")

	@api.multi
	def set_values(self):
		super(EmailVerificationConfig, self).set_values()
		IrDefault = self.env['ir.default'].sudo()
		IrDefault.set('email.verification.config','token_validity', self.token_validity)
		IrDefault.set('email.verification.config','restrict_unverified_users', self.restrict_unverified_users)

	@api.multi
	def get_values(self):
		res = super(EmailVerificationConfig, self).get_values()
		IrDefault = self.env['ir.default'].sudo()
		res.update({
			'token_validity':IrDefault.get('email.verification.config','token_validity', self.token_validity) or 2,
			'restrict_unverified_users':IrDefault.get('email.verification.config', 'restrict_unverified_users', self.restrict_unverified_users) or True
		})
		return res
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
from openerp import api, fields , models
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'
   
    @api.model
    def check_email_is_validated(self):
        current_user = self.env['res.users'].sudo().browse(self._uid)
        status = 'verified'
        restrict_users = self.env['ir.default'].sudo().get('email.verification.config', 'restrict_unverified_users')
        if restrict_users:
            if not current_user.wk_token_verified:
                if not current_user.signup_valid:
                    status = 'expired'
                else:
                    status = 'unverified'
        return status

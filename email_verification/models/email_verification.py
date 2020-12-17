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

from odoo import api, fields, models, _
from odoo.addons.auth_signup.models.res_partner import now
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    wk_token_verified = fields.Boolean(
        string='Token Verified', default=True)

    @api.model
    def send_verification_email(self, res_id):
        user = self.browse(res_id)
        validity = self.env['ir.default'].sudo().get('email.verification.config', 'token_validity')
        expiration = now(days=+validity)
        temp_id = self.env.ref('email_verification.wk_email_verification_email_template_id')
        user.partner_id.signup_prepare(signup_type="verify", expiration=expiration)
        signup_type = user.partner_id.signup_type
        if 'verify' == signup_type:
            user.partner_id.signup_prepare(signup_type="reset", expiration=expiration)
        if temp_id:
            try:
                res = temp_id.send_mail(res_id, True)
            except Exception as e:
                return False
        return True

    @api.model
    def create(self, vals):
        vals['wk_token_verified'] = False
        res_id = super(ResUsers, self).create(vals)
        self.send_verification_email(res_id.id)
        return res_id

    @api.model
    def get_verification_url(self):
        db =self._cr.dbname
        if self.signup_token and db:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            redirect_url = '/web/login'
            url = "%s/web/email/verification?db=%s&wk_token=%s&wk_uid=%s"%(base_url, db,self.signup_token,self.id)
            return url
        return False

    @api.model
    def wk_verify_email(self, params={}):
        status = 'error'
        msg = "Oops!!. There is some error currently please try after some time." 
        try:
            if params.get('wk_token') and params.get('wk_uid') and params.get('db'):
                uid = int(params.get('wk_uid'))
                token = str(params.get('wk_token'))
                user = request.env['res.users'].sudo().browse(uid)
                msg = "Your account has been verified. You will be automatically redirected to login page."
                if not user.wk_token_verified:
                    if user.signup_token == token:
                        if not user.signup_valid:
                            status = 'expired'
                            msg = "This link has been expired. Resend a new verification link from your account."
                        else:
                            user.wk_token_verified = True
                            status = 'verified'
                    else:   
                        status = 'unverified'
                        msg = "The account is not verified yet. Resend a new verification link from your account."
                else:
                    status = 'already_verified'
                    msg = "Your account has already been verified. You will be automatically redirected to login page."
        except Exception as e:
            status = 'error'
            msg = "Oops!!. There is some error currently please try after some time." 
        return {'status':status,'msg':msg}

    @api.multi
    def resend_verification_user_email(self):
        msg =  "A new email has been sent to this user successfully."
        res = self.send_verification_email(self.id)
        if not res:        
            msg = 'Exception in sending the email. Please try again later.'
        wizard_id = self.env['wizard.message'].create(
                {'text': msg})
        return {'name': _("Summary"),
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'wizard.message',
                'res_id': wizard_id.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                }
    @api.multi
    def verify_email_manually(self):
        self.wk_token_verified = True
        wizard_id = self.env['wizard.message'].create(
                {'text': "Email has been verified manually!!"})
        return {'name': _("Summary"),
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'wizard.message',
                'res_id': wizard_id.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                }
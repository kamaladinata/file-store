
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
import logging
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
import werkzeug.utils
from odoo.addons.web.controllers.main import  Home
_logger = logging.getLogger(__name__)
class Home(Home):

    @http.route('/web/email/verification', type='http', auth="none")
    def web_email_verification(self, redirect=None, **kw):
        res = request.env['res.users'].wk_verify_email(kw)
        return request.render('email_verification.email_verification_template',{'status':res['status'],'msg':res['msg']})
    
    @http.route('/resend/email', type='http', auth='public', website=True)
    def resend_email(self, *args, **kw):
        request.env['res.users'].sudo().send_verification_email(request.uid)
        return 
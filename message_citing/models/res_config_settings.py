# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval

class res_config_settings(models.TransientModel):
    """
    Overwrite to add mail routing settings
    """
    _inherit = "res.config.settings"

    message_citing_header = fields.Html(string="Cited Message Header")

    @api.model
    def get_values(self):
        """
        Overwrite to add new system params
        """
        res = super(res_config_settings, self).get_values()
        Config = self.env['ir.config_parameter'].sudo()
        message_citing_header = Config.get_param("message_citing_header", "")
        values = {"message_citing_header": message_citing_header,}
        res.update(values)
        return res

    @api.model
    def set_values(self):
        """
        Overwrite to add new system params
        """
        super(res_config_settings, self).set_values()
        Config = self.env['ir.config_parameter'].sudo()
        Config.set_param("message_citing_header", self.message_citing_header)

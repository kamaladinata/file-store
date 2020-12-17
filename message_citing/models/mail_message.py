# -*- coding: utf-8 -*-

from odoo import models


class mail_message(models.Model):
    """
    Overwrite to introduce js methods for citing messages
    """
    _inherit = 'mail.message'

    def return_message_search(self, res_model, res_id):
        """
        The method to return message search view

        Args:
         * res_model - model name
         * res_id - id of document

        Methods:
         * _return_tags_for_document

        Returns:
         * list of:
          ** dict for article search action
          ** cited header  
        """
        view_id = self.env.ref('message_citing.cite_message_form_view').id
        context = self.env.context.copy()
        context.update({"default_model": res_model, "default_res_id": res_id})
        res = {
            "view_id": view_id,
            "context": context,
        }
        Config = self.env['ir.config_parameter'].sudo()
        cited_header = Config.get_param("message_citing_header", "")
        cited_header = cited_header and "<br/>" + cited_header or ""
        return [res, cited_header]

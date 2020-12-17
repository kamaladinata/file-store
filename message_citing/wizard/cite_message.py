# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

class cite_message(models.TransientModel):
    """
    The model to search and select messages
    """
    _name = "cite.message"
    _description = "Cite Message"

    @api.onchange("model", "res_id")
    def _onchange_model(self):
        """
        Onchange method for model

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        if self.model and self.res_id:
            self.current_thread = True
        else:
            self.current_thread = False

    @api.onchange("current_thread", "author_id", "email_from", "subject", "body", "date_start", "date_end",)
    def _onchange_current_thread(self):
        """
        Onchnage method for current_thread, author_id, email_from, body, date_start, date_end

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        domain = []
        if self.current_thread:
            domain += [("model", "=", self.model), ("res_id", "=", self.res_id)]
        if self.author_id:
            domain += [("author_id", "=", self.author_id.id)]
        if self.email_from:
            domain += [("email_from", "ilike", self.email_from)]
        if self.subject:
            domain += [("subject", "ilike", self.subject)]
        if self.body:
            domain += [("body", "ilike", self.body)]
        if self.date_start:
            domain += [("date", ">=", fields.Datetime.to_string(self.date_start))]
        if self.date_end:
            domain += [("date", "<=", fields.Datetime.to_string(self.date_end))]
        str_domain = str(domain)
        if str_domain != self.domain:
            self.domain = str_domain
        self.domain = str(domain)

    @api.onchange("domain")
    def _onchange_domain(self):
        """
        Onchange method for domain

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        domain = safe_eval(self.domain)
        cited_message_ids = self.env["mail.message"]._search(domain)
        self.cited_message_ids = [(6, 0, cited_message_ids)]

    current_thread = fields.Boolean(string="Only the same thread",)
    model = fields.Char(string="Model")
    res_id = fields.Integer(string="Res ID")
    author_id = fields.Many2one(
        "res.partner",
        string="Author",
    )
    email_from = fields.Char(string="Email From")
    subject = fields.Char(string="Subject")
    body = fields.Char(string="Contents")
    date_start = fields.Datetime(string="Date")
    date_end = fields.Datetime(string="Date end")
    domain = fields.Char(string="Domain", default="[]")
    cited_message_ids = fields.Many2many(
        "mail.message",
        "mail_message_cite_message_rel_table",
        "mail_message_id",
        "cite_message_id",
        string="Messages",
    )

from odoo import api, fields, models, _

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def send_mail(self, auto_commit=False):
        active_model = self._context.get('active_model')
        model_desc = self._context.get('model_description')
        if active_model == 'account.move' and not model_desc:
            ctx = self.set_account_move_context(self._context)
            self = self.with_context(ctx)
        res = super(MailComposer, self).send_mail(auto_commit=False)
        return res

    def set_account_move_context(self,context):
        ctx = context.copy()
        record = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
        if record.type == 'out_invoice':
            ctx['model_description'] = 'Invoice'
        return ctx
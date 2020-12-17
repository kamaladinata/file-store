# import re
# import base64

from bs4 import BeautifulSoup
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)
class MailChannel(models.Model):
    _inherit = 'mail.channel'

    # opportunity experiment
    def _define_command_opportunity(self):
        return {'help': _("Create a new Opportunity (/opportunity opportunity_title)")}
    
    def _execute_command_opportunity(self, **kwargs):
        partner = self.env.user.partner_id
        user = self.env.user
        members = [p.id for p in self.channel_partner_ids[:30] if p != partner]
        msg = "Something is wrong!, please try again later"
        if len(members) == 0:
            msg = _("You are alone in this channel or other user are currently offline.")
            self._send_transient_message(partner, msg)
        elif len(members) == 1:
            crm_obj = self.env['crm.lead']
            partner_id = self.env['res.partner'].browse(members)
            
            raw_name = kwargs['body'].split(' ')
            name = ' '.join(raw_name[1:len(raw_name)])
            name = partner_id.name +' - '+ name

            #chat history
            chat = ""
            for message_id in self.channel_message_ids.sorted(key=lambda msg:msg.id):
                try:
                    raw_body = BeautifulSoup(message_id.body)
                    body = raw_body.get_text()
                    chat = "%s : %s"%(message_id.author_id.name,body) if not chat else "%s\n\n%s : %s"%(chat,message_id.author_id.name,body)
                except:
                    chat = "%s : Incomprehensible[%s]"%(message_id.author_id.name,message_id.id) if not chat else "%s\n\n%s : Incomprehensible[%s]"%(chat,message_id.author_id.name,message_id.id)

            vals = {
                'name' : name,
                'partner_id' : partner_id.id,
                'partner_name' : partner_id.name if partner_id.company_type == 'company' else '',
                'street' : partner_id.street,
                'street2' : partner_id.street2,
                'city' : partner_id.city,
                'state_id' : partner_id.state_id.id,
                'zip' : partner_id.zip,
                'country_id' : partner_id.country_id.id,
                'website' : partner_id.website,
                'user_id' : user.id,
                'team_id' : user.sale_team_id.id,
                'email_from' : partner_id.email,
                'phone' : partner_id.phone,
                'mobile' : partner_id.mobile,
                'description' : chat
            }
            try:
                oppor_id = crm_obj.create(vals)
                oppor_id.convert_opportunity(partner_id.id, [], False)
                oppor_id.allocate_salesman(user.ids, team_id=user.sale_team_id.id)
                link = "/web?#id=%s&model=crm.lead&view_type=form"%(oppor_id.id)
                msg = _("An Opportunity <a href='%s'>%s</a> has been created for this inquiry."%(link,name))
                self.message_post(
                    body=msg,
                    message_type='comment',
                    subtype='mail.mt_comment'
                )
            except ValueError as e:
                # sumtingwong
                _logger.exception(e)
        else:
            msg = _("You need to use this command in direct message.")
            self._send_transient_message(partner, msg)

       
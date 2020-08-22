# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintellecs.com>).
#
##############################################################################

# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
# from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
from openerp.exceptions import UserError


class invoice_mass(models.TransientModel):
    _name = "mass.mail.invoice"
    _inherit = ['mail.thread']

    @api.model
    def _get_template_id(self):
        temp_id = self.env['mail.template'].search([('name', '=', 'Invoice - Send by Email')])
        if temp_id:
            return temp_id[0]
        return

    template_id = fields.Many2one('mail.template', string="Usa template", default=_get_template_id, required=True,
                                  select=True)

    def send_button(self):
        invoice_ids = self.env.context.get('active_ids')
        invoices = self.env['account.move'].browse(invoice_ids)
        invoices_not_draft = invoices.filtered(lambda r: r.state != "draft")
        partners = invoices_not_draft.mapped('partner_id')
        for partner in partners:
            if not partner.notify_email == 'always':
                raise UserError("For the customer " + str(
                    partner.name) + "the email is not configured .Specify an email and try again")
        for invoice_not_draft in invoices_not_draft:
            notify_email = invoice_not_draft.partner_id.notify_email
            if notify_email == 'always':
                if self.template_id.id:
                    mtp = self.env['mail.template'].browse(self.template_id.id)
                    mtp.send_mail(invoice_not_draft.id, force_send=True)
        return True

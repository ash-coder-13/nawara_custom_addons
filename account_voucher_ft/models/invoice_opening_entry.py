# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import UserError
READONLY_STATES = {
        'proforma': [('readonly', True)],
        'proforma2': [('readonly', True)],
        'open': [('readonly', True)],
        'paid': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self):
        invoice = self._context.get('invoice', False)
        self._post_validate()
        for move in self:
            move.line_ids.create_analytic_lines()
            if move.name == '/':
                new_name = False
                journal = move.journal_id
                if invoice and invoice.opening_entry:
                    move.name = invoice.inv_name
                    # move.opening_entry = True
                else:
                    if invoice and invoice.move_name and invoice.move_name != '/':
                        new_name = invoice.move_name
                    else:
                        if journal.sequence_id:
                            # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                            sequence = journal.sequence_id
                            if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                                if not journal.refund_sequence_id:
                                    raise UserError(_('Please define a sequence for the refunds'))
                                sequence = journal.refund_sequence_id
                            new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                        else:
                            raise UserError(_('Please define a sequence on the journal.'))
                if new_name:
                    # company_prefix_code = self.env['res.users'].browse(self._uid).company_id.company_prefix_code
                    # if not company_prefix_code:
                    #     raise UserError(_("Please select a prefix code  in company form"))
                    # move.name = company_prefix_code + new_name
                    move.name =  new_name
        return self.write({'state': 'posted'})



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    _description = "Account Invoice"

    inv_name = fields.Char('Invoice No', states=READONLY_STATES )
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, index=True, ondelete='restrict',
                              copy=False, help="Link to the automatically generated Journal Items.")
    opening_entry = fields.Boolean('Opening Entry', default=False, states=READONLY_STATES )
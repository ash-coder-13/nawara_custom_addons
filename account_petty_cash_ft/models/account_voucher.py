from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError, RedirectWarning


PC_TYPE = [
    ('normal', 'Normal'),
    ('allocation', 'Allocation'),
    ('topup', 'TopUp')
]


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    petty_cash_fund = fields.Many2one('pettycash.fund')
    voucher_type = fields.Selection(selection_add=[
        ('pettycash', 'Petty Cash')
    ])
    pc_voucher_type = fields.Selection(PC_TYPE, default='normal', string='Voucher Type')
    attachments = fields.Many2many('ir.attachment', string='Add Reference Files')

    @api.onchange('amount', 'line_ids')
    def onchange_amunt(self):
        if self.petty_cash_fund:
            if (self.petty_cash_fund.balance - self.amount) < 0:
                raise ValidationError("Pls TopUp to add extra line")

    @api.model
    def create(self, vals):

        if vals['voucher_type'] == 'pettycash':
            if not vals.get('account_id'):
                pf = self.petty_cash_fund.browse(vals.get('petty_cash_fund'))
                vals.update(journal_id=pf.journal.id, account_id=pf.custodian_account.id)
            if vals['pc_voucher_type'] == 'normal' and not 'number' in vals:
                vals.update(number=self.env['ir.sequence'].next_by_code('voucher.pettycash'))

        return super(AccountVoucher, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.voucher_type == 'pettycash':
            super(AccountVoucher, self).onchange_partner_id()

    def first_move_line_get(self, move_id, company_currency, current_currency):
        res = super(AccountVoucher, self).first_move_line_get(move_id, company_currency, current_currency)
#        credit = 0.0
        if self.voucher_type == 'pettycash':
            credit = self._convert_amount(self.amount)
            sign = res.get('debit', 0.0) - credit < 0 and -1 or 1
            # set the first line of the voucher
            res.update({
                'credit': credit,
                'amount_currency': (sign * abs(self.amount)  # amount < 0 for refunds
                                    if company_currency != current_currency else 0.0),
            })
        return res

    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        if self.voucher_type == 'pettycash':
            line_total = line_total - self._convert_amount(self.tax_amount)
            self = self.with_context(is_pettycash=True)
        for line in self.line_ids:
            # create one move line per voucher line where amount is not 0.0
            if not line.price_subtotal:
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context,
            # so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(line.price_unit * line.quantity)
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': self.partner_id.id,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                'debit': abs(amount) if self.voucher_type in ['purchase', 'pettycash'] else 0.0,
                'date': self.account_date,
                'tax_ids': [(4, t.id) for t in line.tax_ids],
                'amount_currency': line.price_subtotal if current_currency != company_currency else 0.0,
                'currency_id': company_currency != current_currency and current_currency or False,
            }

            self.env['account.move.line'].with_context(apply_taxes=True).create(move_line)
        return line_total

    def print_voucher_ft(self):
        return self.env.ref('account_voucher_ft.report_voucher').report_action(self, data=None)

        # return self.env['report'].get_action(self, 'account_voucher_ft.report_voucher')

    @api.model
    def default_get(self,fields):
        res=super(AccountVoucher,self).default_get(fields)
        if self._context.get('active_id') and self._context.get('from_petty_cash'):
            petty_cash_fund=self.env['pettycash.fund'].browse(self._context.get('active_id'))
            payment_method_id=petty_cash_fund.get_payment_method()
            res.update({'payment_method_id':payment_method_id.id})
        return res
#            
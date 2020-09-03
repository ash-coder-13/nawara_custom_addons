from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

PAYMENT_METHODS = [
    ('cash', 'Cash or Bank'),
    ('payable', 'Payable')
]
PAYMENT_MODES = [
    ('manual', 'Manual'),
    ('cheque', 'Cheque')
]


class CreateFund(models.TransientModel):

    _name = 'pettycash.fund.create'
    _description = 'Petty Cash Fund Allocation Wizard'

    def _get_account_domain(self):
        return [('user_type_id.id', '=', self.env.ref('account.data_account_type_current_assets').id)]

    fund_name = fields.Char(required=True)
    fund_amount = fields.Float(
        digits=dp.get_precision('Product Price'), required=True)
    custodian = fields.Many2one('res.users', required=True)
    payment_method = fields.Selection(PAYMENT_METHODS, string='Payment Method', default='cash',
                                      required=True)
    payment_mode = fields.Selection(PAYMENT_MODES, default='manual')
    cheque_number = fields.Char('Cheque Number')
    custodian_account = fields.Many2one('account.account', string='Custodian Account', required=True,
                                        domain=_get_account_domain)
    payment_account = fields.Many2one('account.account', required=True, string='Payment Account',
                                      domain=[('internal_type', 'in', ['liquidity', 'payable'])])
    effective_date = fields.Date(required=True, default=fields.Date.today())

    def create_fund(self):
        if self.fund_amount <= 0.0:
            raise UserError('Fund Amount should be non-zero.')
        petty_cash_fund_o = self.env['pettycash.fund']
        fund = petty_cash_fund_o.with_context(default_pc_voucher_type='allocation').create_fund(self)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',

            'res_model': 'pettycash.fund',
            'res_id': fund.id
        }

    @api.onchange('custodian')
    def on_change_values(self):
        res = {}
        if self.custodian:
            res.update(fund_name='Petty Cash - ' + self.custodian.name)
        return {'value': res}

    @api.onchange('payment_method')
    def onchange_payment_method(self):
        if not self.payment_method:
            return
        domain = {}
        value = {}
        if self.payment_method == 'cash':
            dom = [('internal_type', '=', 'liquidity')]
            value.update(payment_account=self.payment_account.search(dom, limit=1))
            domain.update(payment_account=dom)
        if self.payment_method == 'payable':
            dom = [('internal_type', '=', 'payable')]
            value.update(payment_account=self.payment_account.search(dom, limit=1))
            domain.update(payment_account=dom)
        return {'value': value, 'domain': domain}

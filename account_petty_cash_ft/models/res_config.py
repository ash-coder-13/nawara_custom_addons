from odoo import api, fields, models


class ResConfig(models.TransientModel):
    _name = 'petty_cash.config.settings'
    _inherit = 'res.config.settings'

    default_payable_account = fields.Many2one('account.account', domain=[('internal_type', '=', 'payable')],
                                              string='Default Petty Cash Payable Account')

    def set_payable_account(self):
        ir_values_obj = self.env['ir.values']
        if self.default_payable_account:
            ir_values_obj.sudo().set_default('pettycash.fund.create', "payable_account", self.default_payable_account.id)

    @api.model
    def get_default_payable_account(self, fields_list):
        res = {}
        ir_values_obj = self.env['ir.values']
        if 'default_payable_account' in fields_list:
            value = ir_values_obj.sudo().get_default('pettycash.fund.create', "payable_account")
            if value:
                res.update(default_payable_account=value)
        return res
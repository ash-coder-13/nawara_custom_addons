from odoo import api, fields, models


class IssueVoucherWizard(models.TransientModel):

    _name = 'pettycash.fund.reconcile'
    _desc = 'Petty Cash Fund Reconciliation Wizard'

    fund = fields.Many2one('pettycash.fund', required=True)
    date = fields.Date(required=True, default=fields.Date.today())

    def reconcile_vouchers(self):
        return

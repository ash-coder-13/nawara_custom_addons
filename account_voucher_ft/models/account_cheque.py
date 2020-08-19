from odoo import api, fields, models


class ChequeRegister(models.Model):
    _inherit = 'cheque.register'

    voucher_id = fields.Many2one('account.voucher', 'For Voucher', readonly=True)
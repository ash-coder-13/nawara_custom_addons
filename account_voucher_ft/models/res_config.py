from odoo import models, fields


class AccountVoucherConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    group_voucher_product_based = fields.Boolean(string='Product Based Voucher Lines',
                                                 implied_group='account_voucher_ft.group_voucher_product_based',
                                                 help="Allows you to create Voucher Line with Products.")

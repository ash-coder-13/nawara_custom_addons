from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    pettycash_id = fields.Many2one('pettycash.fund', string='PettyCash Fund', readonly=True)
    partner_type = fields.Selection(selection_add=[('custodian', 'Custodian')])

    @api.depends('partner_type')
    def onchange_partner_type(self):
        if self.partner_type == 'custodian' and not self.pettycash_id:
            raise UserError('Sorry You cannot create a Custodian Payment directly')

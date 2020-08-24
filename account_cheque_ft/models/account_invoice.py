from odoo import models,fields,api

class AccountMove(models.Model):
    _inherit='account.move'
    
    # @api.depends('payment_ids')
    # def get_pdc_amt(self):
    #     for rec in self:
    #         rec.pdc_amount=sum([payment.amount for payment in rec.payment_ids.filtered(lambda payment:payment.state=='on_pdc')])
    #         if rec.pdc_amount==rec.residual and rec.payment_ids:
    #             rec.reg_payment=True
    #         else:
    #             rec.reg_payment=False
    
    pdc_amount=fields.Float(string='PDC Amount')
    reg_payment=fields.Boolean(string='Register Payments')
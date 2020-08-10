from odoo import models,fields,api

class AccountMove(models.Model):
    _inherit='account.move'
    
    # @api.one
    # @api.depends('payment_ids')
    # def get_pdc_amt(self):
    #     self.pdc_amount=sum([payment.amount for payment in self.payment_ids.filtered(lambda payment:payment.state=='on_pdc')])
    #     if self.pdc_amount==self.residual and self.payment_ids:
    #         self.reg_payment=True
    #     else:
    #         self.reg_payment=False

    def get_pdc_amt(self):
        self.reg_payment = True
        self.pdc_amount = 0



    # @api.one
    # @api.depends('')
    #
    # payment_ids = fields.Many2many('account.payment', string="Payments", copy=False, readonly=True,compute='_compute_payment_lines')
    #
    pdc_amount=fields.Float(string='PDC Amount',compute='get_pdc_amt')
    reg_payment=fields.Boolean(string='Register Payments',compute='get_pdc_amt')
# -*- coding: utf-8 -*-
from odoo import models, fields


class CustomBank(models.Model):
    _inherit = 'res.bank'
    _description = 'Custom Bank'

    bank_code = fields.Char(string='Bank Code')
    iban_code = fields.Char(string='IBAN Code')
    mob_num = fields.Char(string='Mobile Number')
    website = fields.Char(string="Website")
    cont_person = fields.Many2one('res.partner', string='Contact person')

    cheque_print_id = fields.Many2one('ir.actions.report.xml', 'Cheque Print Format',
                                      domain=[('model', '=', 'res.bank')])

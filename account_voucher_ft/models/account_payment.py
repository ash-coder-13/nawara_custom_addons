# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import math

from odoo import models, fields, api, _
from odoo.tools import  float_round


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    def set_amt_in_words(self):
        amount, currency = self.amount, self.currency_id.name
        amount_in_words = self.currency_id.amount_to_text(amount, lang='en', currency=currency)
        if currency == 'AED':
            amount_in_words = str(amount_in_words).replace('AED', 'Dhirham')
            amount_in_words = str(amount_in_words).replace('Cents', 'fils')
            amount_in_words = str(amount_in_words).replace('Cent', 'fil')
        amount_in_words += '\tonly'
        self.amt_in_words = amount_in_words.capitalize()

    amt_in_words = fields.Char(compute='set_amt_in_words')
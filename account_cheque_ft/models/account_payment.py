# -*- coding: utf-8 -*-
import math
from lxml import etree
from odoo import models, fields, api, _
from odoo.tools import amount_to_text_en, float_round
from odoo.exceptions import UserError, ValidationError
PAY_METH_CODES = [
    'cheque_payment',
    'cheque_receipt',
    'cheque_pdc_payment',
    'cheque_pdc_receipt'
]


class account_payment_method(models.Model):
    _inherit = "account.payment.method"

    payment_method_type = fields.Selection([('normal', 'Normal'), ('delayed', 'Delayed')], default='normal')


class AccountPayment(models.Model):
    _inherit = "account.payment"

    cheque_id = fields.Many2one('cheque.register', 'Cheque No.', domain="[('state', '=', 'blank'), ('acc_num','=', journal_id)]", 
                                ondelete='restrict')
    amount_in_words = fields.Char('Amount in Words', readonly=True)
    state = fields.Selection(selection_add=[('on_pdc', 'On PDC')])

    category_cheque_pdc_id = fields.Many2one('cheque.category.cheques', 'Post Dated Cheque', readonly=True)
    mature_date = fields.Date('Cheque Maturing Date')
    
    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
            """
                Add domain 'allow_check_writting = True' on journal_id field and remove 'widget = selection' on the same
                field because the dynamic domain is not allowed on such widget
            """
            res = super(AccountPayment, self).fields_view_get(view_id=view_id, view_type=view_type,toolbar=toolbar, submenu=submenu)
            doc = etree.XML(res['arch'])
            if self._context.has_key('from_cheque') :
                nodes = doc.xpath("//field[@name='payment_method_id']")
                for node in nodes:
                    node.set('domain',str([('id', 'in', self._context.get('payment_method_id'))]) )
                res['arch'] = etree.tostring(doc)
            return res
        
    # to subtract pdc amount
    @api.model
    def default_get(self,fields):
        res=super(AccountPayment,self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_model=='account.move':
            invoice = self.env[active_model].browse(active_id)
            if invoice.pdc_amount:
                amount=res.get('amount')
                res.update({'amount':amount-invoice.pdc_amount})
        return res

    # to subtract pdc amount
    def _compute_total_invoices_amount(self):
        """ Compute the sum of the residual of invoices, expressed in the payment currency """
        payment_currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or self.env.user.company_id.currency_id
        invoices = self.reconciled_invoice_ids

        if all(inv.currency_id == payment_currency for inv in invoices):
            total = sum(invoices.mapped('amount_residual_signed'))-sum(invoices.mapped('pdc_amount'))
        else:
            total = 0
            for inv in invoices:
                if inv.company_currency_id != payment_currency:
                    total += inv.company_currency_id.with_context(date=self.payment_date).compute(inv.amount_residual_signed, payment_currency)
                    total -= inv.company_currency_id.with_context(date=self.payment_date).compute(inv.pdc_amount, payment_currency)
                else:
                    total += inv.residual_company_signed-inv.pdc_amount
        return abs(total)
    @api.multi
    def write(self, vals):
        if 'payment_method_id' in vals and self.payment_method_code in PAY_METH_CODES and self.cheque_id:
            raise UserError('Sorry You Cannot change Payment Method of this Payment,'
                            ' Because you already create a Cheque.')
        else:
            return super(AccountPayment, self).write(vals)

    @api.multi
    def create_category_cheque(self):
        category_cheque_o = self.env['cheque.category.cheques']
        return category_cheque_o.create({
            'payment_id': self.id,
            'category_id': 'pdc',
            'partner_id': self.partner_id.id,
            'reg_date': self.payment_date,
            'mature_date': self.mature_date,
            'cheque_amount': self.amount,
            'memo': self.communication,
            'cheque_id': self.cheque_id.id,
            'cheque_type': 'company' if self.payment_method_code == 'cheque_pdc_payment' else 'partner'
        })

    @api.multi
    def process_pdc_method(self):
        category_cheque_pdc_id = self.create_category_cheque()
        category_cheque_pdc_id.action_validate()
        self.update({
            'state': 'on_pdc',
            'category_cheque_pdc_id': category_cheque_pdc_id,
            'name': 'PIN.%s' % category_cheque_pdc_id.name if self.payment_method_code == 'cheque_pdc_payment' else 'POUT.%s' % category_cheque_pdc_id.name
        })

    @api.multi
    def post_pdc(self):
        self.state = 'draft'
        return super(AccountPayment, self).post()

    @api.multi
    def post(self):
        if not self.cheque_id and self.payment_method_code in PAY_METH_CODES:
            raise UserError('Without a Cheque Entry, You cannot validate this Payment')
        if self.cheque_id:
            if self.payment_method_code == 'cheque_pdc_payment':
                self.cheque_id.write(
                {'issue_date':self.payment_date,'cheque_date':self.mature_date,
                'amount':self.amount,'payment_id':self.id,'payee_name':self.company_id.partner_id.id}
                )
            self.cheque_id.action_validate()
        if self.payment_method_code in ['cheque_pdc_payment', 'cheque_pdc_receipt']:
            return self.process_pdc_method()
        res = super(AccountPayment, self).post()
        return res

    @api.multi
    def unlink(self):
        for record in self:
            cheque_id = record.cheque_id
            super(AccountPayment, record).unlink()
            if cheque_id:
                cheque_id.cancel_cheque(unlink=True)
        return True

# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError, RedirectWarning
BLANK_REQUIRED = {'blank': [('required', True), ('readonly', False)]}
DRAFT_EDITABLE = {'draft': [('readonly', False), ('required', True)]}
VALID_EDITABLE = {'blank': [('required', True), ('readonly', False)],'valid': [('readonly', False), ('required', True)]}


class ChequeRegister(models.Model):
    _name = 'cheque.register'
    _description = 'Cheque Register'
    _rec_name = 'cheque_no'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('blank', 'Blank'),
        ('valid', 'Valid'),
        ('on_pdc', 'On PDC'),
        ('processed', 'Processed'),
        ('cancel', 'Cancelled')
    ], default='draft')
    currency_id = fields.Many2one('res.currency', default=lambda s: s.env.user.company_id.currency_id.id)
    sl_no = fields.Char(string='Sl.No', readonly=True)
    acc_num = fields.Many2one('account.journal', string='Account Number', domain=[('type', '=', 'bank')],
                              readonly=True, states=DRAFT_EDITABLE)
    acc_num_out = fields.Char('Account Number')
    bank_name = fields.Many2one('res.bank', string='Bank Name', readonly=True, states=DRAFT_EDITABLE)
    bank_name_out = fields.Char('Bank Name')
    cheque_type = fields.Selection([('company', 'Company'), ('partner', 'Partner')], default='company',
                                   readonly=True)
    cheque_no = fields.Char(string='Cheque Number')

    amount = fields.Monetary(string='Amount', readonly=True, states=BLANK_REQUIRED)
    payee_name = fields.Many2one('res.partner', string='Payee', readonly=True, states=BLANK_REQUIRED)
    issue_date = fields.Date(string='Issue Date', readonly=True, states=BLANK_REQUIRED)
    cheque_date = fields.Date(string='Cheque Date',readonly=True,states=VALID_EDITABLE)

    category_id = fields.Selection([
        ('pdc', 'Post-Dated Cheque'),
        ('bgc', 'Bank Guarantee Cheque'),
        ('sc', 'Security Cheque')], 'Cheque Category', readonly=True)

    cheque_book_id = fields.Many2one('cheque.book', 'Cheque Book', readonly=True)

    cheque_ref = fields.Char('Cheque Reference')
    description = fields.Text('Description')

    payment_id = fields.Many2one('account.payment', 'For Payment', readonly=True)

    @api.model
    def create(self, vals):
        vals.update({
            'sl_no': self.env['ir.sequence'].next_by_code('cheque_sl_no'),
            'state': 'blank'
        })
        if not vals.get('acc_num_out') and vals.get('acc_num'):
            vals.update(acc_num_out=self.env['account.journal'].browse(vals.get('acc_num')).bank_acc_number)
        return super(ChequeRegister, self).create(vals)

    def write(self,vals):
        res=super(ChequeRegister,self).write(vals)
        for cheque in self:
            if vals.get('cheque_date') and cheque.payment_id and cheque.payment_id.mature_date:
                if cheque.payment_id:
                    cheque.payment_id.write({'mature_date':vals.get('cheque_date')})
                if cheque.payment_id.category_cheque_pdc_id:
                    cheque.payment_id.category_cheque_pdc_id.write({'mature_date':vals.get('cheque_date')})
        return res
    
    @api.onchange('acc_num')
    def onchange_acc_number(self):
        if self.acc_num:
            self.bank_name = self.acc_num.bank_id
            

    def action_validate(self):
        self.state = 'valid'


    def processed(self):
        for cheque in self:
            cheque.state = 'processed'
            if cheque.payment_id and cheque.payment_id.category_cheque_pdc_id:
                pdc_cheque=cheque.payment_id.category_cheque_pdc_id
                today = fields.Date.today()
                if pdc_cheque.state=='valid' and pdc_cheque.mature_date <= today:
                    pdc_cheque.state = 'matured'


    def create_and_link_cheque_id(self):
        active_model = self.env[self.env.context.get('active_model')]
        active_rec = active_model.browse(self.env.context.get('active_id'))
        active_rec.cheque_id = self.id
        if self._context.has_key('from_inv'):
            view = self.env.ref('account.view_account_payment_invoice_form')
            payment_methods = active_rec.payment_type == 'inbound' and active_rec.journal_id.inbound_payment_method_ids or active_rec.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            context={
                'active_model': self.env.context.get('active_model'),
                'active_ids':self.env.context.get('active_ids'),
                'active_id':self.env.context.get('active_id'),
                'default_journal_id':active_rec.journal_id.id,
                'from_cheque':True,
                'payment_method_id':payment_methods.ids,
            }
            return{
                'name': _('Enter transfer details'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': self.env.context.get('active_id'),
                'context': context,
                }
        return True


    def cancel_cheque(self, unlink=False):
        self.state = 'cancel'
        if unlink:
            self.unlink()
    

    def button_cheque_reg_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in', self.payment_id.ids)],
        }


EDIT_ON_DRAFT = {'draft': [('readonly', False)]}


class ChequeBook(models.Model):
    _name = 'cheque.book'
    _description = 'Cheque Books'
    _rec_name = 'cheque_book_ref'

    cheque_book_ref = fields.Char('Cheque Book Reference', required=True)
    acc_num = fields.Many2one('account.journal', string='Account Number', domain=[('type', '=', 'bank')],
                              required=True)
    bank_name = fields.Many2one('res.bank', string='Name of Bank', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('registered', 'Registered'),
        ('cancel', 'Cancelled')
    ], default='draft')
    cheque_no_from = fields.Char(string='From', required=True, readonly=True, states=EDIT_ON_DRAFT)
    cheque_no_to = fields.Char(string='Upto', required=True, readonly=True, states=EDIT_ON_DRAFT)

    cheque_ids = fields.One2many('cheque.register', 'cheque_book_id', 'Cheques')

    @api.onchange('cheque_no_from')
    def onchange_cheque_no_from(self):
        self.cheque_no_to = self.cheque_no_from


    @api.onchange('acc_num')
    def onchange_acc_number(self):
        if self.acc_num:
            self.bank_name = self.acc_num.bank_id

    @api.constrains('cheque_no_from', 'cheque_no_to')
    def cheque_book_sequence_constrain(self):
        if self.cheque_no_from and self.cheque_no_to and self.cheque_no_from > self.cheque_no_to:
            raise UserError('Please check the Cheque Numbers Series you entered.')
        return True


    def validate(self):
        if self.cheque_no_from and self.cheque_no_to and self.cheque_book_sequence_constrain():
            self.state = 'validated'
        else:
            raise ValidationError('Cheque Sl.No:Start No/End No Not Found')


    def register_cheques(self):
        for i in range(int(self.cheque_no_from), int(self.cheque_no_to) + 1):
            cheques = self.cheque_ids.create({
                'acc_num': self.acc_num.id,
                'acc_num_out': self.acc_num.name,
                'bank_name': self.bank_name.id,
                'bank_name_out': self.bank_name.name,
                'cheque_no': str(i).zfill(len(self.cheque_no_from)),
                'cheque_book_id': self.id
            })
        self.state = 'registered'
        return cheques


    def cancel_cheques(self):
        if self.cheque_ids:
            self.cheque_ids.cancel()
        self.state = 'cancel'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id
        }


    def cancel(self):
        if self.state == 'registered' and self.cheque_ids:
            action_id = self.env.ref('account_cheque_ft.action_server_cancel_cheques').id
            action = '%s&active_id=%s' % (action_id, self.id)
            raise RedirectWarning('Are you sure want cancel this Cheque Book and its related'
                                  'Cheque Leafs ?', action, 'Confirm and Continue')
        else:
            self.state = 'cancel'





# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, api,fields,_
from odoo.exceptions import UserError


class CategoryCheques(models.Model):
    _name = 'cheque.category.cheques'
    _inherit = ['ir.needaction_mixin']

    name = fields.Char('Name', readonly=True)
    category_id = fields.Selection([
        ('pdc', 'Post-Dated Cheque'),
        ('bgc', 'Bank Guarantee Cheque'),
        ('sc', 'Security Cheque')], 'Cheque Category', readonly=True)
    currency_id = fields.Many2one('res.currency', default=lambda s: s.env.user.company_id.currency_id.id)
    partner_id = fields.Many2one('res.partner', string="Partner", required=True,
                                 readonly=True, states={'draft': [('readonly', False)]})
    reg_date = fields.Date('Register Date', default=datetime.today(), readonly=True,
                           states={'draft': [('readonly', False)]})
    mature_date = fields.Date('Cheque Date/Mature Date', required=True, readonly=True,
                              states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('valid', 'Validated'),
        ('matured', 'Matured'),
        ('processed', 'Processed'),
        ('cancel', 'Cancelled')], default='draft', string="Status")
    cheque_amount = fields.Monetary('Cheque Amount', required=True)
    memo = fields.Char('Memo', readonly=True, states={'draft': [('readonly', False)]})

    cheque_id = fields.Many2one('cheque.register', string='Cheque', readonly=True,
                                states={'draft': [('readonly', False)]}, ondelete='restrict')
    cheque_no = fields.Char('Cheque Number', readonly=True, related='cheque_id.cheque_no')
    cheque_ref = fields.Char('Cheque Reference', readonly=True, related='cheque_id.cheque_ref')
    description = fields.Text('Description', readonly=True, related='cheque_id.description')

    bank_name = fields.Many2one('res.bank', string='Bank Name', readonly=True, related='cheque_id.bank_name', store=True)
    bank_name_out = fields.Char('Bank Name', related='cheque_id.bank_name_out', store=True, readonly=True)

    acc_num = fields.Many2one('account.journal', string='Account Number', domain=[('type', '=', 'bank')],
                              readonly=True, related='cheque_id.acc_num', store=True)
    acc_num_out = fields.Char('Account Number', related='cheque_id.acc_num_out', store=True, readonly=True)

    cheque_type = fields.Selection([('company', 'Issue'), ('partner', 'Receive')], default='company',
                                   readonly=True)

    project_id = fields.Many2one('project.project', string="Project", readonly=True,
                                 states={'draft': [('readonly', False)]})
    analytic_account = fields.Many2one('account.analytic.account', string='Analytic Account',
                                       readonly=True, states={'draft': [('readonly', False)]})
    payment_id = fields.Many2one('account.payment', 'Related Payment', readonly=True)

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            vals.update(name=self.env['ir.sequence'].next_by_code('cheque.pdc'))
        return super(CategoryCheques, self).create(vals)

    @api.onchange('cheque_id')
    def onchange_cheque(self):
        if self.cheque_id:
            vals = {'cheque_no': self.cheque_id.cheque_no}
            if self.cheque_type == 'company':
                vals.update({
                    'bank_name': self.cheque_id.bank_name,
                    'acc_num': self.cheque_id.acc_num
                })
            if self.cheque_type == 'partner':
                vals.update({
                    'bank_name_out': self.cheque_id.bank_name_out,
                    'acc_num_out': self.cheque_id.acc_num_out
                })
            return {'value': vals}

    @api.multi
    def unlink(self):
        for record in self:
            cheque_id = record.cheque_id
            super(CategoryCheques, record).unlink()
            if cheque_id:
                cheque_id.cancel_cheque(unlink=True)
        return True

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'matured')]

    @api.multi
    def action_validate(self):
        if not self.cheque_id:
            raise UserError('Please Create a Cheque before Validating.')
        self.cheque_id.action_validate()
        if self.mature_date > fields.Date.today():
            self.state = 'valid'
        else:
            self.state = 'matured'

    @api.multi
    def action_process(self):
        if self.payment_id:
            self.payment_id.post_pdc()
        self.cheque_id.state = 'processed'
        self.state = 'processed'

    @api.model
    def maturity_check(self, cron_mode=True):
        today = fields.Date.today()
        for record in self.search([('state', 'in', 'valid')]):
            if record.mature_date <= today:
                record.state = 'matured'

    @api.multi
    def button_cheque_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in', self.payment_id.ids)],
        }


import datetime
from odoo import api, exceptions, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare,amount_to_text_en
from odoo.exceptions import ValidationError
PETTYCASH_STATE = [
    ('draft', 'Draft'),
    ('open', 'Open'),
    ('reconcile', 'On Reconcile Approval'),
    ('topup', 'On Topup Approval'),
    ('closed', 'Closed'),
]
PAYMENT_METHODS = [
    ('cash', 'Cash or Bank'),
    ('payable', 'Payable')
]
PAYMENT_MODES = [
    ('manual', 'Cash on Hand'),
    ('cheque', 'Cheque')
]
VOUCHER_SEQ_TYPE = {
    'normal': 'voucher.pettycash',
    'allocation': 'voucher.pettycash.allocation',
    'topup': 'voucher.pettycash.topup'
}
DRAFT_EDITONLY = {'draft': [('readonly', False)]}


class PettyCash(models.Model):

    _name = 'pettycash.fund'
    _description = 'Petty Cash Fund'
    
    def set_amt_in_words(self):
        amount, currency = self.amount, self.currency_id.name
        amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency=currency)
        if currency == 'AED':
            amount_in_words = str(amount_in_words).replace('AED', 'Dhirham')
            amount_in_words = str(amount_in_words).replace('Cents', 'fils')
            amount_in_words = str(amount_in_words).replace('Cent', 'fil')
        amount_in_words += '\tonly'
        self.amt_in_words = amount_in_words.capitalize()

    amt_in_words = fields.Char(compute='set_amt_in_words')
    code = fields.Char('Fund Code', readonly=True)
    name = fields.Char(required=True, readonly=True, states=DRAFT_EDITONLY)
    custodian = fields.Many2one('hr.employee', required=True, readonly=True,
                                states=DRAFT_EDITONLY)
    custodian_partner = fields.Many2one('res.partner', related='custodian.address_id', readonly=True)
    journal = fields.Many2one('account.journal', readonly=True)
    amount = fields.Float(string='Fund Amount', readonly=True, digits=dp.get_precision('Product Price'),
                          states={'draft': [('readonly', False)], 'topup':[('readonly', False)]}, store=True)
    balance = fields.Float(string='Balance', compute='_valid_balance', readonly=True, store=True,
                           digits=dp.get_precision('Product Price'), states={'draft': [('invisible', True)]})
    state = fields.Selection(selection=PETTYCASH_STATE, default='draft')
    effective_date = fields.Date('Allocation Date', readonly=True, states=DRAFT_EDITONLY, required=True)
    custodian_account = fields.Many2one('account.account', states=DRAFT_EDITONLY, required=True)
    payment_account = fields.Many2one('account.account', states=DRAFT_EDITONLY, required=True)
    payment_method = fields.Selection(PAYMENT_METHODS, string='Payment Method', default='cash',
                                      states=DRAFT_EDITONLY, required=True)
    payment_mode = fields.Selection(PAYMENT_MODES, default='manual', states=DRAFT_EDITONLY, required=True)
    cheque_number = fields.Many2one('cheque.register', 'Cheque Number', states=DRAFT_EDITONLY,
                                    domain=[('state', '=', 'blank')])
    active = fields.Boolean(default=True)
    company = fields.Many2one('res.company', default=lambda s: s.env.user.company_id)
    vouchers = fields.One2many('account.voucher', 'petty_cash_fund', states={'open': [('readonly', False)]},
                               domain=[('state', 'not in', ['cancel', 'posted'])], readonly=True)
    vouchers_history = fields.One2many('account.voucher', 'petty_cash_fund',
                                       domain=[('state', 'in', ['cancel', 'posted'])])
    journal_entries = fields.Many2many('account.move', readonly=True)
    currency_id = fields.Many2one('res.currency', default=lambda s: s.env.user.company_id.currency_id)

    @api.onchange('custodian')
    def on_change_values(self):
        res = {}
        if self.custodian:
            res.update(name='Petty Cash - ' + self.custodian.name)
        return {'value': res}

    @api.onchange('payment_method')
    def onchange_payment_method(self):
        if self.payment_method == 'cash':
            journals = self.env['account.journal'].search([('type', 'in', ['cash', 'bank'])])
            payment_account_ids = journals.mapped('default_credit_account_id').ids
            return {'domain': {'payment_account': [('id', 'in', payment_account_ids)]}}
        if self.payment_method == 'payable':
            return {'domain': {'payment_account': [('internal_type', '=', 'payable')]}}

    @api.depends('vouchers.amount', 'vouchers_history', 'amount')
    def _valid_balance(self):
        for fund in self:
            amount = 0.0
            for voucher in fund.vouchers_history | fund.vouchers:
                if voucher.state == 'cancel':
                    continue
                if voucher.pc_voucher_type in ['allocation', 'topup']:
                    amount += voucher.amount
                else:
                    amount -= voucher.amount
            if amount < 0:
                raise ValidationError('Pls TopUp to add extra line')
            fund.balance = amount

    @api.model
    def validate_fund(self):
        seq_o = self.env['ir.sequence']
        fund_code = seq_o.next_by_code('petty.cash.fund')
        journal_seq = self.create_journal_sequence(fund_code)
        journal_o = self.create_journal(fund_code, journal_seq.id)
        fund = self.write({
            'code': fund_code,
            'journal': journal_o.id,
        })
        return fund

    @api.multi
    def validate_and_open(self):
        self.validate_fund()
        desc = _("Petty Cash Allocation(%s)" % self.code)
        voucher = self.create_pettycash_voucher(desc, allocation=True)
        voucher.action_move_line_create()
        self.update({
            'journal_entries': voucher.move_id,
            'state': 'open'
        })
        return True

    @api.multi
    def get_payment_method(self):
        today=datetime.datetime.today().date()
        payment_method=False
        if self.payment_method=='cash':
            if self.payment_mode=='manual':
                payment_method=self.env.ref('account.account_payment_method_manual_in')
            elif self.payment_mode=='cheque':
                allocation_date=datetime.datetime.strptime(self.effective_date,'%Y-%m-%d').date()
                if allocation_date>today:
                    payment_method=self.env.ref('account_cheque_ft.account_receipt_method_pdc')
                elif allocation_date==today:
                    payment_method=self.env.ref('account_cheque_ft.account_receipt_method_cheque')
                else:
                    raise ValidationError(_('You can not create a cheque of previous date!'))
        elif self.payment_method=='payable':
            payment_method=self.env.ref('account.account_payment_method_manual_out')
        return payment_method
        
    @api.multi
    def create_pettycash_voucher(self, desc, allocation=False):
        voucher_o = self.env['account.voucher']
        
        journal_vals={}
        payment_method=self.get_payment_method()
        if self.payment_method=='cash':
            journal_vals.update({'inbound_payement_method_ids':[(4,[payment_method.id])]})
        elif self.payment_method=='payable':
            journal_vals.update({'outbound_payement_method_ids':[(4,[payment_method.id])]})
       
        line = [(0, False, {
            'name': desc,
            'account_id': self.custodian_account.id,
            'price_unit': self.amount,
        })]
        voucher = voucher_o.create({
            'voucher_type': 'pettycash',
            'pc_voucher_type': 'allocation',
            'number': self.env['ir.sequence'].next_by_code('voucher.pettycash.allocation'),
            'name': desc if allocation else self.name,
            'date': self.effective_date,
            'journal_id': self.journal.id,
            'account_id': self.payment_account.id,
            'partner_id': self.custodian_partner.id,
            'line_ids': line,
            'petty_cash_fund': self.id,
            'amount': self.amount,
            'payment_method_id':payment_method.id,
            'cheque_id':self.cheque_number.id,
        })
        self.journal.write(journal_vals)
        return voucher

    @api.model
    def create_journal_sequence(self, fund_code):
        seq_o = self.env['ir.sequence']
        seq = seq_o.sudo().create({
            'name': self.name,
            'code': 'petty.cash.fund.'+fund_code,
            'prefix': fund_code + "%(y)s",
            'padding': 2,
        })
        return seq

    @api.model
    def create_journal(self,fund_code, journal_seq):
        journal_o = self.env['account.journal']
        journal = journal_o.create({
            'name': self.name,
            'code': fund_code,
            'type': 'pettycash',
            'default_credit_account_id': self.custodian_account.id,
            'default_debit_account_id': self.custodian_account.id,
            'sequence_id': journal_seq,
            'update_posted': True,
            'show_on_dashboard': False
        })
        return journal

    @api.multi
    def request_reconcile(self):
        self.state = 'reconcile'

    @api.multi
    def request_topup(self):
        self.state = 'topup'

    @api.multi
    def reconcile_fund(self):
        moves = []
        for voucher in self.vouchers:
            voucher.action_move_line_create()
            moves.append((4, voucher.move_id.id))
        self.journal_entries = moves
        self.state = 'open'

    @api.multi
    def topup_fund(self):
        moves = []
        desc = _("Petty Cash Topup(%s)" % self.code)
        payment_method=self.get_payment_method()
        line = [(0, False, {
            'name': desc,
            'account_id': self.custodian_account.id,
            'price_unit': self.amount,  # - self.balance,
        })]
        topup_voucher = self.vouchers.create({
            'voucher_type': 'pettycash',
            'pc_voucher_type': 'topup',
            'number': self.env['ir.sequence'].next_by_code('voucher.pettycash.topup'),
            'name': desc,
            'date': fields.Date.today(),
            'journal_id': self.journal.id,
            'account_id': self.payment_account.id,
            'partner_id': self.custodian_partner.id,
            'line_ids': line,
            'petty_cash_fund': self.id,
            'amount': self.amount,
            'payment_method_id':payment_method.id,
            'cheque_id':self.cheque_number.id,
        })
        topup_voucher.action_move_line_create()
        moves.append((4, topup_voucher.move_id.id))
        self.journal_entries = moves
        self.state = 'open'

    @api.multi
    def reconcile_and_refill(self):
        self.reconcile_fund()
        self.topup_fund()

    @api.multi
    def close_fund(self):
        if self.vouchers:
            self.reconcile_fund()
        self.state = 'closed'

    @api.multi
    def reopen_fund(self):
        self.topup_fund()
        self.state = 'open'

    @api.model
    def check_is_in_group(self, name, name_desc, action_desc):

        grp = self.env.ref(name)
        user_grp_ids = self.env.user.groups_id.ids
        if grp.id not in user_grp_ids:
            raise exceptions.AccessError(
                _("Only users in group %s may %s." % (name_desc, action_desc))
            )

    @api.multi
    def change_fund_amount(self, new_amount):

        # Only the Finance manager should be allowed to change the
        # amount of the fund.
        self.check_is_in_group('account.group_account_manager',
                               'Finance Manager',
                               _("change the amount of a petty cash fund"))

        for fund in self:
            # If this is a decrease in funds and there are unreconciled
            # vouchers do not allow the user to proceed.
            diff = float_compare(new_amount, fund.amount, precision_digits=2)
            if diff == -1 and fund.vouchers and len(fund.vouchers) > 0:
                raise exceptions.ValidationError(
                    _("Petty Cash fund (%s) has unreconciled vouchers" %
                      (fund.name))
                )
            fund.amount = new_amount



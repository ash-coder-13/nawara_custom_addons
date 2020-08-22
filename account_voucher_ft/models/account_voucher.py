# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree
from odoo.tools import amount_to_text_en
from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

V_GROUP = 'account_voucher_ft.group_voucher_product_based'
SEQ_TYPE = {
    'sale': 'voucher.receipt',
    'purchase': 'voucher.payment',
}
PAY_METH_CODES = [
    'cheque_payment',
    'cheque_receipt',
    'cheque_pdc_payment',
    'cheque_pdc_receipt'
]


class AccountVoucher(models.Model):
    _name = 'account.voucher'
    _description = 'Accounting Voucher'
    _inherit = ['mail.thread']
    _order = "date desc, id desc"

    def set_amt_in_worlds(self):
        amount, currency = self.amount, self.currency_id.name
        amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency=currency)
        if currency == 'AED':
            amount_in_words = str(amount_in_words).replace('AED', 'Dirhams')
            amount_in_words = str(amount_in_words).replace('Cents', 'Fils')
            amount_in_words = str(amount_in_words).replace('Cent', 'Fils')
        amount_in_words += '\tOnly'
        self.amt_in_words = amount_in_words

    amt_in_words = fields.Char(compute='set_amt_in_worlds')
    voucher_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase')
    ], string='Type', readonly=True, states={'draft': [('readonly', False)]}, oldname="type")
    name = fields.Char('Payment Reference',
                       readonly=True, states={'draft': [('readonly', False)]}, default='')
    date = fields.Date("Bill Date", readonly=True, required=True,
                       index=True, states={'draft': [('readonly', False)]},
                       copy=False, default=fields.Date.context_today)
    account_date = fields.Date("Accounting Date",
                               readonly=True, index=True, states={'draft': [('readonly', False)]},
                               help="Effective date for accounting entries", copy=False,
                               default=fields.Date.context_today)
    journal_id = fields.Many2one('account.journal', 'Journal', domain=[('type', 'in', ('bank', 'cash'))],
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})
    account_id = fields.Many2one('account.account', 'Account',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]}
                                 , domain=[('deprecated', '=', False)])
                                 # domain="[('deprecated', '=', False), ('internal_type','=', 'liquidity')]")
    line_ids = fields.One2many('account.voucher.line', 'voucher_id', 'Voucher Lines',
                               readonly=True, copy=True,
                               states={'draft': [('readonly', False)]})
    narration = fields.Text('Notes', readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', compute='_get_journal_currency',
                                  string='Currency', readonly=True, required=True,
                                  default=lambda self: self._get_currency())
    company_id = fields.Many2one('res.company', 'Company',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 related='journal_id.company_id', default=lambda self: self._get_company())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('proforma', 'Pro-forma'),
        ('posted', 'Posted')
    ], 'Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Voucher.\n"
             " * The 'Pro-forma' status is used when the voucher does not have a voucher number.\n"
             " * The 'Posted' status is used when user create voucher,a voucher number is generated and voucher entries are created in account.\n"
             " * The 'Cancelled' status is used when user cancel voucher.")
    reference = fields.Char('Bill Reference', readonly=True, states={'draft': [('readonly', False)]},
                            help="The partner reference of this document.", copy=False)
    amount = fields.Monetary(string='Total', store=True, compute='_compute_total', required=True, readonly=False,
                             default=0.0)
    tax_amount = fields.Monetary(readonly=True, store=True, compute='_compute_total')
    tax_correction = fields.Monetary(readonly=True, states={'draft': [('readonly', False)]},
                                     help='In case we have a rounding problem in the tax, use this field to correct it')
    number = fields.Char(readonly=True, copy=False)
    move_id = fields.Many2one('account.move', 'Journal Entry', copy=False)
    partner_id = fields.Many2one('res.partner', 'Partner', change_default=1, readonly=True,
                                 states={'draft': [('readonly', False)]})
    partner_account_id = fields.Many2one('account.account')
    payed_to_name = fields.Char(string="Paid To")
    paid = fields.Boolean(compute='_check_paid', help="The Voucher has been totally paid.")
    pay_now = fields.Selection([
        ('pay_now', 'Pay Directly'),
        ('pay_later', 'Pay Later'),
    ], 'Payment', index=True, readonly=True, states={'draft': [('readonly', False)]}, default='pay_now')
    date_due = fields.Date('Due Date', readonly=True, index=True, states={'draft': [('readonly', False)]})

    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True,
                                        oldname="payment_method", domain=[('payment_method_type', '=', 'normal')])
    payment_method_code = fields.Char(related='payment_method_id.code',
                                      help="Technical field used to adapt the interface to the payment type selected.",
                                      readonly=True)

    cheque_id = fields.Many2one('cheque.register', 'Cheque No.', domain=[('state', '=', 'blank')],
                                ondelete='restrict')
    # amount_in_words = fields.Float((14, 4), compute='onchange_amount')

    @api.depends('amount')
    def set_amt_in_words(self):
        amount, currency = self.amount, self.currency_id.name
        amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency=currency)
        if currency == 'AED':
            amount_in_words = str(amount_in_words).replace('AED', 'Dirhams')
            amount_in_words = str(amount_in_words).replace('Cents', 'Fils')
            amount_in_words = str(amount_in_words).replace('Cent', 'Fils')
        amount_in_words += '\tOnly'
        self.amt_in_words = amount_in_words.capitalize()

    def write(self, vals):
        if 'payment_method_id' in vals and self.payment_method_code in PAY_METH_CODES and self.cheque_id:
            raise UserError('Sorry You Cannot change Payment Method of this Payment,'
                            ' Because you already create a Cheque.')
        else:
            return super(AccountVoucher, self).write(vals)

    def cancel_cheque(self, unlink=False):
        self.state = 'cancel'
        if unlink:
            self.unlink()

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            self.account_id = self.voucher_type == 'purchase' and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.voucher_type == 'sale' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.voucher_type == 'purchase' and 'outbound' or 'inbound'
            return {'domain': {
                'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
        return {}

    @api.onchange('date')
    def onchange_date(self):
        self.account_date = self.date

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountVoucher, self). \
            fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and not self.user_has_groups(V_GROUP):
            arch = res['fields']['line_ids']['views']['tree']['arch']
            arch_el = etree.fromstring(arch)
            arch_el.find('field[@name="price_unit"]').set('string', 'Amount')
            res['fields']['line_ids']['views']['tree']['arch'] = etree.tostring(arch_el)
        return res

    @api.depends('move_id.line_ids.reconciled', 'move_id.line_ids.account_id.internal_type')
    def _check_paid(self):
        for rec in self:
            rec.paid = any(
                [((line.account_id.internal_type, 'in', ('receivable', 'payable')) and line.reconciled) for line in
                 rec.move_id.line_ids])

    @api.model
    def _get_currency(self):
        journal = self.env['account.journal'].browse(self._context.get('journal_id', False))
        if journal.currency_id:
            return journal.currency_id.id
        return self.env.user.company_id.currency_id.id

    @api.model
    def _get_company(self):
        return self._context.get('company_id', self.env.user.company_id.id)

    @api.depends('name', 'number')
    def name_get(self):
        return [(r.id, (r.number or _('Voucher'))) for r in self]

    @api.depends('journal_id', 'company_id')
    def _get_journal_currency(self):
        for rec in self:
            rec.currency_id = rec.journal_id.currency_id.id or rec.company_id.currency_id.id

    @api.depends('tax_correction', 'line_ids.price_subtotal')
    def _compute_total(self):
        for voucher in self:
            if voucher.line_ids:
                total = 0
                tax_amount = 0
                for line in voucher.line_ids:
                    tax_info = line.tax_ids.compute_all(line.price_unit, voucher.currency_id, line.quantity,
                                                        line.product_id, voucher.partner_id)
                    total += tax_info.get('total_included', 0.0)
                    tax_amount += sum([t.get('amount', 0.0) for t in tax_info.get('taxes', False)])
                voucher.amount = total + voucher.tax_correction
                voucher.tax_amount = tax_amount

    # @api.one
    # @api.depends('account_pay_now_id', 'account_pay_later_id', 'pay_now')
    # def _get_account(self):
    #     self.account_id = self.account_pay_now_id if self.pay_now == 'pay_now' else self.account_pay_later_id

    @api.onchange('date')
    def onchange_date(self):
        self.account_date = self.date

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.partner_account_id = self.partner_id.property_account_receivable_id \
            if self.voucher_type == 'sale' else self.partner_id.property_account_receivable_id

    def proforma_voucher(self):
        self.action_move_line_create()

    def action_cancel_draft(self):
        self.write({'state': 'draft'})

    def cancel_voucher(self):
        for voucher in self:
            voucher.move_id.button_cancel()
            voucher.move_id.unlink()
        self.write({'state': 'cancel', 'move_id': False})

    def unlink(self):
        for voucher in self:
            cheque_id = voucher.cheque_id
            if voucher.state not in ('draft', 'cancel'):
                raise UserError(_('Cannot delete voucher(s) which are already opened or paid.'))
            res = super(AccountVoucher, voucher).unlink()
            if cheque_id:
                cheque_id.cancel_cheque(unlink=True)
        return res

    def first_move_line_get(self, move_id, company_currency, current_currency):
        debit = credit = 0.0
        if self.voucher_type == 'purchase':
            credit = self._convert_amount(self.amount)
        elif self.voucher_type == 'sale':
            debit = self._convert_amount(self.amount)
        if debit < 0.0:
            debit = 0.0
        if credit < 0.0:
            credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        # set the first line of the voucher
        move_line = {
            'name': self.name or '/',
            'debit': debit,
            'credit': credit,
            'account_id': self.account_id.id,
            'move_id': move_id,
            'journal_id': self.journal_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': company_currency != current_currency and current_currency or False,
            'amount_currency': (sign * abs(self.amount)  # amount < 0 for refunds
                                if company_currency != current_currency else 0.0),
            'date': self.account_date,
            'date_maturity': self.date_due
        }
        return move_line

    def account_move_get(self):
        if self.number:
            name = self.number
        else:
            sequence = self.env['ir.sequence'].with_context(ir_sequence_date=self.date). \
                next_by_code(SEQ_TYPE.get(self.voucher_type))
            name = sequence if sequence else ''

        move = {
            'name': name,
            'journal_id': self.journal_id.id,
            'narration': self.narration,
            'date': self.account_date,
            'ref': self.reference,
        }
        return move

    def _convert_amount(self, amount):
        '''
        This function convert the amount given in company currency. It takes either the rate in the voucher (if the
        payment_rate_currency_id is relevant) either the rate encoded in the system.
        :param amount: float. The amount to convert
        :param voucher: id of the voucher on which we want the conversion
        :param context: to context to use for the conversion. It may contain the key 'date' set to the voucher date
            field in order to select the good rate to use.
        :return: the amount in the currency of the voucher's company
        :rtype: float
        '''
        for voucher in self:
            return voucher.currency_id.compute(amount, voucher.company_id.currency_id)

    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        for line in self.line_ids:
            # create one move line per voucher line where amount is not 0.0
            if not line.price_subtotal:
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context,
            # so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(line.price_unit * line.quantity)
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': self.partner_id.id,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                'date': self.account_date,
                'tax_ids': [(4, t.id) for t in line.tax_ids],
                'amount_currency': line.price_subtotal if current_currency != company_currency else 0.0,
                'currency_id': company_currency != current_currency and current_currency or False,
            }

            self.env['account.move.line'].with_context(apply_taxes=True).create(move_line)
        return line_total

    def action_move_line_create(self):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        for voucher in self:
            local_context = dict(self._context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            if not self.cheque_id and self.payment_method_code in PAY_METH_CODES:
                raise UserError('Without a Cheque Entry, You cannot validate this Payment')
            amount = self.amount
            for line in self.line_ids:
                amount -= line.price_subtotal
            if amount != 0:
                raise UserError('Please Validate the Payment Lines. Total Amount and'
                                'Sum of lines doesnt match')
            company_currency = voucher.journal_id.company_id.currency_id.id
            current_currency = voucher.currency_id.id or company_currency
            # we select the context to use accordingly if it's a multicurrency case or not
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = local_context.copy()
            ctx['date'] = voucher.account_date
            ctx['check_move_validity'] = False
            # Create the account move record.
            move = self.env['account.move'].create(voucher.account_move_get())
            # Get the name of the account_move just created
            # Create the first line of the voucher with main Asset/Payable Account (Cash, Bank, etc)
            move_line = self.env['account.move.line'].with_context(ctx).create(
                voucher.with_context(ctx).first_move_line_get(move.id, company_currency, current_currency))
            line_total = move_line.debit - move_line.credit
            if voucher.voucher_type == 'sale':
                line_total = line_total - voucher._convert_amount(voucher.tax_amount)
            elif voucher.voucher_type == 'purchase':
                line_total = line_total + voucher._convert_amount(voucher.tax_amount)
            # Create one move line per voucher line where amount is not 0.0
            line_total = voucher.with_context(ctx).voucher_move_line_create(line_total, move.id, company_currency,
                                                                            current_currency)

            # Add tax correction to move line if any tax correction specified
            if voucher.tax_correction != 0.0:
                tax_move_line = self.env['account.move.line'].search(
                    [('move_id', '=', move.id), ('tax_line_id', '!=', False)], limit=1)
                if len(tax_move_line):
                    tax_move_line.write(
                        {'debit': tax_move_line.debit + voucher.tax_correction if tax_move_line.debit > 0 else 0,
                         'credit': tax_move_line.credit + voucher.tax_correction if tax_move_line.credit > 0 else 0})

            # We post the voucher.
            voucher.write({
                'move_id': move.id,
                'state': 'posted',
                'number': move.name
            })
            move.post()
            if voucher.cheque_id:
                voucher.cheque_id.amount = voucher.amount
                voucher.cheque_id.action_validate()
        return True


class AccountVoucherLine(models.Model):
    _name = 'account.voucher.line'
    _description = 'Voucher Lines'

    def _get_readonly(self):
        return self.user.user_has_groups(V_GROUP)

    name = fields.Text(string='Description')
    sequence = fields.Integer(default=10,
                              help="Gives the sequence of this line when displaying the voucher.")
    voucher_id = fields.Many2one('account.voucher', 'Voucher', required=1, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product',
                                 ondelete='set null', index=True)
    account_id = fields.Many2one('account.account', string='Account',
                                 required=True, domain=[('deprecated', '=', False)],
                                 help="The income or expense account related to the selected product.")
    project_id = fields.Many2one("project.project", string="Project", required=False)

    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'),
                              oldname='amount')
    price_subtotal = fields.Monetary(string='Amount',
                                     store=True, readonly=_get_readonly, compute='_compute_subtotal')
    quantity = fields.Float(digits=dp.get_precision('Product Unit of Measure'),
                            required=True, default=1)
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    company_id = fields.Many2one('res.company', related='voucher_id.company_id', string='Company', store=True,
                                 readonly=True)
    tax_ids = fields.Many2many('account.tax', string='Tax', help="Only for tax excluded from price")
    currency_id = fields.Many2one('res.currency', related='voucher_id.currency_id')

    @api.depends('price_unit', 'tax_ids', 'quantity', 'product_id', 'voucher_id.currency_id')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
            if line.tax_ids:
                taxes = line.tax_ids.compute_all(line.price_unit, line.voucher_id.currency_id, line.quantity,
                                                 product=line.product_id, partner=line.voucher_id.partner_id)
                line.price_subtotal = taxes['total_excluded']

    @api.onchange('product_id', 'price_unit')
    def _onchange_line_details(self):
        if not self.product_id:
            return {}
        context = self.env.context
        company = self.company_id if self.company_id is not None else context.get('company_id', False)
        currency = self.currency_id
        if not self.voucher_id.partner_id:
            raise UserError(_("You must first select a partner!"))
        if self.voucher_id.partner_id.lang:
            self = self.with_context(lang=self.voucher_id.partner_id.lang)

        fpos = self.voucher_id.partner_id.property_account_position_id
        accounts = self.product_id.product_tmpl_id.get_product_accounts(fpos)
        account = accounts['income'] if type == 'sale' else accounts['expense']
        values = {
            'name': self.product_id.partner_ref,
            'account_id': account.id,
        }

        if type == 'purchase':
            values['price_unit'] = self.price_unit or self.product_id.standard_price
            taxes = self.product_id.supplier_taxes_id or account.tax_ids
            if self.product_id.description_purchase:
                values['name'] += '\n' + self.product_id.description_purchase
        else:
            values['price_unit'] = self.product_id.lst_price
            taxes = self.product_id.taxes_id or account.tax_ids
            if self.product_id.description_sale:
                values['name'] += '\n' + self.product_id.description_sale

        values['tax_ids'] = taxes.ids

        if company and currency:
            if company.currency_id != currency:
                if type == 'purchase':
                    values['price_unit'] = self.product_id.standard_price
                values['price_unit'] = values['price_unit'] * currency.rate
        return {'value': values}

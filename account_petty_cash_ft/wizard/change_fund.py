from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, float_is_zero


class ChangeFundWizard(models.TransientModel):

    _name = 'pettycash.fund.change'
    _description = 'Petty Cash Fund Change Wizard'

    fund = fields.Many2one('pettycash.fund', required=True, readonly=True)
    custodian = fields.Many2one('res.users', readonly=True)
    fund_amount = fields.Float(related='fund.amount', readonly=True, digits=dp.get_precision('Product Price'))
    new_amount = fields.Float(
        digits=dp.get_precision('Product Price'))
    payable_account = fields.Many2one(
        'account.account', domain=[('internal_type', '=', 'payable')])
    receivable_account = fields.Many2one(
        'account.account', domain=[('internal_type', '=', 'receivable')])
    effective_date = fields.Date(required=True)
    do_receivable = fields.Boolean()
    move = fields.Many2one('account.move', string="Journal Entry")

    @api.onchange('new_amount')
    def onchange_new_amount(self):

        for wiz in self:
            res = False
            if float_compare(wiz.new_amount, wiz.fund_amount,
                             precision_digits=2) == -1:
                res = True
            wiz.do_receivable = res

    def change_fund(self):

        # Create the petty cash fund
        #
        for wizard in self:
            fnd = wizard.fund

            # Make necessary changes to fund
            #
            update_vals = {}
            if fnd.name and fnd.name != wizard.fund_name:
                update_vals.update({'name': wizard.fund_name})
            if wizard.custodian and fnd.custodian.id != wizard.custodian.id:
                update_vals.update({'custodian': wizard.custodian.id})
            fnd.write(update_vals)

            # Is there is a change in fund amount create journal entries
            #
            if not float_is_zero(wizard.new_amount, precision_digits=2) \
                and float_compare(
                    fnd.amount, wizard.new_amount, precision_digits=2) != 0:

                action = 'Increase'
                if float_compare(wizard.new_amount, fnd.amount,
                                 precision_digits=2) == -1:
                    action = 'Decrease'
                desc = _("%s Petty Cash Fund (%s)"
                         % (action, wizard.fund.name))

                # If it is an increase create a payable account entry. If
                # we are decreasing the fund amount it should be a receivable
                # from the custodian.
                #
                if action == 'Increase':
                    move = fnd.create_payable_journal_entry(
                        fnd, wizard.payable_account.id, wizard.effective_date,
                        wizard.new_amount - wizard.fund_amount, desc)
                else:
                    move = fnd.create_receivable_journal_entry(
                        fnd, wizard.receivable_account.id,
                        wizard.effective_date,
                        wizard.fund_amount - wizard.new_amount, desc)
                wizard.move = move

                # Change the amount on the fund record
                fnd.change_fund_amount(wizard.new_amount)

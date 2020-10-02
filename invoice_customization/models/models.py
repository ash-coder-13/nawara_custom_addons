# -*- coding: utf-8 -*-
import datetime
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class invoiceModuleCost(models.Model):
    _name = 'invoice.module.cost'

    name = fields.Char(string="Name")
    account_journal = fields.Many2one("account.journal", string="Journal Account")
    account_id = fields.Many2one("account.account", string="Default Account", required=True)
    cost_tree_ids = fields.One2many('invoice.module.cost.tree', 'invoice_cost_id', string="Line ID")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('invoice.module.cost.seq')
        return super(invoiceModuleCost, self).create(vals)

    def importBalancesCustomer(self):
        account_id = None
        invoice_type = None
        if self.cost_tree_ids:
            for rec in self.cost_tree_ids:
                if rec.partner_cost_ids.customer:
                    account_id = rec.partner_cost_ids.property_account_receivable_id.id
                    invoice_type = 'out_invoice'
                elif rec.partner_cost_ids.supplier:
                    account_id = rec.partner_cost_ids.property_account_payable_id.id
                    invoice_type = 'in_invoice'
                if not rec.account_invoice:
                    records = self.env['account.move'].create({
                        'partner_id': rec.partner_cost_ids.id,
                        'invoice_date': rec.date,
                        'journal_id': self.account_journal.id,
                        'account_id': account_id,
                        'type': invoice_type,
                    })

                    records.invoice_line_ids.create({
                        'name': rec.description,
                        'price_unit': rec.amount,
                        'account_id': self.account_id.id,
                        'quantity': 1,
                        'move_id': records.id
                    })
                    rec.account_invoice = records.id
                else:
                    raise UserError(_("Invoices already exist for these records."))


class invoiceModuleCostTree(models.Model):
    _name = 'invoice.module.cost.tree'

    amount = fields.Float(string="Amount")
    date = fields.Date(string="Date")
    description = fields.Char(string="Description")
    account_invoice = fields.Many2one("account.move", string="Invoices")
    partner_cost_ids = fields.Many2one('res.partner', string="Partner")
    invoice_cost_id = fields.Many2one('invoice.module.cost', string="Line Ids")


class extDepreciationJob(models.Model):
    _name = 'ext.depreciation.job'

    # Cron job for creation of move it should be run once a day or every min and you have
    # to manually create this from scheduled actions
    @api.model
    def _cron_create_move(self):
        for recs in self.env['account.asset.asset'].search([]):
            if recs.state == 'open':
                for line in recs.depreciation_line_ids:
                    if not line.move_check:
                        if str(line.depreciation_date) == str(datetime.now().date()):
                            line.create_move()


# inherit from account.asset.asset
class extAccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    # Inherit the method and use super to override
    def validate(self):
        res = super(extAccountAssetAsset, self).validate()
        OpeningAccount = self.env['account.account'].search([('code', '=', '3001121')])
        JournalAccount = self.env['account.journal'].search([('code', '=', 'ACDEP')])
        if self.salvage_value > 0:
            JournalEntry = self.genrateJournalEntries(JournalAccount.id, self.date)
            self.genrateJournalEntriyLines(JournalEntry, OpeningAccount.id, False, 'Debit', self.salvage_value, False)
            self.genrateJournalEntriyLines(JournalEntry, self.category_id.account_depreciation_id.id, False, 'Credit',
                                           self.salvage_value, True)
        return res

    def genrateJournalEntries(self, journal_id, date):
        JornalEntries = self.env['account.move']
        create_journal_entry = JornalEntries.create({
            'journal_id': journal_id,
            'date': date,
            'asset_salvage_id': self.id,  # field to link the record
        })
        return create_journal_entry

    def genrateJournalEntriyLines(self, move_id, account_id, partner_id, name, amount, deb_amount):
        JornalEntries_lines = self.env['account.move.line']
        if deb_amount:
            move_id.line_ids.create({
                'account_id': account_id,
                'partner_id': partner_id,
                'name': str(name),
                'debit': 0,
                'credit': amount,
                'move_id': move_id.id
            })
        else:
            move_id.line_ids.create({
                'account_id': account_id,
                'partner_id': partner_id,
                'name': str(name),
                'debit': amount,
                'credit': 0,
                'move_id': move_id.id
            })
    # create_journal_entry.post()


class extAccountMove(models.Model):
    _inherit = 'account.move'

    asset_salvage_id = fields.Many2one('account.asset.asset', string="Asset Salvage ID")

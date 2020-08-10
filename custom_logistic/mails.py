# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ToMails(models.Model):
    _name = 'to.mails'
    _rec_name = 'name'

    name = fields.Char("Recipient Email:")


class MultiMails(models.Model):
    _name = 'multi.mails'
    _rec_name = 'name'
    _description = 'Operational Email Notification WorkFlow'

    name = fields.Char(default="Operational Mails Notifications")
    sale_support = fields.Many2many(comodel_name="to.mails", relation="multi_mails_sale_support_rel",
                                    string="Sales Support", )
    ntf_terminal = fields.Many2many(comodel_name="to.mails", relation="multi_mails_ntf_terminal_rel",
                                    string="NTF Terminal", )
    custom_clearance = fields.Many2many(comodel_name="to.mails", relation="multi_mails_custom_clearance_rel",
                                        string="Custom Clearance", )
    finance = fields.Many2many(comodel_name="to.mails", relation="multi_mails_finance_rel", string="Finance", )


class statemnent_accounts(models.Model):
    _name = 'statemnent.accounts'


class statemnent_invoices(models.Model):
    _name = 'statemnent.invoices'


class report_partner_ledger_partner_ledger_2_report(models.Model):
    _name = 'report.partner_ledger.partner_ledger_2_report'


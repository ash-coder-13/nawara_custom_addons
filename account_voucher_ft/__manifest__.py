# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Receipt and Payment Vouchers [FT]',
    'version': '1.0',
    'summary': 'Manage your Payment and Receipt Vouchers',
    'description': """
TODO

old description:
Invoicing & Payments by Accounting Voucher & Receipts
=====================================================
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers. 

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. 

The Invoicing system includes receipts and vouchers (an easy way to keep track of sales and purchases). It also offers you an easy method of registering payments, without having to encode complete abstracts of account.

This module manages:

* Voucher Entry
* Voucher Receipt
* Voucher Payment
    """,
    'category': 'Accounting',
    'sequence': 20,
    'author': 'Ashish',
    'website': 'www.hashinclu.de',
    'depends': ['account_accountant', 'account_cheque_ft','web_readonly_bypass','accounting_pdf_reports','account_voucher'],
    'data': [
         'security/ir.model.access.csv',
        'data/account_voucher_data.xml',
        'security/account_voucher_security.xml',
        'reports/report_partnerledger.xml',
        'wizard/account_report_partner_ledger_view.xml',
        'views/res_config_view.xml',
        'views/account_voucher_views.xml',
        'views/account_move_cash_credit_report.xml',
        'views/account_move_cash_debit_report.xml',
        'views/extended_layout_view.xml',
         # 'views/account_voucher_reports.xml',
         # 'views/account_journal_voucher_reports.xml',
        'views/account_payment_report.xml',
        'reports/voucher_reports.xml',
        'views/invoice_opening_entry.xml',

    ],
    'auto_install': False,
    'installable': True,
}

{
    'name': 'Cheque Manager',
    'version': '13.0.1',
    'summary': 'Managing Cheque in Finance',
    'description': 'This module enables cheque facility in Accounting Payments, Cheque Register,'
                   'Cheque Printing, Post Dated Cheques, Bank Guarantee, Security Cheque, etc',
    'category': 'Accounting',
    'author': 'Ashish`',
    'website': '',
    'depends': ['account_accountant'],
    'data': [
        'data/account_cheque_data.xml',
        'security/ir.model.access.csv',
        'views/custom_bank_views.xml',
        'views/account_cheque_templates.xml',
        'views/cheque_register_views.xml',
        'views/category_cheques_views.xml',
        'views/account_invoice_views.xml',
        'views/account_payment_views.xml',
        'reports/print_cheque_format.xml'
    ],
    'installable': True,
    'auto_install': False,
}
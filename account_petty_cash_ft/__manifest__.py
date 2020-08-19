{
    "name": "Petty Cash",
    "summary": "Automated management of petty cash funds",
    "description": """
    """,
    "author": "Hash Inclu.de",
    "website": "www.hashinclu.de",
    "license": "AGPL-3",
    "version": "13.0.1.0",
    "category": "Accounting & Finance",
    "depends": [
        'account',
        'account_accountant',
        'project',
        'account_voucher_ft',
        'account_cheque_ft',
        'hr'
    ],
    "data": [
        'security/petty_cash.xml',
        'security/ir.model.access.csv',
        'data/petty_cash_data.xml',
        'views/petty_cash_view.xml',
        # 'wizard/change_fund_view.xml',
        # 'wizard/close_fund_view.xml',
        'wizard/create_fund_view.xml',
        # 'wizard/reconcile_view.xml',
        # 'wizard/reopen_view.xml',
        'views/account_voucher_view.xml',
        # 'views/account_payment_view.xml',
        'views/res_config_view.xml',
        'views/extended_layout_view.xml',
        'views/petty_cash_report.xml',
        'reports/account_voucher_report.xml'
    ],
    "installable": True,
    "active": True,
}









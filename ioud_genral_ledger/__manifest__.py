{
    'name': 'Account General Ledger I',
    'description': 'View your Account General Ledger',
    'author': 'Ashish',
    'website': "http://www.solutionfounder.com",
    'category': 'account',
    'version': '13.0.1.0',
    'depends': ['base', 'report', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/module_report.xml',
        'wizard/genral_ledger.xml',
    ],
}

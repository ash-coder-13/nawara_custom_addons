# -*- coding: utf-8 -*-
{
    'name': "Import Balance,Salvage Value JV",


    'description': """No description""",

    'author': "Ashish",
    'website': "http://www.solutionfounder.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'account',
    'version': '13.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account_asset','account_accountant','analytic','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/invoice_cost_view.xml',
    ],
}
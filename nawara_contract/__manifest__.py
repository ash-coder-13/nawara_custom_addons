# -*- coding: utf-8 -*-
{
    'name': "nawara_contract",

    'summary': """
        Contract Customization""",

    'description': """
        Contract Customization
    """,

    'author': 'Solution Founder',
    'website': 'http://solutionfounder.com/',
    'version': '10.0.2.3',
    'category': 'hr',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_contract','hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],

}
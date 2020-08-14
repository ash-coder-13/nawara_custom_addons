# -*- coding: utf-8 -*-
{
    'name': "nawara_invoice_container",

    'summary': "nawara_invoice_container",

    'description': "nawara_invoice_container",

    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'version': '10.0.1.12',
    'category': 'account',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],
    # always loaded
    'data': [
        'template.xml',
        'views/module_report.xml',
    ],
    'css': ['static/src/css/report.css'],
}

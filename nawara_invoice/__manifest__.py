# -*- coding: utf-8 -*-
{
    'name': "nawara_invoice",

    'summary': "nawara_invoice",

    'description': "nawara_invoice",

    'author': 'Ashish',
    'website': "http://www.solutionfounder.com",
    'version': '13.0.1.0',
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

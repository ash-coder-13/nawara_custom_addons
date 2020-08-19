# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Employee Extension K S A',
    'description': 'HR Employee Extension K S A',
    'author': 'Ashish',
    'summary': 'Hr Employee KSA loacalization BAFCO',
    'website': 'http://solutionfounder.com/',
    'version': '13.0.1.0',
    'depends': ['base', 'hr', 'hr_contract', 'hr_payroll', 'hr_attendance', 'maintenance'],
    'data': [
        'templates.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'css': ['static/src/css/my_css.css'],
    'installable': True,
    'auto_install': False
}

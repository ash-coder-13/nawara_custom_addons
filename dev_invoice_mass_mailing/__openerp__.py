# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintellecs.com>).
#
##############################################################################

{
    'name': 'Mass Customer Invoice Send by Mail',
    'version': '1.0',
    'sequence': 1,
    'description': """
Apps will send invoice mail to customers by Mass invocie send mail wizard. 

Mass Customer Invoice Send by Mail
Odoo Mass Customer Invoice Send by Mail
send invoice to customers by Mass invoice mail wizard
Odoo send invoice to customers by Mass invoice mail wizard
Send mass invoice to customers 
Odoo send mass invoice to customers
Send mass invoice odoo app
Send mass invoice odoo apps
Mass invoice 
Odoo mass invoice
Mass invoice send by email
Odoo mass invoice send by email
Mass invoice send by email odoo app
Mass invoice management
Mass invoice management odoo apps
Odoo mass invoice management
Manage the mass of invoice
Odoo manage the mass of invoice
Mass invoices by email
Odoo mass invoices by email
Send mass invoice email
Odoo send mass invoice email
Send mass invoice mail
Odoo send mass invoice mail


""",
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com/',
    'images': ['images/main_screenshot.png'],
    'summary': 'Apps will send invoice mail to customers by Mass invocie send mail wizard.',
    'category': 'account',
    'depends': ['base',
                'sale',
                'mail',
                ],
    'demo': [],
    'test': [],
    'data': [
        'views/wizard_invoice_mass.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price':10.0,
    'currency':'EUR',  
    'live_test_url':'https://youtu.be/kK7F-gGUzOk',     
}

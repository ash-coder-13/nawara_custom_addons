# -*- coding: utf-8 -*-
{
    'name': "Custom Clearance Transportation Projects",
    'summary': """Provides The Import, Export, Transportation, Projects and Transportation Project Logistics Facility
        """,
    'description': """
    Provides The Import, Export, Transportation, Projects and Transportation Project Logistics Facility
    """,
    'author': 'Ashish Thomas',
    'website': "",
    'category': 'Specific Industry Applications',
    'version': '13.0.1.0',
    'depends': ['base', 'sale', 'account', 'sale_stock', 'fleet', 'stock'],
    'data': [
        'security/security.xml',
         'security/ir.model.access.csv',
         # 'views.xml',
        'quote.xml',
        'supplier.xml',
        'mails.xml',
        'report.xml',
    ],
    'installable': True,
    'auto_install': False

}

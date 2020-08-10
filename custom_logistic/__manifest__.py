# -*- coding: utf-8 -*-
{
    'name': "Custom Clearance Transportation Projects",
    'summary': """Provides The Import, Export, Transportation, Projects and Transportation Project Logistics Facility
        """,
    'description': """
    Provides The Import, Export, Transportation, Projects and Transportation Project Logistics Facility
    """,
    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'category': 'Specific Industry Applications',
    'version': '10.0.2.33',
    'depends': ['base', 'sale', 'account', 'sale_stock', 'fleet', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views.xml',
        'quote.xml',
        'supplier.xml',
        'mails.xml',
        'report.xml',
    ],
    'installable': True,
    'auto_install': False

}

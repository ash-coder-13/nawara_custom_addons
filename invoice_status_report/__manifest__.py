{
    'name': "invoice_status_report",

    'summary': "invoice_status_report",

    'description': "invoice_status_report",

    'author': 'Ashish',
    'website': "http://www.solutionfounder.com",
    'version': '13.0.1.0',
    'category': 'account',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],
    # always loaded
    'data': [
        'ir.model.access.csv',
        'template.xml',
        'views/module_report.xml',
    ],
    'css': ['static/src/css/report.css'],
}

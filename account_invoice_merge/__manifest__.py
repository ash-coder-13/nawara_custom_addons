# -*- coding: utf-8 -*-
# Copyright 2004-2010 Tiny SPRL (http://tiny.be).
# Copyright 2010-2011 Elico Corp.
# Copyright 2016 Acsone (https://www.acsone.eu/)
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice Merge Modified',
    'version': '13.0.1.0.2',
    'category': 'Finance',
    'summary': "This Module is modified as per transportation seniors 'Merge invoices in draft'",
    'author': 'SolutionFounder',
    'website': "http://www.solutionfounder.com",
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'wizard/invoice_merge_view.xml',
    ],
    'installable': True,
}

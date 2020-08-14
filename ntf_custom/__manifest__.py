# -*- coding: utf-8 -*-
# /#############################################################################
#
#    NTF Group
#    Copyright (C) 2019-TODAY NTF Group(<http://ntf-group.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# /#############################################################################
{
    'name': 'NTF Customizations',
    'version': '10.1.2',
    'description': """Nawara Transport and Freight Group Odoo Customizations""",
    'summary': """Nawara Transport and Freight Group Odoo Customizations""",
    'category': 'Sales',
    'license': 'LGPL-3',
    'author': "Muhammad Faizal NS",
    'website': "http://ntf-group.com/",
    'depends': ['base', 'custom_logistic', 'account', 'report', 'sales_team', 'crm', 'fleet'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_terminal_wiz.xml',
        'report/reports.xml',
        'report/customer_focuzed_revenue_view.xml',
        'report/report_customer_focuzed_rev.xml',
        'views/inherited_views.xml'
    ],
    'qweb': [],
    'installable': True,
    'application': True,
}

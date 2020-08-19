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
    'name': 'Any Screen to Excel',
    'version': '13.0.1.0.0',
    'category': 'Web',
    'author': 'Ashish',
    'website': 'http://ntf-group.com/',
    'license': 'AGPL-3',
    'depends': [
        'web',
    ],
    "data": [
        'views/web_export_view_view.xml',
    ],
    'qweb': [
        "static/src/xml/web_export_view_template.xml",
    ],
    'installable': True,
    'auto_install': False,
}

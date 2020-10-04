# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################
from openerp import models, fields, api
import datetime

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.tax_balance.module_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('tax_balance.module_report')
        records = self.env['account.tax'].browse(docids)
        to_date = 1
        from_date = 2
        current_date = datetime.datetime.now().date()

        for rec in self.env['wizard.open.tax.balances'].search([])[-1]:
            from_date = rec.from_date
            to_date = rec.to_date

        def gettype(types):
            type = types.split()
            required = 'Sale'
            if required.lower() == type[0].lower():
                return 1
            else:
                return 2

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.tax',
            'docs': records,
            'data': data,
            'gettype': gettype,
            'today_date': current_date,
            'to_date':to_date,
            'from_date':from_date,
        }

        return docargs

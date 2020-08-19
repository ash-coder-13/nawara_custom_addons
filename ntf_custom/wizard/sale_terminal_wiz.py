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
import xlwt
import xlsxwriter
from odoo.tools import config
import base64
from odoo import api, fields, models, tools, SUPERUSER_ID, _, modules
from datetime import datetime, timedelta, date
import calendar
import datetime
import dateutil.relativedelta
import dateutil.parser


class SaleTerminalExcelReport(models.TransientModel):
    _name = 'sale.terminal.excel.report'
    _description = 'Terminal and CC Excel Report'

    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    start_date_m = fields.Date('Start Date')
    end_date_m = fields.Date('End Date')
    period_string = fields.Selection(
        (('this_week', 'This Week'), ('this_month', 'This Month'), ('last_three_months', 'Last 3 Months'),
         ('last_six_months', 'Last 6 Months'), ('last_one_year', 'Last 1 Year')))
    is_custom_range = fields.Boolean("Custom Range")

    @api.onchange('start_date', 'end_date')
    def _onchange_date(self):
        for file in self:
            if file.start_date:
                file.start_date_m = file.start_date
            if file.end_date:
                file.end_date_m = file.end_date

    @api.onchange('period_string')
    def onchange_period(self):
        if self.period_string == 'this_month':
            today = datetime.datetime.now()
            _, num_days = calendar.monthrange(today.year, today.month)
            start = datetime.datetime(today.year, today.month, 1)
            end = today
            self.start_date = start
            self.end_date = end
        if self.period_string == 'last_three_months':
            today = datetime.datetime.now()
            start = today - dateutil.relativedelta.relativedelta(months=3)
            print ("start", start)
            end = datetime.datetime.now()
            self.start_date = start
            self.end_date = end
        if self.period_string == 'last_six_months':
            today = datetime.datetime.now()
            start = today - dateutil.relativedelta.relativedelta(months=6)
            print ("start", start)
            end = datetime.datetime.now()
            self.start_date = start
            self.end_date = end
        if self.period_string == 'last_one_year':
            today = datetime.datetime.now()
            start = today - dateutil.relativedelta.relativedelta(months=12)
            print ("start", start)
            end = datetime.datetime.now()
            self.start_date = start
            self.end_date = end
        if self.period_string == 'this_week':
            day = datetime.datetime.now()
            start = day - timedelta(days=day.weekday() + 1)
            end = start + timedelta(days=6)
            self.start_date = start
            self.end_date = end


    def genarate_excel_report(self):
        custom_value = {}
        custom_obj = self.env['import.logic']
        sale_obj = self.env['sale.order']
        terminal_sea = sale_obj.search(
            [('sales_imp_id.date', '>=', self.start_date_m), ('sales_imp_id.date', '<=', self.end_date_m)])
        custom_sea = custom_obj.search([('date', '>=', self.start_date_m), ('date', '<=', self.end_date_m)])
        workbook = xlwt.Workbook()

        # Style for Excel
        style0 = xlwt.easyxf(
            'font: name Times New Roman bold on;align: horiz center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
        style1 = xlwt.easyxf(
            'font: name Times New Roman bold on; pattern: pattern solid, fore_colour green;align: horiz center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')

        # Excel Heading Manipulation
        sheet = workbook.add_sheet("Report By BL")
        sheet.col(0).width = 2000
        sheet.col(1).width = 17553
        sheet.col(2).width = 13553
        sheet.col(3).width = 9000
        sheet.col(4).width = 6000
        sheet.col(5).width = 6000
        sheet.col(6).width = 9000
        sheet.col(7).width = 9000
        sheet.col(8).width = 6000
        sheet.col(9).width = 9000
        sheet.col(10).width = 9000
        sheet.col(11).width = 9000
        sheet.col(12).width = 9000
        sheet.col(13).width = 9000
        sheet.col(14).width = 9000
        sheet.col(15).width = 10000
        sheet.write(0, 0, 'Job No', style1)
        sheet.write(0, 1, 'Customer', style1)
        sheet.write(0, 2, 'By Customer', style1)
        sheet.write(0, 3, 'Port', style1)
        sheet.write(0, 4, 'B/L Number', style1)
        sheet.write(0, 5, 'No. Of Containers', style1)
        sheet.write(0, 6, 'Docs Received Date', style1)
        sheet.write(0, 7, 'ETA', style1)
        sheet.write(0, 8, 'Demurrage Date', style1)
        sheet.write(0, 9, 'Cleared Date', style1)
        sheet.write(0, 10, 'Delivery Plan Date', style1)
        sheet.write(0, 11, 'Actual Delivery Date', style1)
        sheet.write(0, 12, 'Detention Date', style1)
        sheet.write(0, 13, 'EIR Date(Actual Empty Return)', style1)
        sheet.write(0, 14, 'Invoice Date', style1)
        sheet.write(0, 15, 'Shipment Status', style1)

        row = 1
        for rec in custom_sea:
            sheet.write(row, 0, rec.job_no or "", style0)
            sheet.write(row, 1, rec.customer.name or "", style0)
            sheet.write(row, 2, rec.by_customer.name or "", style0)
            sheet.write(row, 3, rec.port.name or "", style0)
            sheet.write(row, 4, rec.bill_no or "", style0)
            sheet.write(row, 5, rec.count_crt or "", style0)
            sheet.write(row, 6, rec.org_date or "", style0)
            sheet.write(row, 7, rec.vsl_exp_arvl_date or "", style0)
            sheet.write(row, 8, rec.demurrage or "", style0)
            sheet.write(row, 9, rec.saddad or "", style0)
            sheet.write(row, 10, rec.delivery or "", style0)
            sheet.write(row, 11, rec.delivery_date or "", style0)
            sheet.write(row, 12, rec.detention_date or "", style0)
            sheet.write(row, 13, rec.eir_date or "", style0)
            sheet.write(row, 14, rec.acc_link.date_invoice or "", style0)
            sheet.write(row, 15, rec.status.name or "", style0)
            row += 1

        sheet2 = workbook.add_sheet("Container Details")
        sheet2.col(0).width = 6000
        sheet2.col(1).width = 17553
        sheet2.col(2).width = 6000
        sheet2.col(3).width = 9000
        sheet2.col(4).width = 6000
        sheet2.col(5).width = 6000
        sheet2.col(6).width = 9000
        sheet2.col(7).width = 9000
        sheet2.col(8).width = 6000
        sheet2.col(9).width = 9000
        sheet2.col(10).width = 9000
        sheet2.col(11).width = 9000
        sheet2.col(12).width = 9000
        sheet2.col(13).width = 9000
        sheet2.col(14).width = 9000
        sheet2.col(15).width = 10000
        sheet2.write(0, 0, 'Order/Job No', style1)
        sheet2.write(0, 1, 'Customer', style1)
        sheet2.write(0, 2, 'Port', style1)
        sheet2.write(0, 3, 'B/L Number', style1)
        sheet2.write(0, 4, 'Container Number', style1)
        sheet2.write(0, 5, 'ETA', style1)
        sheet2.write(0, 6, 'Docs Received Date', style1)
        sheet2.write(0, 7, 'Demurrage Date', style1)
        sheet2.write(0, 8, 'Cleared Date', style1)
        sheet2.write(0, 9, 'PullOut Date', style1)
        sheet2.write(0, 10, 'Actual Delivery Date', style1)
        sheet2.write(0, 11, 'Depart From Customer', style1)
        sheet2.write(0, 12, 'Arrival To Terminal', style1)
        sheet2.write(0, 13, 'Detention Date', style1)
        sheet2.write(0, 14, 'EIR Date', style1)
        sheet2.write(0, 15, 'Shipment Status', style1)

        row = 1
        for rec in terminal_sea:
            if rec.sales_imp_id:
                sheet2.write(row, 0, rec.sales_imp_id.job_no or "", style0)
                sheet2.write(row, 1, rec.partner_id.name or "", style0)
                sheet2.write(row, 2, rec.sales_imp_id.port.name or "", style0)
                sheet2.write(row, 3, rec.sales_imp_id.bill_no or "", style0)
                sheet2.write(row, 4, rec.container_num or "", style0)
                sheet2.write(row, 5, rec.sales_imp_id.vsl_exp_arvl_date or "", style0)
                sheet2.write(row, 6, rec.sales_imp_id.org_date or "", style0)
                sheet2.write(row, 7, rec.sales_imp_id.demurrage or "", style0)
                sheet2.write(row, 8, rec.sales_imp_id.saddad or "", style0)
                sheet2.write(row, 9, rec.pullout_date or "", style0)
                sheet2.write(row, 10, rec.delivery_date or "", style0)
                sheet2.write(row, 11, rec.upload_date or "", style0)
                sheet2.write(row, 12, rec.return_date or "", style0)
                sheet2.write(row, 13, rec.sales_imp_id.detention_date or "", style0)
                sheet2.write(row, 14, rec.eir_date or "", style0)
                sheet2.write(row, 15, rec.sales_imp_id.status.name or "", style0)
                row += 1

        workbook.save('/tmp/import_shipment_status.xls')
        result_file = open('/tmp/import_shipment_status.xls', 'rb').read()
        attach_id = self.env['wizard.excel.report'].create({
            'name': 'Import Shipment Status.xls',
            'report': base64.encodestring(result_file)
        })
        return {
            'name': _('Notification'),
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.excel.report',
            'res_id': attach_id.id,
            'data': None,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }


class WizardExcelReport(models.TransientModel):
    _name = "wizard.excel.report"

    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)

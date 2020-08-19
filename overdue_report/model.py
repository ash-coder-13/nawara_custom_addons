import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64


class XlsxReportoverdue(models.TransientModel):
    _name = 'overdue.report'

    date = fields.Date(default=date.today())
    name = fields.Char()
    file = fields.Binary('Download Report', )

    @api.multi
    def print_report(self):
        data = []
        rec = self.env['account.move'].search(
            [('type', '=', 'out_invoice'), ('state', 'in', ['draft','posted']), ('date_due', '<=', self.date)])
        for x in rec:
            if x.partner_id not in data:
                data.append(x.partner_id)

        self.xlsx_report(data)

    @api.multi
    def xlsx_report(self, input_records):
        with xlsxwriter.Workbook(config['data_dir'] + "/overdue_report.xlsx") as workbook:
            main_heading = workbook.add_format({
                "bold": 1,
                "border": 1,
                "align": 'center',
                "valign": 'vcenter',
                "font_color": 'white',
                "bg_color": '548235',
                'font_size': '10',
            })

            # Create a format to use in the merged range.
            merge_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size': '15',
                "font_color": 'white',
                'fg_color': '7030a0'})

            main_data = workbook.add_format({
                "align": 'center',
                "valign": 'vcenter',
                'font_size': '8',
            })

            merge_format.set_shrink()
            main_heading.set_text_justlast(1)
            main_data.set_border()
            worksheet = workbook.add_worksheet('Overdue Report')
            head_date = time.strftime('%d-%B-%Y', time.strptime(self.date, '%Y-%m-%d'))
            head = "Overdue Report" + '-' + str(head_date)
            for row in range(1, 1):
                worksheet.set_row(row, 3)
            worksheet.merge_range('A1:C1', head, merge_format)

            worksheet.set_column('B:B', 40)
            worksheet.set_column('A:A', 10)
            worksheet.set_column('C:C', 60)
            worksheet.write('A3', 'Sr #', main_heading)
            worksheet.write('B3', 'Customer Name', main_heading)
            worksheet.write('C3', 'Overdue (once exceeding the agreed credit limits)', main_heading)

            row = 3
            col = 0
            records = input_records

            amounttotal = 0
            sr = 1
            for x in records:
                worksheet.write_string(row, col, str(sr), main_data)
                worksheet.write_string(row, col + 1, unicode(x.name), main_data)

                def get_amount(attr):
                    value = 0
                    invoices = self.env['account.move'].search(
                        [('type', '=', 'out_invoice'), ('state', 'in', ['draft','posted']), ('partner_id.id', '=', attr),
                         ('date_due', '<=', self.date)])
                    for z in invoices:
                        if z.partner_id.property_payment_term_id:
                            payment_day = z.partner_id.property_payment_term_id.line_ids.days
                        else:
                            payment_day = 0
                        if z.date_invoice:
                            start_date = datetime.datetime.strptime(z.date_invoice, "%Y-%m-%d")
                            new_date = start_date + timedelta(days=payment_day + 10)
                            end_date = datetime.datetime.strptime(self.date, "%Y-%m-%d")
                            if new_date < end_date:
                                value = value + z.residual

                    return value

                worksheet.write_string(row, col + 2, str(get_amount(x.id)), main_data)

                amounttotal = amounttotal + get_amount(x.id)
                sr += 1
                row += 1

            loc = 'A' + str(row + 1)
            loc1 = 'B' + str(row + 1)
            loc2 = 'C' + str(row + 1)
            end_loc = str(loc) + ':' + str(loc1)
            worksheet.merge_range(str(end_loc), 'Total', main_heading)
            worksheet.write_string(str(loc2), str(amounttotal), main_heading)

    def get_report(self):
        self.print_report()
        data_file = open(config['data_dir'] + "/overdue_report.xlsx", "rb")
        out = data_file.read()
        data_file.close()
        self.name = 'Overdue Report' + ' ' + self.date + ' ' + '.xlsx'
        self.file = base64.b64encode(out)
        return {
            "type": "ir.actions.do_nothing",
        }

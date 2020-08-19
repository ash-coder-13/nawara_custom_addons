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


class XlsxReportstatement(models.TransientModel):
    _name = 'statement.invoices'

    partner = fields.Many2one('res.partner', string="Customer", required=True)
    form = fields.Date("From")
    to = fields.Date("To")
    date = fields.Date(default=date.today())
    name = fields.Char()
    file = fields.Binary('Download Report', )

    @api.multi
    def print_report(self):
        data = self.env['account.move'].search(
            [('partner_id', '=', self.partner.id), ('type', '=', 'out_invoice'), ('state', 'in', ['draft','posted']),
             ('invoice_date', '>=', self.form), ('invoice_date', '<=', self.to)])
        data = sorted(data, key=lambda k: (k['date_invoice']))
        self.xlsx_report(data)

    @api.multi
    def xlsx_report(self, input_records):
        with xlsxwriter.Workbook(config['data_dir'] + "/statement_of_invoices.xlsx") as workbook:
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
                'font_size': '16',
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
            worksheet = workbook.add_worksheet('Statement of Accounts (Nawara)')

            head = "SOA (Nawara) OF" + ' ' + str(self.partner.name) + ' ' + "FROM" + ' ' + str(
                self.form) + ' ' + "TO" + ' ' + str(self.to)
            for row in range(1, 1):
                worksheet.set_row(row, 7)
            worksheet.merge_range('A1:G1', head, merge_format)

            worksheet.set_column('B:F', 18)
            worksheet.set_column('A:A', 10)
            worksheet.set_column('G:G', 28)
            worksheet.write('A3', 'Date', main_heading)
            worksheet.write('B3', 'Invoice No.', main_heading)
            worksheet.write('C3', 'Invoice Total', main_heading)
            worksheet.write('D3', 'Paid', main_heading)
            worksheet.write('E3', 'Remaining', main_heading)
            worksheet.write('F3', 'Age of Invoice', main_heading)
            worksheet.write('G3', 'BL Number/ Reference Number', main_heading)

            row = 3
            col = 0
            records = input_records

            # def get_age(attr):
            #     delta = 0
            #     for i in records:
            #         print i.id
            #         print attr
            #         print "================"
            #         if i.id == attr:
            #             mdate1 = datetime.datetime.strptime(self.date, "%Y-%m-%d")
            #             rdate1 = datetime.datetime.strptime(i.date_invoice, "%Y-%m-%d")
            #             delta =  (mdate1 - rdate1).days

            #         return delta

            for x in records:
                worksheet.write_string(row, col, str(x.date_invoice), main_data)
                worksheet.write_string(row, col + 1, str(x.number), main_data)
                worksheet.write_string(row, col + 2, str(x.amount_total), main_data)
                worksheet.write_string(row, col + 3, str(x.amount_total - x.residual), main_data)
                worksheet.write_string(row, col + 4, str(x.residual), main_data)

                def get_age(attr):
                    delta = 0
                    if x.id == attr:
                        mdate1 = datetime.datetime.strptime(self.date, "%Y-%m-%d")
                        rdate1 = datetime.datetime.strptime(x.date_invoice, "%Y-%m-%d")
                        delta = (mdate1 - rdate1).days

                    return delta

                worksheet.write_string(row, col + 5, str(get_age(x.id)), main_data)
                if x.bayan_no:
                    bayan = x.bayan_no
                else:
                    bayan = ""
                if x.customer_ref:
                    ref = x.customer_ref
                else:
                    ref = ""
                worksheet.write_string(row, col + 6, str(bayan + '   ' + ref), main_data)

                row += 1

    def get_report(self):
        self.print_report()
        data_file = open(config['data_dir'] + "/statement_of_invoices.xlsx", "rb")
        out = data_file.read()
        data_file.close()
        self.name = 'Statement of Accounts (Nawara) For ' + self.partner.name + '.xlsx'
        self.file = base64.b64encode(out)
        return {
            "type": "ir.actions.do_nothing",
        }

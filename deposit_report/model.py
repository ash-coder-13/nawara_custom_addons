import xlsxwriter
from odoo import models, fields, api
from odoo.tools import config
import base64
import string


class ContainerDepositReport(models.TransientModel):
    _name = 'deposit.report'

    form = fields.Date("From")
    to = fields.Date("To")
    name = fields.Char('Deposit Report')
    m_name = fields.Char()
    total = fields.Boolean("All Deposits", default=True)
    file = fields.Binary('Download Report', )

    @api.onchange('total')
    def onchange_total(self):
        if self.total:
            self.form = self.to = ''

    def print_report(self):
        if not self.total:
            data = self.env[self.m_name].search([('date', '>=', self.form), ('date', '<=', self.to)])
        if self.total:
            data = self.env[self.m_name].search([])
        self.xlsx_report(data)

    def report_name(self):
        if self.m_name == 'import.logic':
            if self.total:
                return 'Import Deposit Report.xlsx'
            if not self.total:
                return 'Import Deposit Report From {0} To {1}.xlsx'.format(str(self.form), str(self.to))
        if self.m_name == 'export.logic':
            if self.total:
                return 'Export Deposit Report.xlsx'
            if not self.total:
                return 'Export Deposit Report From {0} To {1}.xlsx'.format(str(self.form), str(self.to))

    def xlsx_report(self, data):
        with xlsxwriter.Workbook(config['data_dir'] + '/' + self.report_name()) as workbook:
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
            merge_format1 = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size': '13',
                "font_color": 'black',
                'fg_color': 'dcdcf8'})

            merge_format.set_shrink()
            main_heading.set_text_justlast(1)
            main_data.set_border()
            worksheet = workbook.add_worksheet('Deposit Report Master')
            worksheet.set_default_row(18)

            for row in range(1, 2):
                worksheet.set_row(row, 10)
            if self.total:
                worksheet.merge_range('A1:H2', 'All Deposit Report', merge_format)
            if not self.total:
                worksheet.merge_range('A1:H2', 'Deposit Report From {0} To {1}'.format(str(self.form), str(self.to)),
                                      merge_format)

            worksheet.set_column('A3:A', 4)
            worksheet.set_column('B3:G3', 14)

            worksheet.write('A3', 'No#', main_heading)
            worksheet.write('B3', 'Customer', main_heading)
            worksheet.write('C3', 'Payment Date', main_heading)
            worksheet.write('D3', 'BL#', main_heading)
            worksheet.write('E3', 'Container#', main_heading)
            worksheet.write('F3', 'Deposit Amount', main_heading)
            worksheet.write('G3', 'Status', main_heading)
            worksheet.write('H3', 'EIR Date', main_heading)
            row = 3
            col = 0

            def check_false(input_data):
                if input_data:
                    return input_data
                else:
                    return ' '

            total_amount = 0.0
            for x in data:
                if self.m_name == 'import.logic' and len(x.import_id) > 1:
                    C_range = 'D' + str(row + 1) + ':D' + str(row + len(x.import_id))
                    print(C_range, row, len(x.import_id))
                    worksheet.merge_range(C_range, str(check_false(x.bill_no)), main_data)
                else:
                    worksheet.write_string(row, col + 3, str(check_false(x.bill_no)), main_data)
                if self.m_name == 'import.logic':
                    for r in x.import_id:
                        total_amount += r.amount
                        worksheet.write_number(row, col, row - 2, main_data)
                        worksheet.write_string(row, col + 1, str(x.customer.name), main_data)
                        worksheet.write_string(row, col + 2, str(check_false(r.p_date)), main_data)
                        worksheet.write_string(row, col + 4, str(check_false(r.crt_no)), main_data)
                        worksheet.write_string(row, col + 5, str(check_false(r.amount)), main_data)
                        worksheet.write_string(row, col + 6, str(check_false(r.status)), main_data)
                        worksheet.write_string(row, col + 7, str(check_false(r.e_date)), main_data)
                        row += 1

                if self.m_name == 'export.logic' and len(x.export_id) > 1:
                    C_range = 'D' + str(row + 1) + ':D' + str(row + len(x.export_id))
                    print(C_range, row, len(x.export_id))
                    worksheet.merge_range(C_range, str(check_false(x.bill_no)), main_data)
                else:
                    worksheet.write_string(row, col + 3, str(check_false(x.bill_no)), main_data)
                if self.m_name == 'export.logic':
                    for r in x.export_id:
                        total_amount += r.amount
                        worksheet.write_number(row, col, row - 2, main_data)
                        worksheet.write_string(row, col + 1, str(x.customer.name), main_data)
                        worksheet.write_string(row, col + 2, str(check_false(r.p_date)), main_data)
                        worksheet.write_string(row, col + 4, str(check_false(r.crt_no)), main_data)
                        worksheet.write_string(row, col + 5, str(check_false(r.amount)), main_data)
                        worksheet.write_string(row, col + 6, str(check_false(r.status)), main_data)
                        worksheet.write_string(row, col + 7, str(check_false(r.e_date)), main_data)
                        row += 1

            for abc in range(1):
                worksheet.set_row(abc, 20)
                rRange = 'A' + str(row + 1) + ':' + 'E' + str(row + 1)
                worksheet.merge_range(rRange, 'Total', merge_format)
            worksheet.write_string(row, col + 5, str(check_false(total_amount)), merge_format)
            for abc in range(1):
                worksheet.set_row(abc, 20)
                rRange = 'G' + str(row + 1) + ':' + 'H' + str(row + 1)
                worksheet.merge_range(rRange, ' ', merge_format)

            #   Summary
            #   Report

            worksheet_s = workbook.add_worksheet('Deposit Report Summary')
            worksheet_s.set_default_row(18)

            for row in range(1, 2):
                worksheet_s.set_row(row, 10)
            if self.total:
                worksheet_s.merge_range('A1:F2', 'All Deposit Report Summary', merge_format)
            if not self.total:
                worksheet_s.merge_range('A1:F2', 'Deposit Report Summary From {0} To {1}'.format(str(self.form),
                                                                                                 str(self.to)),
                                        merge_format)

            worksheet_s.set_column('A3:A3', 4)
            worksheet_s.set_column('B3:F3', 14)
            worksheet_s.write('A3', 'No#', main_heading)
            worksheet_s.write('B3', 'Customer', main_heading)
            worksheet_s.write('C3', 'Refunded', main_heading)
            worksheet_s.write('D3', 'Under Refunding', main_heading)
            worksheet_s.write('E3', 'Waiting EIR', main_heading)
            worksheet_s.write('F3', 'Grand Total', main_heading)

            customers = data.read_group(domain=[], fields=['customer'], groupby=['customer'])
            customers = [c['customer'][0] for c in customers]
            row = 3
            col = 0
            grf = guf = gwa = ggt = 0.0
            for customer in customers:
                rf = uf = wa = gt = 0.0
                if self.total:
                    customer_data = self.env[self.m_name].search([('customer', '=', customer)])
                if not self.total:
                    customer_data = self.env[self.m_name].search([('customer', '=', customer), ('date', '>=', self.form)
                                                                     , ('date', '<=', self.to)])
                if self.m_name == 'import.logic':
                    for rec in customer_data:
                        for r in rec.import_id:
                            if r.status == 'Waiting EIR':
                                wa = wa + r.amount
                            if r.status == 'Under Refunding':
                                uf = uf + r.amount
                            if r.status == 'Refunded':
                                rf = rf + r.amount
                        gt = rf + uf + wa
                if self.m_name == 'export.logic':
                    for rec in customer_data:
                        for r in rec.export_id:
                            if r.status == 'Waiting EIR':
                                wa = wa + r.amount
                            if r.status == 'Under Refunding':
                                uf = uf + r.amount
                            if r.status == 'Refunded':
                                rf = rf + r.amount
                        gt = rf + uf + wa
                if customer_data:
                    worksheet_s.write_string(row, col, str(row - 2), main_data)
                    worksheet_s.write_string(row, col + 1, str(check_false(customer_data[0][0].customer.name)),
                                             main_data)
                    worksheet_s.write_string(row, col + 2, str(check_false(rf)), main_data)
                    worksheet_s.write_string(row, col + 3, str(check_false(uf)), main_data)
                    worksheet_s.write_string(row, col + 4, str(check_false(wa)), main_data)
                    worksheet_s.write_string(row, col + 5, str(check_false(gt)), main_data)
                    row += 1
                    gwa += wa
                    grf += rf
                    guf += uf
                    ggt += gt

            if (grf + guf + gwa + ggt) > 0:
                for abc in range(1):
                    worksheet_s.set_row(abc, 20)
                    rRange = 'A' + str(row + 1) + ':' + 'B' + str(row + 1)
                    worksheet_s.merge_range(rRange, 'Grand Total', merge_format)
                worksheet_s.write_string(row, col + 2, str(check_false(grf)), merge_format)
                worksheet_s.write_string(row, col + 3, str(check_false(guf)), merge_format)
                worksheet_s.write_string(row, col + 4, str(check_false(gwa)), merge_format)
                worksheet_s.write_string(row, col + 5, str(check_false(ggt)), merge_format)

    def get_report(self):
        self.print_report()
        data_file = open(config['data_dir'] + '/' + self.report_name(), "rb")
        out = data_file.read()
        data_file.close()
        self.name = self.report_name()
        self.file = base64.b64encode(out)
        return {
            "type": "ir.actions.do_nothing",
        }

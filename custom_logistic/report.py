import os
import xlsxwriter
from datetime import datetime, date
from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64


class XlsxReport(models.Model):
    _name = 'xl.report'
    _rec_name = 'customer'

    customer = fields.Many2one('res.partner', string="Customer", required=True)
    s_date = fields.Date("Start Date")
    e_date = fields.Date("End Date")
    ttype = fields.Selection([
        ('export', 'Export'),
        ('import', 'Import'),
    ], default='export', string="Report Type", required=True)
    total = fields.Boolean("Total Report", default=False)
    b_name = fields.Many2one('by.customer', "By Customer")
    site = fields.Many2one(comodel_name="import.site", string="Site", required=True, )

    name = fields.Char()
    file = fields.Binary('Download Report', )

    @api.onchange('total')
    def onchange_total(self):
        if self.total:
            self.s_date = self.e_date = ''

    @api.onchange('customer')
    def onchange_customer(self):
        if not self.customer.by_customer:
            self.b_name = ''

    def print_report(self):
        for rec in self:
            if rec.total:
                if rec.ttype == 'export':
                    data = self.env['export.logic'].search(
                        [('customer', '=', rec.customer.id), ('by_customer', '=', rec.b_name.id),
                         ('site', '=', rec.site.id)])
                    if data:
                        return rec.xlsx_report(data, ttype='export')
                    else:
                        raise ValidationError('Report Does Not Exist According To Given Data')
                elif rec.ttype == 'import':
                    data = self.env['import.logic'].search(
                        [('customer', '=', rec.customer.id), ('by_customer', '=', rec.b_name.id),
                         ('site', '=', rec.site.id)])
                    if data:
                        return rec.xlsx_report(data, ttype='import')
                    else:
                        raise ValidationError('Report Does Not Exist According To Given Data')
                else:
                    raise ValidationError('Report Does Not Exist According To Given Data')
            else:
                if rec.ttype == 'export' and rec.e_date and rec.s_date:
                    data = self.env['export.logic'].search(
                        [('customer', '=', rec.customer.id), ('by_customer', '=', rec.b_name.id),
                         ('date', '>=', rec.s_date), ('date', '<=', rec.e_date), ('site', '=', rec.site.id)])
                    if data:
                        return rec.xlsx_report(data, ttype='export')
                    else:
                        raise ValidationError('Report Does Not Exist According To Given Data')

                elif rec.ttype == 'import' and rec.e_date and rec.s_date:
                    data = self.env['import.logic'].search(
                        [('customer', '=', rec.customer.id), ('by_customer', '=', rec.b_name.id),
                         ('date', '>=', rec.s_date), ('date', '<=', rec.e_date), ('site', '=', rec.site.id)])
                    if data:
                        return rec.xlsx_report(data, ttype='import')
                    else:
                        raise ValidationError('Report Does Not Exist According To Given Data')
                else:
                    raise ValidationError('Report Does Not Exist According To Given Data')

    def xlsx_report(self, input_records, ttype):
        with xlsxwriter.Workbook(config['data_dir'] + "/SHIPMENT_STATUS_REPORT.xlsx") \
                as workbook:
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
                'align': 'left',
                'valign': 'vcenter',
                'font_size': '13',
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
            worksheet = workbook.add_worksheet(self.customer.name)

            for row in range(1, 2):
                worksheet.set_row(row, 33)
            worksheet.merge_range('A1:AL2', 'SHIPMENT STATUS REPORT  {0} {1} {2}'.format(str(date.today())
                                                                                         , str(self.customer.name),
                                                                                         (str(self.b_name.name) if self.b_name else '')),
                                  merge_format)

            worksheet.set_column('A3:A3', 4)
            worksheet.set_column('B3:C3', 6)
            worksheet.set_column('D3:AL3', 10)

            worksheet.write('A3', 'No', main_heading)
            worksheet.write('B3', 'SR. no.', main_heading)
            worksheet.write('C3', 'Our Job No', main_heading)
            worksheet.write('D3', 'Customer Name', main_heading)
            worksheet.write('E3', 'Order No.', main_heading)
            worksheet.write('F3', 'Customer Ref Inv No.', main_heading)
            worksheet.write('G3', 'Shipment Received Date', main_heading)
            worksheet.write('H3', 'B/L Number', main_heading)
            worksheet.merge_range('I3:J3', 'Number Of Containers', main_heading)
            worksheet.write('K3', 'Terminal', main_heading)
            worksheet.write('L3', 'Shipping Line', main_heading)
            worksheet.write('M3', 'Vessel Name', main_heading)
            worksheet.merge_range('N3:O3', 'ETA', main_heading)
            worksheet.write('P3', 'CC Days', main_heading)
            worksheet.write('Q3', 'Manifest documents Received Date', main_heading)
            worksheet.write('R3', 'Bayan NO.', main_heading)
            worksheet.write('S3', 'Rotation NO.', main_heading)
            worksheet.write('T3', 'Initial Bayan Date', main_heading)
            worksheet.write('U3', 'Pre-Bayan', main_heading)
            worksheet.write('V3', 'Manifest to Initial Bayan Printed', main_heading)
            worksheet.write('W3', 'Initial Bayan to Pre Bayan Printed', main_heading)
            worksheet.merge_range('X3:Y3', 'Shuttling', main_heading)
            worksheet.write('Z3', 'Final Bayan Date', main_heading)
            worksheet.write('AA3', 'Shuttle to final bayan', main_heading)
            worksheet.write('AB3', 'Random Inspection', main_heading)
            worksheet.write('AC3', 'Custom Exam Of Containers no.', main_heading)
            worksheet.write('AD3', 'New Seal no.', main_heading)
            worksheet.write('AE3', 'Load Permit Printed On', main_heading)
            worksheet.merge_range('AF3:AI3', 'Total Expenses', main_heading)
            worksheet.write('AJ3', 'Status', main_heading)
            worksheet.write('AK3', 'Remarks', main_heading)
            worksheet.write('AL3', 'Reason for the delay (Shutout) (If any)', main_heading)
            worksheet.write('A4', ' ', main_heading)
            worksheet.write('B4', ' ', main_heading)
            worksheet.write('C4', ' ', main_heading)
            worksheet.write('D4', ' ', main_heading)
            worksheet.write('E4', ' ', main_heading)
            worksheet.write('F4', ' ', main_heading)
            worksheet.write('G4', ' ', main_heading)
            worksheet.write('H4', ' ', main_heading)
            worksheet.write('I4', '20ft', main_heading)
            worksheet.write('J4', '40ft', main_heading)
            worksheet.write('K4', ' ', main_heading)
            worksheet.write('L4', ' ', main_heading)
            worksheet.write('M4', ' ', main_heading)
            worksheet.write('N4', 'On or About', main_heading)
            worksheet.write('O4', 'Revised ETA Date', main_heading)
            worksheet.write('P4', ' ', main_heading)
            worksheet.write('Q4', ' ', main_heading)
            worksheet.write('R4', ' ', main_heading)
            worksheet.write('S4', ' ', main_heading)
            worksheet.write('T4', ' ', main_heading)
            worksheet.write('U4', ' ', main_heading)
            worksheet.write('V4', ' ', main_heading)
            worksheet.write('W4', ' ', main_heading)
            worksheet.write('X4', 'Start Date', main_heading)
            worksheet.write('Y4', 'End Date', main_heading)
            worksheet.write('Z4', ' ', main_heading)
            worksheet.write('AA4', ' ', main_heading)
            worksheet.write('AB4', ' ', main_heading)
            worksheet.write('AC4', ' ', main_heading)
            worksheet.write('AD4', ' ', main_heading)
            worksheet.write('AE4', ' ', main_heading)
            worksheet.write('AF4', 'Custom Duty', main_heading)
            worksheet.write('AG4', 'Inspection', main_heading)
            worksheet.write('AH4', 'Container Seal', main_heading)
            worksheet.write('AI4', 'Total', main_heading)
            worksheet.write('AJ4', ' ', main_heading)
            worksheet.write('AK4', ' ', main_heading)
            worksheet.write('AL4', ' ', main_heading)

            row = 4
            col = 0
            records = input_records

            def check_false(data):
                if data:
                    return data
                else:
                    return ' '

            if ttype == 'export':
                for i, x in enumerate(records):
                    worksheet.write_string(row, col, str(i + 1), main_data)
                    worksheet.write_string(row, col + 1, str(check_false(x.sr_no)), main_data)
                    worksheet.write_string(row, col + 2, str(check_false(x.our_job_no)), main_data)
                    worksheet.write_string(row, col + 3, str(check_false(x.customer.name)), main_data)
                    worksheet.write_string(row, col + 4, str(check_false(x.customer_ref)), main_data)
                    worksheet.write_string(row, col + 5, str(check_false(x.cust_ref_inv)), main_data)
                    worksheet.write_string(row, col + 6, str(check_false(x.shipper_date)), main_data)
                    worksheet.write_string(row, col + 7, str(check_false(x.bill_no)), main_data)

                    def ft20(line):
                        count = 0
                        for x in line:
                            if x.types == '20 ft':
                                count = count + 1
                        return count

                    def ft40(line):
                        count = 0
                        for x in line:
                            if x.types == '40 ft':
                                count = count + 1
                        return count

                    worksheet.write_string(row, col + 8, str(check_false(ft20(x.export_id))), main_data)
                    worksheet.write_string(row, col + 9, str(check_false(ft40(x.export_id))), main_data)
                    worksheet.write_string(row, col + 10, ' - ', main_data)
                    worksheet.write_string(row, col + 11, str(check_false(x.s_supplier.name)), main_data)
                    worksheet.write_string(row, col + 12, str(check_false(x.vessel_name)), main_data)
                    worksheet.write_string(row, col + 13, str(check_false(x.vessel_date)), main_data)
                    worksheet.write_string(row, col + 14, str(check_false(x.eta)), main_data)
                    if x.vessel_date and x.shipper_date:
                        k_e = (datetime.date(datetime.strptime(x.vessel_date, '%Y-%m-%d')) - datetime.date(
                            datetime.strptime(x.shipper_date, '%Y-%m-%d'))).days
                    else:
                        k_e = ''
                    worksheet.write_string(row, col + 15, str(k_e), main_data)
                    worksheet.write_string(row, col + 16, str(check_false(x.mani_date)), main_data)
                    worksheet.write_string(row, col + 17, str(check_false(x.bayan_no)), main_data)
                    worksheet.write_string(row, col + 18, str(check_false(x.rot_no)), main_data)
                    worksheet.write_string(row, col + 19, str(check_false(x.bayan_date)), main_data)
                    worksheet.write_string(row, col + 20, str(check_false(x.pre_bayan)), main_data)
                    if x.pre_bayan and x.mani_date:
                        r_o = (datetime.date(datetime.strptime(x.pre_bayan, '%Y-%m-%d')) - datetime.date(
                            datetime.strptime(x.mani_date, '%Y-%m-%d'))).days
                    else:
                        r_o = ''
                    worksheet.write_string(row, col + 21, str(r_o), main_data)
                    if x.pre_bayan and x.bayan_date:
                        s_r = (datetime.date(datetime.strptime(x.pre_bayan, '%Y-%m-%d')) - datetime.date(
                            datetime.strptime(x.bayan_date, '%Y-%m-%d'))).days
                    else:
                        s_r = ''
                    worksheet.write_string(row, col + 22, str(s_r), main_data)
                    worksheet.write_string(row, col + 23, str(check_false(x.shutl_start_date)), main_data)
                    worksheet.write_string(row, col + 24, str(check_false(x.shutl_end_date)), main_data)
                    worksheet.write_string(row, col + 25, str(check_false(x.fin_bayan_date)), main_data)
                    if x.fin_bayan_date and x.shutl_start_date:
                        x_v = (datetime.date(datetime.strptime(x.fin_bayan_date, '%Y-%m-%d')) - datetime.date(
                            datetime.strptime(x.shutl_start_date, '%Y-%m-%d'))).days
                    else:
                        x_v = ''
                    worksheet.write_string(row, col + 26, str(x_v), main_data)
                    worksheet.write_string(row, col + 27, ' ', main_data)

                    if x.custom_exam == True and x.export_link:
                        worksheet.write_string(row, col + 28, str(check_false(x.export_link.container_no)), main_data)
                        worksheet.write_string(row, col + 29, str(check_false(x.export_link.new_seal)), main_data)
                    else:
                        worksheet.write_string(row, col + 28, str(' '), main_data)
                        worksheet.write_string(row, col + 29, str(' '), main_data)

                    worksheet.write_string(row, col + 30, ' ', main_data)
                    if x.custom_exam:
                        for y, z in [(y, z) for y in x.export_id for z in x.export_link]:
                            if y.crt_no == z.container_no:
                                worksheet.write_string(row, col + 31, ' N/A', main_data)
                                worksheet.write_string(row, col + 32, ' N/A', main_data)
                                worksheet.write_string(row, col + 33, str(check_false(z.new_seal)), main_data)
                                worksheet.write_string(row, col + 34, str(check_false(z.amt_paid)), main_data)
                            else:
                                worksheet.write_string(row, col + 31, ' * ', main_data)
                                worksheet.write_string(row, col + 32, ' * ', main_data)
                                worksheet.write_string(row, col + 33, ' * ', main_data)
                                worksheet.write_string(row, col + 34, ' * ', main_data)
                    else:
                        worksheet.write_string(row, col + 31, ' / ', main_data)
                        worksheet.write_string(row, col + 32, ' / ', main_data)
                        worksheet.write_string(row, col + 33, ' / ', main_data)
                        worksheet.write_string(row, col + 34, ' / ', main_data)

                    worksheet.write_string(row, col + 35, str(check_false(x.status.comment)), main_data)
                    worksheet.write_string(row, col + 36, str(check_false(x.remarks)), main_data)
                    worksheet.write_string(row, col + 37, ' ', main_data)

                    row += 1

            elif ttype == 'import':
                for i, x in enumerate(records):
                    worksheet.write_string(row, col, str(i + 1), main_data)
                    worksheet.write_string(row, col + 1, str(check_false(x.s_no)), main_data)
                    worksheet.write_string(row, col + 2, str(check_false('/')), main_data)
                    worksheet.write_string(row, col + 3, str(check_false(x.customer.name)), main_data)
                    worksheet.write_string(row, col + 4, str(check_false(x.job_no)), main_data)
                    worksheet.write_string(row, col + 5, str(check_false(x.cust_ref_inv)), main_data)
                    worksheet.write_string(row, col + 6, str(check_false(x.shipper_date)), main_data)
                    worksheet.write_string(row, col + 7, str(check_false(x.bill_no)), main_data)

                    def ft20(line):
                        count = 0
                        for x in line:
                            if x.types == '20 ft':
                                count = count + 1
                        return count

                    def ft40(line):
                        count = 0
                        for x in line:
                            if x.types == '40 ft':
                                count = count + 1
                        return count

                    worksheet.write_string(row, col + 8, str(check_false(ft20(x.import_id))), main_data)
                    worksheet.write_string(row, col + 9, str(check_false(ft40(x.import_id))), main_data)
                    worksheet.write_string(row, col + 10, ' - ', main_data)
                    worksheet.write_string(row, col + 11, str(check_false(x.s_supplier.name)), main_data)
                    worksheet.write_string(row, col + 12, str(check_false(x.vessel_name)), main_data)
                    worksheet.write_string(row, col + 13, str(check_false(x.vessel_date)), main_data)
                    worksheet.write_string(row, col + 14, str(check_false(date.today())), main_data)
                    if x.vessel_date and x.shipper_date:
                        k_e = (datetime.date(datetime.strptime(x.vessel_date, '%Y-%m-%d')) - datetime.date(
                            datetime.strptime(x.shipper_date, '%Y-%m-%d'))).days
                    else:
                        k_e = ''
                    worksheet.write_string(row, col + 15, str(k_e), main_data)
                    worksheet.write_string(row, col + 16, ' N/A', main_data)
                    worksheet.write_string(row, col + 17, str(check_false(x.bayan_no)), main_data)
                    worksheet.write_string(row, col + 18, str(check_false(x.rot_no)), main_data)
                    worksheet.write_string(row, col + 19, str(check_false(x.bayan_date)), main_data)
                    worksheet.write_string(row, col + 20, 'N/A', main_data)
                    worksheet.write_string(row, col + 21, 'N/A', main_data)
                    worksheet.write_string(row, col + 22, 'N/A', main_data)
                    worksheet.write_string(row, col + 23, 'N/A', main_data)
                    worksheet.write_string(row, col + 24, 'N/A', main_data)
                    worksheet.write_string(row, col + 25, 'N/A', main_data)
                    worksheet.write_string(row, col + 26, ' ', main_data)
                    worksheet.write_string(row, col + 27, 'N/A', main_data)
                    worksheet.write_string(row, col + 28, ' - ', main_data)
                    worksheet.write_string(row, col + 29, ' ', main_data)
                    worksheet.write_string(row, col + 30, '  ', main_data)
                    worksheet.write_string(row, col + 31, '  ', main_data)
                    worksheet.write_string(row, col + 32, '  ', main_data)
                    worksheet.write_string(row, col + 33, '  ', main_data)
                    worksheet.write_string(row, col + 34, str(check_false(x.status.comment)), main_data)
                    worksheet.write_string(row, col + 35, str(check_false(x.remarks)), main_data)
                    worksheet.write_string(row, col + 36, ' ', main_data)
                    worksheet.write_string(row, col + 37, ' ', main_data)

                    row += 1

    def get_report(self):
        self.print_report()
        data_file = open(config['data_dir'] + "/SHIPMENT_STATUS_REPORT.xlsx", "rb")
        out = data_file.read()
        data_file.close()
        self.name = 'SHIPMENT STATUS REPORT - {0} - {1} {2} {3}'.format(str(self.ttype).upper(),
                                                                        str(date.today()), str(self.customer.name),
                                                                        (str(self.b_name.name) if self.b_name else ' '))\
                    + '.xlsx'
        self.file = base64.b64encode(out)
        return {
            "type": "ir.actions.do_nothing",
        }

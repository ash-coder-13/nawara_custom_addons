import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
from odoo import models, fields, api
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64
import string
import sys



class XlsxReportstatement(models.TransientModel):
    _name = 'salary.sheet'


    batch = fields.Many2one('hr.payslip.run',string="Payslip Batch",required=True)
    name = fields.Char()
    file = fields.Binary('Download Report',)
   

    @api.multi
    def print_report(self):

        data=self.batch.slip_ids
        if data:
            self.xlsx_report(data)
        else:
            raise  ValidationError('Report Does Not Exist According To Given Data')
            


    @api.multi
    def xlsx_report(self,input_records):
        with xlsxwriter.Workbook(config['data_dir']+"/salary_sheet.xlsx") as workbook:
        
            main_heading = workbook.add_format({
                "bold": 1, 
                "border": 1,
                "align": 'center',
                "valign": 'vcenter',
                "font_color":'white',
                "bg_color": '548235',
                'font_size': '10',
                })

            # Create a format to use in the merged range.
            merge_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size': '12',
                "font_color":'white',
                'fg_color': '7030a0'})

            main_data = workbook.add_format({
                "align": 'center',
                "valign": 'vcenter',
                'font_size': '8',
                })
            merge_format.set_shrink()
            main_heading.set_text_justlast(1)
            # main_data.set_border()
            worksheet = workbook.add_worksheet('Salary Sheet')

            head = "Statement of salaries of employees for" +' '+ str(self.batch.name)
            for row in range(1, 1):
                worksheet.set_row(row, 7)
            worksheet.merge_range('AA1:A1', head,merge_format)

            # worksheet.set_column('A:A', 10)
            # worksheet.set_column('G:G', 28)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('W:AA', 15)
            worksheet.set_column('H:Q', 15)
            worksheet.write('AA2', 'Employee Name', main_heading)
            worksheet.write('Z2', 'Nationality', main_heading)
            worksheet.write('Y2', 'Job title',main_heading)
            worksheet.write('X2', 'Functional code',main_heading)
            worksheet.write('W2', 'Basic Salary',main_heading)
            worksheet.merge_range('U2:V2','Overtime',main_heading)
            worksheet.write('V3', 'Hour',main_heading)
            worksheet.write('U3', 'Time',main_heading)
            worksheet.merge_range('R2:T2','Absence',main_heading)
            worksheet.write('R3', 'Minute',main_heading)
            worksheet.write('S3', 'Hour',main_heading)
            worksheet.write('T3', 'Day',main_heading)
            worksheet.merge_range('H2:Q2','Allowances',main_heading)
            worksheet.write('H3', 'Total',main_heading)
            worksheet.write('I3', 'Overtime Amount',main_heading)
            worksheet.write('J3', 'Other',main_heading)
            worksheet.write('K3', 'Food',main_heading)
            worksheet.write('L3', 'Assignment',main_heading)
            worksheet.write('M3', 'Job of Title',main_heading)
            worksheet.write('N3', 'Telephone',main_heading)
            worksheet.write('O3', 'Housing',main_heading)
            worksheet.write('P3', 'Transportation',main_heading)
            worksheet.write('Q3', 'Basic Salary',main_heading)
            worksheet.merge_range('C2:G2','Deduction',main_heading)
            worksheet.write('C3', 'Total',main_heading)
            worksheet.write('D3', 'Other',main_heading)
            worksheet.write('E3', 'GOSI',main_heading)
            worksheet.write('F3', 'Absence',main_heading)
            worksheet.write('G3', 'Advance',main_heading)
            worksheet.write('B2', 'Net Receivable',main_heading)
            worksheet.write('A2', 'Notes',main_heading)


            row = 3
            col = 0
            records = input_records

            basic = 0
            trans = 0
            house = 0
            tele = 0
            job = 0
            assign = 0
            food = 0
            other = 0
            over = 0
            gosi = 0
            net = 0

            for x in records:
                # name = str(x.employee_id.name).encode('utf-8').strip()
                worksheet.write_string (row, col+26,'{0}'.decode('utf-8').format(x.employee_id.name),main_data)
                # worksheet.write_string (row, col+25,'{0}'.decode('utf-8').format(x.employee_id.ar_country_id),main_data)
                # worksheet.write_string (row, col+24,'{0}'.decode('utf-8').format(x.employee_id.ar_designation),main_data)
                # worksheet.write_string (row, col+23,'{0}'.decode('utf-8').format(x.employee_id.pin),main_data)
                def get_basic(attr):
                    contract = self.env['hr.contract'].search([('employee_id.id','=',attr)],limit=1)

                    return contract.wage

                def get_trans():
                    trans = 0
                    house = 0
                    tele = 0
                    job = 0
                    assign = 0
                    food = 0
                    other = 0
                    over = 0
                    gosi = 0
                    net = 0
                    for y in x.line_ids:
                        if y.code == 'Transportation Allowance Employee':
                            trans = y.total
                        if y.code == 'HouseRentAllowanceUnMaried' or y.code == 'HRAUNMARRIED01':
                            house = y.total
                        if y.code == 'Telephone Allowance' or y.code == 'Telephone Allowance 70SR':
                            tele = y.total
                        if y.code == 'Job Title Allowance':
                            job = y.total
                        if y.code == 'assign':
                            assign = y.total
                        if y.code == 'Food Allowance':
                            food = y.total
                        if y.code == 'other':
                            other = y.total
                        if y.code == 'overtime':
                            over = y.total
                        if y.code == 'EMPGOSI':
                            gosi = y.total
                        if y.code == 'NET':
                            net = y.total


                    return trans,house,tele,job,assign,food,other,over,gosi,net

                worksheet.write_string (row, col+22,str(get_basic(x.employee_id.id)),main_data)
                worksheet.write_string (row, col+15,str(get_trans()[0]),main_data)
                worksheet.write_string (row, col+14,str(get_trans()[1]),main_data)
                worksheet.write_string (row, col+13,str(get_trans()[2]),main_data)
                worksheet.write_string (row, col+12,str(get_trans()[3]),main_data)
                worksheet.write_string (row, col+11,str(get_trans()[4]),main_data)
                worksheet.write_string (row, col+10,str(get_trans()[5]),main_data)
                worksheet.write_string (row, col+9,str(get_trans()[6]),main_data)
                worksheet.write_string (row, col+8,str(get_trans()[7]),main_data)
                worksheet.write_string (row, col+4,str(get_trans()[8]),main_data)
                worksheet.write_string (row, col+4,str(get_trans()[8]),main_data)
                worksheet.write_string (row, col+1,str(get_trans()[9]),main_data)

                basic = basic + get_basic(x.employee_id.id)
                trans = trans + get_trans()[0]
                house = house + get_trans()[1]
                tele = tele + get_trans()[2]
                job = job + get_trans()[3]
                assign = assign + get_trans()[4]
                food = food + get_trans()[5]
                other = other + get_trans()[6]
                over = over + get_trans()[7]
                gosi = gosi + get_trans()[8]
                net = net + get_trans()[9]

                row += 1

            loc = 'X'+str(row+1)
            loc1 = 'AA'+str(row+1)
            end_loc = str(loc)+':'+str(loc1)
            worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
            locw = 'W'+str(row+1)
            worksheet.write_string(str(locw),str(basic),main_heading)
            locp = 'P'+str(row+1)
            worksheet.write_string(str(locp),str(trans),main_heading)
            loco = 'O'+str(row+1)
            worksheet.write_string(str(loco),str(house),main_heading)
            locn = 'N'+str(row+1)
            worksheet.write_string(str(locn),str(tele),main_heading)
            locm = 'M'+str(row+1)
            worksheet.write_string(str(locm),str(job),main_heading)
            locl = 'L'+str(row+1)
            worksheet.write_string(str(locl),str(assign),main_heading)
            lock = 'K'+str(row+1)
            worksheet.write_string(str(lock),str(food),main_heading)
            locj = 'J'+str(row+1)
            worksheet.write_string(str(locj),str(other),main_heading)
            loci = 'I'+str(row+1)
            worksheet.write_string(str(loci),str(over),main_heading)
            loce = 'E'+str(row+1)
            worksheet.write_string(str(loce),str(gosi),main_heading)
            locb = 'B'+str(row+1)
            worksheet.write_string(str(locb),str(net),main_heading)

            loceo = 'C'+str(row+4)
            loceo1 = 'D'+str(row+4)
            end_loceo = str(loceo)+':'+str(loceo1)
            worksheet.merge_range(str(end_loceo), 'CEO' ,main_heading)
            locHR = 'H'+str(row+4)
            locHR1 = 'I'+str(row+4)
            end_locHR = str(locHR)+':'+str(locHR1)
            worksheet.merge_range(str(end_locHR), 'HR Management' ,main_heading)
            locR = 'R'+str(row+4)
            locT = 'T'+str(row+4)
            end_locRT = str(locR)+':'+str(locT)
            worksheet.merge_range(str(end_locRT), 'Financial Management' ,main_heading)
            locX = 'X'+str(row+4)
            locY = 'Y'+str(row+4)
            end_locXY = str(locX)+':'+str(locY)
            worksheet.merge_range(str(end_locXY), 'Preparing' ,main_heading)


            
            

    def get_report(self):
        self.print_report()
        data_file = open(config['data_dir'] + "/salary_sheet.xlsx", "rb")
        out = data_file.read()
        data_file.close()
        self.name = 'Salary Sheet' +' '+ self.batch.name + ' '+'.xlsx'
        self.file = base64.b64encode(out)
        return {
        "type": "ir.actions.do_nothing",
        }

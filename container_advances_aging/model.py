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
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class XlsxReportoverdueAging(models.TransientModel):
    _name = 'container.aging'


    date = fields.Date(default=date.today(),required=True,string="Date")
    account_id = fields.Many2one('account.account',string="Parent Account",default=114)
    name = fields.Char()
    file = fields.Binary('Download Report',)
    filters = fields.Selection([
        ('all', 'All'),
        ('posted','Posted')], string='Filter',required=True)
   

    def print_report(self):

        acc = []
        accounts = self.env['account.account'].search([])
        for x in accounts:
            if x.parent_id.id == self.account_id.id:
                acc.append(x)

        self.xlsx_report(acc)


    def xlsx_report(self,input_records):
        with xlsxwriter.Workbook(config['data_dir']+"/container_advances_aging.xlsx") as workbook:
            main_heading = workbook.add_format({
                "bold": 1, 
                "border": 1,
                "align": 'center',
                "valign": 'vcenter',
                "font_color":'white',
                "bg_color": '548235',
                'font_size': '10',
                })

            main_heading1 = workbook.add_format({
                "bold": 1, 
                "border": 1,
                "align": 'center',
                "valign": 'vcenter',
                "font_color":'white',
                "bg_color": '7030a0',
                'font_size': '10',
                })

            main_heading2 = workbook.add_format({
                "bold": 1, 
                "border": 1,
                "align": 'center',
                "valign": 'vcenter',
                "font_color":'white',
                "bg_color": 'red',
                'font_size': '10',
                })

            # Create a format to use in the merged range.
            merge_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size': '13',
                "font_color":'white',
                'fg_color': '7030a0'})

            main_data = workbook.add_format({
                "align": 'center',
                "valign": 'vcenter',
                'font_size': '8',
                })
            merge_format.set_shrink()
            main_heading.set_text_justlast(1)
            main_data.set_border()
            worksheet = workbook.add_worksheet('Container Advances Aging')

            start_date = datetime.strptime(self.date,"%Y-%m-%d")
            less15 = start_date - relativedelta(days=15)
            less30 = start_date - relativedelta(days=30)
            less45 = start_date - relativedelta(days=45)
            less60 = start_date - relativedelta(days=60)
            less75 = start_date - relativedelta(days=75)
            less90 = start_date - relativedelta(days=90)


            head = 'Container Deposit Aging Report ('+' '+str(self.date)+' '+')'
            worksheet.merge_range('A1:I1', head,merge_format)
            worksheet.set_column('B:B', 45)
            worksheet.set_column('A:A', 10)
            worksheet.set_column('C:Q', 15)
            worksheet.write('A3', 'Code', main_heading)
            worksheet.write('B3', 'Account Name',main_heading)
            worksheet.write('C3', 'Balance',main_heading)
            # worksheet.write('D3', 'Debit Balance',main_heading1)
            worksheet.write('D3', 'Less Than 15',main_heading1)
            worksheet.write('E3', 'From 15 To 30',main_heading1)
            worksheet.write('F3', 'From 30 To 45',main_heading1)
            worksheet.write('G3', 'From 45 To 60',main_heading1)
            worksheet.write('H3', 'From 60 To 75',main_heading1)
            worksheet.write('I3', 'From 75 To 90',main_heading1)
            # worksheet.write('K3', 'Credit Balance',main_heading2)
            # worksheet.write('L3', 'Less Than 15',main_heading2)
            # worksheet.write('M3', 'From 15 To 30',main_heading2)
            # worksheet.write('N3', 'From 30 To 45',main_heading2)
            # worksheet.write('O3', 'From 45 To 60',main_heading2)
            # worksheet.write('P3', 'From 60 To 75',main_heading2)
            # worksheet.write('Q3', 'From 75 To 90',main_heading2)
            
            row = 3
            col = 0
            records = input_records

            debited = 0
            debited15 = 0
            debited30 = 0
            debited45 = 0
            debited60 = 0
            debited75 = 0
            debited90 = 0
            credited = 0
            credited15 = 0
            credited30 = 0
            credited45 = 0
            credited60 = 0
            credited75 = 0
            credited90 = 0
            balanced = 0
           
            for x in records:

                def get_15(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less15),('move_id.date','<=',self.date),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less15),('move_id.date','<=',self.date),('account_id.id','=',attr),('move_id.state','=','posted')])

                    debits = sum(line.debit for line in rec)
                    credits = sum(line.credit for line in rec)
                    
                    return debits - credits

                def cget_15(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less15),('move_id.date','<=',self.date),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less15),('move_id.date','<=',self.date),('account_id.id','=',attr),('move_id.state','=','posted')])

                    credits = sum(line.credit for line in rec)
                    
                    return credits

                def get_30(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less30),('move_id.date','<=',less15),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less30),('move_id.date','<=',less15),('account_id.id','=',attr),('move_id.state','=','posted')])

                    debits = sum(line.debit for line in rec)
                    credits = sum(line.credit for line in rec)

                    
                    return debits - credits

                def cget_30(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less30),('move_id.date','<=',less15),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less30),('move_id.date','<=',less15),('account_id.id','=',attr),('move_id.state','=','posted')])

                    credits = sum(line.credit for line in rec)
                    
                    return credits

                def get_45(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less45),('move_id.date','<=',less30),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less45),('move_id.date','<=',less30),('account_id.id','=',attr),('move_id.state','=','posted')])

                    debits = sum(line.debit for line in rec)
                    credits = sum(line.credit for line in rec)

                    
                    return debits - credits


                def cget_45(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less45),('move_id.date','<=',less30),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less45),('move_id.date','<=',less30),('account_id.id','=',attr),('move_id.state','=','posted')])

                    credits = sum(line.credit for line in rec)
                    
                    return credits



                def get_60(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less60),('move_id.date','<=',less45),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less60),('move_id.date','<=',less45),('account_id.id','=',attr),('move_id.state','=','posted')])

                    debits = sum(line.debit for line in rec)
                    credits = sum(line.credit for line in rec)

                    
                    return debits - credits


                def cget_60(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less60),('move_id.date','<=',less45),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less60),('move_id.date','<=',less45),('account_id.id','=',attr),('move_id.state','=','posted')])

                    credits = sum(line.credit for line in rec)
                    
                    return credits


                def get_75(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less75),('move_id.date','<=',less60),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less75),('move_id.date','<=',less60),('account_id.id','=',attr),('move_id.state','=','posted')])

                    debits = sum(line.debit for line in rec)
                    credits = sum(line.credit for line in rec)

                    
                    return debits - credits

                def cget_75(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less75),('move_id.date','<=',less60),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less75),('move_id.date','<=',less60),('account_id.id','=',attr),('move_id.state','=','posted')])

                    credits = sum(line.credit for line in rec)
                    
                    return credits


                def get_90(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less90),('move_id.date','<=',less75),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less90),('move_id.date','<=',less75),('account_id.id','=',attr),('move_id.state','=','posted')])

                    debits = sum(line.debit for line in rec)
                    credits = sum(line.credit for line in rec)

                    
                    return debits - credits

                def cget_90(attr):
                    if self.filters == 'all':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less90),('move_id.date','<=',less75),('account_id.id','=',attr)])

                    if self.filters == 'posted':
                        rec = self.env['account.move.line'].search([('move_id.date','>',less90),('move_id.date','<=',less75),('account_id.id','=',attr),('move_id.state','=','posted')])

                    credits = sum(line.credit for line in rec)
                    
                    return credits


                worksheet.write_string (row, col,str(x.code),main_data)
                worksheet.write_string (row, col+1,str(x.name),main_data)
                debit_bal = get_15(x.id) + get_30(x.id) + get_45(x.id) + get_60(x.id) +get_75(x.id) + get_90(x.id)
                # credit_bal = cget_15(x.id) + cget_30(x.id) + cget_45(x.id) + cget_60(x.id) +cget_75(x.id) + cget_90(x.id)
                # bal = debit_bal - credit_bal

                worksheet.write_string (row, col+2,str(debit_bal),main_data)
                # worksheet.write_string (row, col+3,str(debit_bal),main_data)
                worksheet.write_string (row, col+3,str(get_15(x.id)),main_data)
                worksheet.write_string (row, col+4,str(get_30(x.id)),main_data)
                worksheet.write_string (row, col+5,str(get_45(x.id)),main_data)
                worksheet.write_string (row, col+6,str(get_60(x.id)),main_data)
                worksheet.write_string (row, col+7,str(get_75(x.id)),main_data)
                worksheet.write_string (row, col+8,str(get_90(x.id)),main_data)
                # worksheet.write_string (row, col+10,str(credit_bal),main_data)
                # worksheet.write_string (row, col+11,str(cget_15(x.id)),main_data)
                # worksheet.write_string (row, col+12,str(cget_30(x.id)),main_data)
                # worksheet.write_string (row, col+13,str(cget_45(x.id)),main_data)
                # worksheet.write_string (row, col+14,str(cget_60(x.id)),main_data)
                # worksheet.write_string (row, col+15,str(cget_75(x.id)),main_data)
                # worksheet.write_string (row, col+16,str(cget_90(x.id)),main_data)

                debited = debited + debit_bal
                debited15 = debited15 + get_15(x.id)
                debited30 = debited30 + get_30(x.id)
                debited45 = debited45 + get_45(x.id)
                debited60 = debited60 + get_60(x.id)
                debited75 = debited75 + get_75(x.id)
                debited90 = debited90 + get_90(x.id)
                # credited = credited + credit_bal
                # credited15 = credited15 + cget_15(x.id)
                # credited30 = credited30 + cget_30(x.id)
                # credited45 = credited45 + cget_45(x.id)
                # credited60 = credited60 + cget_60(x.id)
                # credited75 = credited75 + cget_75(x.id)
                # credited90 = credited90 + cget_90(x.id)
                # balanced = balanced + bal

                row += 1

            loc = 'A'+str(row+1)
            loc1 = 'B'+str(row+1)
            locb = 'C'+str(row+1)
            # locd = 'D'+str(row+1)
            loc15 = 'D'+str(row+1)
            loc30 = 'E'+str(row+1)
            loc45 = 'F'+str(row+1)
            loc60 = 'G'+str(row+1)
            loc75 = 'H'+str(row+1)
            loc90 = 'I'+str(row+1)
            # locc = 'K'+str(row+1)
            # cloc15 = 'L'+str(row+1)
            # cloc30 = 'M'+str(row+1)
            # cloc45 = 'N'+str(row+1)
            # cloc60 = 'O'+str(row+1)
            # cloc75 = 'P'+str(row+1)
            # cloc90 = 'Q'+str(row+1)
            end_loc = str(loc)+':'+str(loc1)
            worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
            worksheet.write_string(str(locb),str(debited),main_heading)
            # worksheet.write_string(str(locd),str(debited),main_heading1)
            worksheet.write_string(str(loc15),str(debited15),main_heading1)
            worksheet.write_string(str(loc30),str(debited30),main_heading1)
            worksheet.write_string(str(loc45),str(debited45),main_heading1)
            worksheet.write_string(str(loc60),str(debited60),main_heading1)
            worksheet.write_string(str(loc75),str(debited75),main_heading1)
            worksheet.write_string(str(loc90),str(debited90),main_heading1)
            # worksheet.write_string(str(locc),str(credited),main_heading2)
            # worksheet.write_string(str(cloc15),str(credited15),main_heading2)
            # worksheet.write_string(str(cloc30),str(credited30),main_heading2)
            # worksheet.write_string(str(cloc45),str(credited45),main_heading2)
            # worksheet.write_string(str(cloc60),str(credited60),main_heading2)
            # worksheet.write_string(str(cloc75),str(credited75),main_heading2)
            # worksheet.write_string(str(cloc90),str(credited90),main_heading2)

    def get_report(self):
        self.print_report()
        data_file = open(config['data_dir'] + "/container_advances_aging.xlsx", "rb")
        out = data_file.read()
        data_file.close()
        self.name = 'Container Deposit Aging Report' + ' ' + '.xlsx'
        self.file = base64.b64encode(out)
        return {
        "type": "ir.actions.do_nothing",
        }

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


class XlsxReportoverdue(models.TransientModel):
    _name = 'parentaccount.balance'


    date_from = fields.Date(default=date.today(),required=True,string="Date From")
    date_to = fields.Date(default=date.today(),required=True,string="Date To")
    account_id = fields.Many2one('account.account',string="Parent Account")
    name = fields.Char()
    file = fields.Binary('Download Report',)
    filters = fields.Selection([
        ('all', 'All'),
        ('posted','Posted')], string='Filter',required=True)
   

    @api.multi
    def print_report(self):

        acc = []
        accounts = self.env['account.account'].search([])
        for x in accounts:
            if x.parent_id.id == self.account_id.id:
                acc.append(x)

        self.xlsx_report(acc)


    @api.multi
    def xlsx_report(self,input_records):
        with xlsxwriter.Workbook(config['data_dir']+"/parent_account_balance.xlsx") as workbook:
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
                'font_size': '16',
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
            worksheet = workbook.add_worksheet('Parent Account Wise Balance')

            head = str(self.account_id.name) +' '+'From'+' '+ str(self.date_from)+' '+'To'+' '+str(self.date_to)

            worksheet.merge_range('A1:F1', head,merge_format)

            worksheet.set_column('B:B', 40)
            worksheet.set_column('A:A', 10)
            worksheet.set_column('C:F', 15)
            worksheet.write('A3', 'Code', main_heading)
            worksheet.write('B3', 'Account Name',main_heading)
            worksheet.write('C3', 'Previous Balance',main_heading)
            worksheet.write('D3', 'Debit',main_heading)
            worksheet.write('E3', 'Credit',main_heading)
            worksheet.write('F3', 'Balance',main_heading)
            
            row = 3
            col = 0
            records = input_records

            opened = 0
            debit = 0
            credit = 0
            balanced = 0
            for x in records:

                def get_open(attr):

                    if self.filters == "all":
                        opend = self.env['account.move.line'].search([('move_id.date','<',self.date_from),('account_id.id','=',attr)])

                    if self.filters == "posted":
                        opend = self.env['account.move.line'].search([('move_id.date','<',self.date_from),('account_id.id','=',attr),('move_id.state','=',"posted")])

                    debits = sum(line.debit for line in opend)
                    credits = sum(line.credit for line in opend)
                    
                    return debits - credits


                def get_debit(attr):

                    debit = 0

                    if self.filters == 'all':

                        rec = self.env['account.move.line'].search([('move_id.date','>=',self.date_from),('move_id.date','<=',self.date_to),('account_id.id','=',attr)])

                    if self.filters == 'posted':

                        rec = self.env['account.move.line'].search([('move_id.date','>=',self.date_from),('move_id.date','<=',self.date_to),('account_id.id','=',attr),('move_id.state','=','posted')])

                    for i in rec:
                        debit = debit + i.debit

                    return debit


                def get_credit(attr):

                    credit = 0

                    if self.filters == 'all':

                        rec = self.env['account.move.line'].search([('move_id.date','>=',self.date_from),('move_id.date','<=',self.date_to),('account_id.id','=',attr)])

                    if self.filters == 'posted':

                        rec = self.env['account.move.line'].search([('move_id.date','>=',self.date_from),('move_id.date','<=',self.date_to),('account_id.id','=',attr),('move_id.state','=','posted')])

                    for i in rec:
                        credit = credit + i.credit

                    return credit


                worksheet.write_string (row, col,str(x.code),main_data)
                worksheet.write_string (row, col+1,str(x.name),main_data)
                worksheet.write_string (row, col+2,str(get_open(x.id)),main_data)
                worksheet.write_string (row, col+3,str(get_debit(x.id)),main_data)
                worksheet.write_string (row, col+4,str(get_credit(x.id)),main_data)
                balance = (get_open(x.id) + get_debit(x.id)) - get_credit(x.id)
                worksheet.write_string (row, col+5,str(balance),main_data)


                opened = opened + get_open(x.id)
                debit = debit + get_debit(x.id)
                credit = credit + get_credit(x.id)
                balanced = balanced + balance

                row += 1

            loc = 'A'+str(row+1)
            loc1 = 'B'+str(row+1)
            loco = 'C'+str(row+1)
            locd = 'D'+str(row+1)
            locc = 'E'+str(row+1)
            locb = 'F'+str(row+1)
            end_loc = str(loc)+':'+str(loc1)
            worksheet.merge_range(str(end_loc), 'Total' ,main_heading)
            worksheet.write_string(str(loco),str(opened),main_heading)
            worksheet.write_string(str(locd),str(debit),main_heading)
            worksheet.write_string(str(locc),str(credit),main_heading)
            worksheet.write_string(str(locb),str(balanced),main_heading)

    def get_report(self):
        self.print_report()
        data_file = open(config['data_dir'] + "/parent_account_balance.xlsx", "rb")
        out = data_file.read()
        data_file.close()
        self.name = 'Parent Account Wise Balance' + ' ' + '.xlsx'
        self.file = base64.b64encode(out)
        return {
        "type": "ir.actions.do_nothing",
        }

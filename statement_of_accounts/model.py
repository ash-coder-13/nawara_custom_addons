import os
import xlsxwriter
from datetime import datetime,date,timedelta
from odoo import models, fields, api
from odoo.exceptions import Warning,ValidationError
from odoo.tools import config
import base64


class XlsxReportstatementAccounts(models.TransientModel):
    _name = 'statement.accounts'

    partner = fields.Many2one('res.partner',string="Customer",required=True)
    form = fields.Date("From")
    to = fields.Date("To")
    name = fields.Char()
    file = fields.Binary('Download Report',)


    def print_report(self):
        data = self.env['account.move.line'].search([('move_id.date','>=',self.form),('move_id.date','<=',self.to),('partner_id.id','=',self.partner.id),'|',('account_id.user_type_id','=','Receivable'),('account_id.user_type_id','=','Payable')])
        entred = self.env['account.move.line'].search([('move_id.date','<',self.form),('partner_id.id','=',self.partner.id),'|',('account_id.user_type_id','=','Receivable'),('account_id.user_type_id','=','Payable')])
        debits = 0
        credits = 0
        for x in entred:
            debits = debits + x.debit
            credits = credits + x.credit

        opening_bal = debits - credits
        data = sorted(data, key=lambda k: (k['date'], k['id']))
        self.xlsx_report(data, opening_bal)

    def xlsx_report(self,input_records,opening):
        with xlsxwriter.Workbook(config['data_dir']+"/statement_of_accounts.xlsx") as workbook:
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
                "align": 'right',
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
            worksheet = workbook.add_worksheet('Statement of Accounts')

            head = "SOA OF" +' '+ str(self.partner.name) +' '+ "FROM" +' '+ str(self.form) +' '+"TO"+' '+str(self.to)
            for row in range(1, 1):
                worksheet.set_row(row, 8)
            worksheet.merge_range('A1:I1', head,merge_format)
            balance = opening
            worksheet.set_column('A:C', 20)
            worksheet.set_column('D:D', 25)
            worksheet.set_column('E:H', 18)
            worksheet.set_column('I:I', 28)
            worksheet.write('A3', 'Date', main_heading)
            worksheet.write('B3', 'Transaction Type', main_heading)
            worksheet.write('C3', 'Invoice No', main_heading)
            worksheet.write('D3', 'Description',main_heading)
            worksheet.write('E3', 'Reference No', main_heading)
            worksheet.write('F3', 'Debit',main_heading)
            worksheet.write('G3', 'Credit',main_heading)
            worksheet.write('H3', 'Balance',main_heading)
            worksheet.write('I3', 'B L Number / Reference Number',main_heading)
            worksheet.write('D4', 'Opening'+' '+':'+' '+str(balance), main_heading)

            row = 4
            col = 0
            records = input_records

            for x in records:
                worksheet.write_string (row, col,str(x.date),main_data)
                worksheet.write_string (row, col+1,str(x.journal_id.name),main_data)
                worksheet.write_string (row, col+2,str(x.move_id.name),main_data)
                worksheet.write_string (row, col+3,str(x.name),main_data)
                worksheet.write_string (row, col+4,str(x.ref),main_data)
                worksheet.write_string (row, col+5,str(x.debit),main_data)
                worksheet.write_string (row, col+6,str(x.credit),main_data)
                worksheet.write_string (row, col+7,str((balance+x.debit)-x.credit),main_data)

                def get_blnum(attr):
                    name = " "
                    # invoices = self.env['account.invoice'].search([('move_id.id','=',attr)])
                    # if invoices.bill_num:
                    #     bill = invoices.bill_num
                    # else:
                    bill = " "

                    # if invoices.customer_ref:
                    #     cust = invoices.customer_ref
                    # else:
                    cust = " "

                    name = str(bill) +' '+ str(cust) 

                    return name

                worksheet.write_string (row, col+8,str(get_blnum(x.move_id.id)),main_data)
                balance = (balance+x.debit)-x.credit

                row += 1

            loc = 'A'+str(row+1)
            loc1 = 'G'+str(row+1)
            end_loc = str(loc)+':'+str(loc1)
            worksheet.merge_range(str(end_loc), 'Total Balance' ,main_heading1)
            locB = 'H'+str(row+1)
            worksheet.write_string(str(locB),str(balance),main_heading)


    def get_report(self):
        self.print_report()
        data_file = open(config['data_dir'] + "/statement_of_accounts.xlsx", "rb")
        out = data_file.read()
        data_file.close()
        self.name = 'Statement of Account For ' + self.partner.name + '.xlsx'
        self.file = base64.b64encode(out)
        return {
        "type": "ir.actions.do_nothing",
        }

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
import xlsxwriter
from odoo import models, fields, api
from odoo.tools import config
import base64
from datetime import date


class XlsxReportDsr(models.TransientModel):
    _name = 'dsr.report'


    date_f = fields.Date(default=date.today(),required=True,string="Date")
    date_t = fields.Date(default=date.today(),required=True,string="Date")
    name = fields.Char()
    file = fields.Binary('Download Report',)
   

    def print_report(self):

        cust = []
        imports = self.env['import.logic'].search([('date','>=',self.date_f),('date','<=',self.date_t),('acc_link','=',False)])
        for x in imports:
            if x.customer not in cust:
                cust.append(x.customer)
        exports = self.env['export.logic'].search([('date','>=',self.date_f),('date','<=',self.date_t),('acc_link','=',False)])
        for y in exports:
            if y.customer not in cust:
                cust.append(y.customer)
        trans = self.env['sale.order'].search([('date_order','>=',self.date_f),('date_order','<=',self.date_t),('acc_link','=',False)])
        for z in trans:
            if z.partner_id not in cust:
                cust.append(z.partner_id)

        self.xlsx_report(cust)


    def xlsx_report(self,input_records):
        with xlsxwriter.Workbook(config['data_dir']+"/dsr_report.xlsx") as workbook:
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
            worksheet = workbook.add_worksheet('DSR Report')


            head = 'DSR Report From'+' '+str(self.date_f)+' '+'To'+' '+str(self.date_t)
            worksheet.merge_range('A1:D1', head,merge_format)
            worksheet.set_column('A:A', 45)
            worksheet.set_column('B:D', 15)
            worksheet.write('A3', 'Customer', main_heading)
            worksheet.write('B3', 'Imports',main_heading)
            worksheet.write('C3', 'Exports',main_heading)
            worksheet.write('D3', 'Transport',main_heading)
            
            
            row = 3
            col = 0
            records = input_records

            imports = 0
            exports = 0
            trans = 0
           
            for x in records:

                def get_trans(attr):
                    amt = 0
                    trans = self.env['sale.order'].search([('date_order','>=',self.date_f),('date_order','<=',self.date_t),('acc_link','=',False),('partner_id.id','=',attr),])

                    for i in trans:
                        amt = amt + i.amount_total

                    return amt

                def get_exp(attr):
                    amt = 0
                    exports = self.env['export.logic'].search([('date','>=',self.date_f),('date','<=',self.date_t),('acc_link','=',False),('customer.id','=',attr)])

                    for i in exports:
                        data = []
                        for j in i.export_id:
                            if j.types not in data:
                                data.append(j.types)

                        for line in data:
                            value = 0
                            for x in i.export_id:
                                if x.types == line:
                                    value = value + 1

                            for y in i.cont_serv:
                                if y.type_contt == line:
                                    amt = amt + (value*y.sevr_charge_cont)

                    return amt


                def get_imp(attr):
                    amt = 0
                    imports = self.env['import.logic'].search([('date','>=',self.date_f),('date','<=',self.date_t),('acc_link','=',False),('customer.id','=',attr)])

                    for i in imports:
                        data = []
                        for j in i.import_id:
                            if j.types not in data:
                                data.append(j.types)

                        for line in data:
                            value = 0
                            for x in i.import_id:
                                if x.types == line:
                                    value = value + 1

                            for y in i.imp_contt:
                                if y.type_contt_imp == line:
                                    amt = amt + (value*y.sevr_charge_imp)

                    return amt


                worksheet.write_string (row, col,str(x.name),main_data)
                worksheet.write_string (row, col+1,str(get_imp(x.id)),main_data)
                worksheet.write_string (row, col+2,str(get_exp(x.id)),main_data)
                worksheet.write_string (row, col+3,str(get_trans(x.id)),main_data)
        
                imports = imports + get_imp(x.id)
                exports = exports + get_exp(x.id)
                trans = trans + get_trans(x.id)
               
                row += 1

            loct = 'A'+str(row+1)
            loc1 = 'B'+str(row+1)
            loc2 = 'C'+str(row+1)
            loc3 = 'D'+str(row+1)
            worksheet.write_string(str(loct),'Total',main_heading)
            worksheet.write_string(str(loc1),str(imports),main_heading)
            worksheet.write_string(str(loc2),str(exports),main_heading)
            worksheet.write_string(str(loc3),str(trans),main_heading)
            

    def get_report(self):
        self.print_report()
        data_file = open(config['data_dir'] + "/dsr_report.xlsx", "rb")
        out = data_file.read()
        data_file.close()
        self.name = 'DSR Report' + ' ' + '.xlsx'
        self.file = base64.b64encode(out)
        return {
        "type": "ir.actions.do_nothing",
        }
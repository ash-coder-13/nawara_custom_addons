# -*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    OpenERP, Open Source Management Solution                                        ##
##    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved       ##
##                                                                                    ##
##    This program is free software: you can redistribute it and/or modify            ##
##    it under the terms of the GNU Affero General Public License as published by     ##
##    the Free Software Foundation, either version 3 of the License, or               ##
##    (at your option) any later version.                                             ##
##                                                                                    ##
##    This program is distributed in the hope that it will be useful,                 ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of                  ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   ##
##    GNU Affero General Public License for more details.                             ##
##                                                                                    ##
##    You should have received a copy of the GNU Affero General Public License        ##
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.           ##
##                                                                                    ##
########################################################################################
########################################################################################

import time
from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.invoice_status_report.sales_summary_report'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('invoice_status_report.sales_summary_report')
        active_wizard = self.env['invoice.statusreport'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list)

        record_wizard = self.env['invoice.statusreport'].search([('id', '=', emp_list_max)])
        record_wizard_del = self.env['invoice.statusreport'].search([('id', '!=', emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form


        cust = []
        invoices = self.env['account.move'].search([('type','=','out_invoice'),('state','in',('draft','posted')),('invoice_date','>=',form),('invoice_date','<=',to)])
        for x in invoices:
            if x.partner_id not in cust:
                cust.append(x.partner_id)


        inv = []
        def get_inv(attr):
            del inv [:]
            invoice = self.env['account.move'].search(
                [('type', '=', 'out_invoice'), ('state', 'in', ('draft', 'posted')), ('invoice_date', '>=', form),
                 ('invoice_date', '<=', to),('partner_id','=',attr)])


            for x in invoice:
                inv.append(x)

        def get_date(attr):

            c_date = ' '
            v_date = ' '
            inv_num = ' '
            sale_name = ' '
            diff = ' '

            invoice = self.env['account.move'].search([('type','=','out_invoice'),('state','in',('draft','posted')),('invoice_date','>=',form),('invoice_date','<=',to),('id','=',attr)])

            if invoice.number:
                inv_num = '('+str(invoice.number)+')'
            if invoice.sale_link:
                sale_name = invoice.sale_link.name
            
            mail_val = self.env['mail.message'].search([('res_id','=',attr),('subtype_id.description','=','Invoice validated')])
            mail_create = self.env['mail.message'].search([('res_id','=',attr),('subtype_id.description','=','Invoice Created')])
            if mail_val:
                mail_val = mail_val[-1]
                v_date = mail_val.date[:10]
            if mail_create:
                mail_create = mail_create[-1]
                c_date = mail_create.date[:10]
            if mail_create and mail_val:
                fmt = '%Y-%m-%d'
                d1 = datetime.strptime(c_date, fmt)
                d2 = datetime.strptime(v_date, fmt)
                diff = str((d2-d1).days)

            return c_date,v_date,inv_num,sale_name,diff



        # datad = []
        # for i in cust:
        #     sub_data = []
        #     inv = self.env['account.invoice'].search([('type','=','out_invoice'),('state','in',('draft','=','open')),('date_invoice','>=',form),('date_invoice','<=',to),('partner_id','=',i.id)])
        #     print inv
        #     print "rrrrrrrrrrrrrrrrrrrrr"
        #     for j in inv:
        #         mail_val = self.env['mail.message'].search([('res_id','=',j.id),('subtype_id.description','=','Invoice validated')])
        #         mail_create = self.env['mail.message'].search([('res_id','=',j.id),('subtype_id.description','=','Invoice Created')])
        #         if mail_val:
        #             v_date = mail_val.date[:10]
        #         if mail_create:
        #             c_date = mail_create.date[:10]

        #         print j.sale_link.name
        #         print c_date
        #         print v_date
        #         print "ggggggggggggggggggg"

        #         sub_data = ({
        #             'source': j.sale_link.name,
        #             'c_date': c_date,
        #             'v_date': v_date,
        #             })

        #         print sub_data
        #         print "ffffffffffffffff"

        #     datad = ({
        #         'named': i.name,
        #         'sub_datad':sub_data,
        #         })

        # print datad
        # print "yyyyyyyyyyyyyyyyy"




        
        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'form': form,
            'to': to,
            'inv': inv,
            'cust': cust,
            'get_inv': get_inv,
            'get_date': get_date,
            
        }

        return report_obj.render('invoice_status_report.sales_summary_report', docargs)

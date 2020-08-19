#-*- coding:utf-8 -*-
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

from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning

class PartnerLedgerReport(models.AbstractModel):
    _name = 'report.terminal_operation_report.partner_ledger_2_report'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('terminal_operation_report.partner_ledger_2_report')
        active_wizard = self.env['terminal.ledger'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['terminal.ledger'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['terminal.ledger'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        records = self.env['sale.order'].search([('in_terminal', '=', True),('in_storage', '=', False),('sale_status.name','!=','Job Completed'),('trans_mode','=','in'),('pullout_mode','=','in')])

        def get_name(attr):
            rec = self.env['sale.order'].search([('id', '=', attr)])
            if rec.vehicle_id:
                return str(rec.vehicle_id.model_id.brand_id.name) +' / '+ str(rec.vehicle_id.model_id.name) +' / '+ str(rec.vehicle_id.license_plate)
            else:
                return ""


        
        docargs = {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': records,
            'get_name': get_name,
        }

        return report_obj.render('terminal_operation_report.partner_ledger_2_report', docargs)
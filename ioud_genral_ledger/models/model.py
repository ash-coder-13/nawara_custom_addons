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
import dateutil.relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import Warning
import calendar

class PartnerLedgerReport(models.AbstractModel):
    _name = 'report.ioud_genral_ledger.genral_ledger_report'

    @api.model
    def _get_report_values(self,docids, data=None):

        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('genral_ledger.genral_ledger_report')
        active_wizard = self.env['genral.ledger'].search([])
        records = self.env['account.account'].browse(docids)
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['genral.ledger'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['genral.ledger'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form
        typed = record_wizard.entry_type
        account = record_wizard.account

        def opening(bal):
            PreMonth = datetime.strptime(form, '%Y-%m-%d').date() - dateutil.relativedelta.relativedelta(months=1)
            LastDate = str(PreMonth.year) + '-' + str(PreMonth.month) +'-' + str(calendar.monthrange(PreMonth.year, PreMonth.month)[1])
            if typed == "all":
                #opend = self.env['account.move.line'].search([('move_id.date','>=',str(PreMonth)),('move_id.date','<=',LastDate),('account_id.id','=',bal.id)])
                opend = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','=',bal.id)])
                
            if typed == "posted":
                opend = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','=',bal.id),('move_id.state','=',"posted")])

            opening = 0
            for x in opend:
                opening += x.debit
                opening -= x.credit
            return opening
        
        def OpeningCRDRStatus(bal):
            PreMonth = datetime.strptime(form, '%Y-%m-%d').date() - dateutil.relativedelta.relativedelta(months=1)
            LastDate = str(PreMonth.year) + '-' + str(PreMonth.month) +'-' + str(calendar.monthrange(PreMonth.year, PreMonth.month)[1])
            if typed == "all":
                #opend = self.env['account.move.line'].search([('move_id.date','>=',str(PreMonth)),('move_id.date','<=',LastDate),('account_id.id','=',bal.id)])
                opend = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','=',bal.id)])
                
            if typed == "posted":
                opend = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','=',bal.id),('move_id.state','=',"posted")])
            credits = 0.0
            debits = 0.0
            for x in opend:
                debits += x.debit
                credits -= x.credit
            return 'Cr' if credits > debits else 'Dr'
        
        if typed == "all":
            entries = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','=',account.id)])

        if typed == "posted":
            entries = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','=',account.id),('move_id.state','=',"posted")])
        

        users = self.env['res.users'].search([('id','=',self._uid)])
        docargs = {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': account,
            'data': data,
            'record_wizard': record_wizard,
            'opening': opening,
            'OpeningCRDRStatus':OpeningCRDRStatus,
            'entries': entries,
            'users': users,
            'acc_num': account,
        }

        return  docargs
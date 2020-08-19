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

from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning


class PartnerLedgerReport(models.AbstractModel):
    _name = 'report.partner_ledger_final.partner_ledger_report'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('partner_ledger_final.partner_ledger_report')
        active_wizard = self.env['partner.ledger'].search([])
        active_wizard_ids = self.env['partner.ledger'].browse(docids)

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list)

        partner_list = []
        for x in active_wizard_ids.partner_ids:
            partner_list.append(x.id)
        partner_records = self.env['res.partner'].browse(partner_list)

        record_wizard = self.env['partner.ledger'].search([('id', '=', emp_list_max)])
        record_wizard_del = self.env['partner.ledger'].search([('id', '!=', emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form

        def getPartnerName(partner):
            return "%s" % (partner.name or '')

        def get_entries(partner):
            entries = self.env['account.move.line'].search(
                [('move_id.date', '<=', to), ('move_id.date', '>=', form), ('partner_id.id', '=', partner.id), '|',
                 ('account_id.user_type_id', '=', 'Receivable'), ('account_id.user_type_id', '=', 'Payable')])
            return entries

        def opening_bal(entries):
            debits = 0
            credits = 0
            for x in entries:
                debits = debits + x.debit
                credits = credits + x.credit

            opening_bal = debits - credits
            return opening_bal

        def get_entries_before(partner):
            entries_before = self.env['account.move.line'].search(
                [('move_id.date', '<=', form), ('partner_id.id', '=', partner.id), '|',
                 ('account_id.user_type_id', '=', 'Receivable'), ('account_id.user_type_id', '=', 'Payable')])
            return entries_before

        def real_open_bal(entries_before):
            prev_ent_debit = 0
            prev_ent_credit = 0

            for i in entries_before:
                prev_ent_debit = prev_ent_debit + i.debit
                prev_ent_credit = prev_ent_credit + i.credit

            real_open_bal = prev_ent_debit - prev_ent_credit
            return real_open_bal

        docargs = {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': partner_records,
            'data': data,
            'form': form,
            'to': to,
            'opening_bal': opening_bal,
            'real_open_bal': real_open_bal,
            'getPartnerName': getPartnerName,
            'get_entries_before': get_entries_before,
            'get_entries': get_entries,
        }

        return report_obj.render('partner_ledger_final.partner_ledger_report', docargs)

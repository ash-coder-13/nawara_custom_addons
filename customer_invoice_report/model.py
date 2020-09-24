# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################
from datetime import date
from num2words import num2words
from odoo import models, fields, api


class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.customer_invoice_report.module_report'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['ir.actions.report']
        report = self.env.ref('customer_invoice_report.module_report')
        active_wizard = self.env['cust.invoice'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list)

        record_wizard = self.env['cust.invoice'].search([('id', '=', emp_list_max)])

        record_wizard_del = self.env['cust.invoice'].search([('id', '!=', emp_list_max)])
        record_wizard_del.unlink()
        date_from = record_wizard.date_from
        date_to = record_wizard.date_to
        customer = record_wizard.customer
        rec = self.env['account.move'].search([('invoice_date', '>=', date_from), ('invoice_date', '<=', date_to),
                                                  ('partner_id', '=', customer.id),
                                                  ('type', '=', 'out_invoice')])

        def getOrderLine(origin, line_name):
            sale_Order = self.env['sale.order'].search([('name', '=', origin)])
            if sale_Order:
                for line in sale_Order.order_line:
                    if line.name == line_name:
                        return line.net_price
            else:
                return 0.0

        def getOrderRef(origin):
            sale_Order = self.env['sale.order'].search([('name', '=', origin)])
            if sale_Order:
                return sale_Order.reference_no
            else:
                return ""

        def getdiscount_fixed(origin, line_name):
            sale_Order = self.env['sale.order'].search([('name', '=', origin)])
            if sale_Order:
                for line in sale_Order.order_line:
                    if line.name == line_name:
                        return line.discount_fixed
            else:
                return 0.0

        def getVatAmount(origin, line_name):
            sale_Order = self.env['sale.order'].search([('name', '=', origin)])
            if sale_Order:
                for line in sale_Order.order_line:
                    if line.name == line_name:
                        return line.afterTaxAmt
            else:
                return 0.0

        def number_to_spell(attrb):
            word = num2words((attrb))
            word = word.title() + " " + "SAR Only"
            return word

        def getname():
            name = self.env['res.users'].search([('id', '=', self._uid)]).name
            return name

        def getPartnerName():
            return "%s" % (customer.name or '')

        def get_entries(partner):
            entries = self.env['account.move.line'].search([
                ('move_id.date', '>=', date_from),
                ('move_id.date', '<=', date_to),
                ('partner_id.id', '=', partner.id),
                '|',
                ('account_id.user_type_id', '=', 'Receivable'),
                ('account_id.user_type_id', '=', 'Payable')])
            return entries

        def get_partner_payment(entries):
            payments = sum(line.credit for line in entries)
            return payments

        def opening_bal(entries):
            debits = 0
            credits = 0
            for x in entries:
                debits = debits + x.debit
                credits = credits + x.credit

            opening_bal = debits - credits
            return opening_bal

        def get_entries_before(partner):
            entries_before = self.env['account.move.line'].search([
                ('move_id.date', '<=', date_from),
                ('partner_id.id', '=', partner.id),
                '|', ('account_id.user_type_id', '=', 'Receivable'),
                ('account_id.user_type_id', '=', 'Payable')])
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
            'rec': rec,
            'getPartnerName': getPartnerName,
            'customer': customer,
            'date': date.today(),
            'getdiscount_fixed': getdiscount_fixed,
            'getOrderLine': getOrderLine,
            'getVatAmount': getVatAmount,
            'number_to_spell': number_to_spell,
            'customer_id': customer.id,
            'getname': getname,
            'getOrderRef': getOrderRef,
            'opening_bal': opening_bal,
            'real_open_bal': real_open_bal,
            'get_entries_before': get_entries_before,
            'get_entries': get_entries,
            'get_partner_payment': get_partner_payment,
        }

        return report_obj.render('customer_invoice_report.module_report', docargs)

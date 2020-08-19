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

from odoo import models, fields, api


class CustomerFocuzedRevenue(models.TransientModel):
    _name = 'customer.focuzed.revenue'

    partner_ids = fields.Many2many("res.partner", string="Customer")
    sale_status_ids = fields.Many2many("import.status", string="Sale Status")
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")


    def generate_cfr_report(self):
        sale_order = self.env['sale.order'].search([
            ('partner_id', '=', self.partner_ids.ids), ('date_order', '>=', self.start_date),
            ('date_order', '<=', self.end_date), ('sale_status', '=', self.sale_status_ids.ids)])
        # print sale_order
        return self.env["report"].get_action(sale_order, 'ntf_custom.report_customer_focuzed_rev')

    # def print_xls_report(self):
    #     sale_order = self.env['sale.order'].search([
    #         ('partner_id', '=', self.partner_ids.ids), ('date_order', '>=', self.start_date),
    #         ('date_order', '<=', self.end_date), ('sale_status', '=', self.sale_status_ids.ids)])
    #     return self.env["report"].get_action(sale_order, 'ntf_custom.report_customer_focused_rev.xlsx')


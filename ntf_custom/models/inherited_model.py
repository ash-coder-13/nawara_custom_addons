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

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import Warning


class CustomerService(models.Model):
    _name = 'customer.service'
    _rec_name = 'name'

    code = fields.Char(string="Code")
    name = fields.Char(string="Service Name")

    _sql_constraints = [('name_uniq', 'unique (name)', 'The Service must be unique !'),
                        ('code_uniq', 'unique (code)', 'The Service code must be unique !'), ]


class IndustrySection(models.Model):
    _name = 'industry.section'
    _rec_name = 'name'

    code = fields.Char(string="Code")
    name = fields.Char(string="Section Description")

    _sql_constraints = [('name_uniq', 'unique (name)', 'The Section must be unique !'),
                        ('code_uniq', 'unique (code)', 'The Section code must be unique !'),
                        ]


class IndustryDivision(models.Model):
    _name = 'industry.division'
    _rec_name = 'name'

    section_id = fields.Many2one("industry.section", string="Section")

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Division Description")
    class_code = fields.Char(string="Classification Code", compute='_compute_class_code')
    c_code = fields.Char(string="Classification Code")

    _sql_constraints = [('name_uniq', 'unique (name)', 'The Division Description must be unique !'),
                        ('code_uniq', 'unique (code)', 'The Division code must be unique !'),
                        ]

    @api.onchange('section_id', 'code')
    def _onchange_c_code(self):
        for file in self:
            if file.code and file.section_id:
                file.c_code = file.section_id.code + file.code


    def _compute_class_code(self):
        for file in self:
            if file.c_code:
                file.class_code = file.c_code


class ResPartner(models.Model):
    _inherit = 'res.partner'

    section_id = fields.Many2one("industry.section", string="Section")
    division_id = fields.Many2one("industry.division", string="Division")
    class_code = fields.Char(string="Classification Code", compute='_compute_class_code')
    customer_service_id = fields.Many2many("customer.service", string="Service")
    profile_type = fields.Selection(string="Profile Type",
                                    selection=[('getting_to_know', 'Getting to know the Customer person'),
                                               ('referral', 'Referral'), ('consolidated_data', 'Consolidated Data')])
    gtk_type = fields.Selection(string="Profile Sub Type", selection=[('rec_or_op', 'Receptionist or Operator'), (
        'not_concerned', 'Not the Concerned Department')])
    ref_type = fields.Selection(string="Referral Sub Type", selection=[('cred_ref', 'Credible referral'),
                                                                       ('dec_maker', 'Decision Maker  and referral'),
                                                                       ('non_cred_ref', 'Non- Credible referral'), (
                                                                           'non_dec_maker',
                                                                           'Non- Decision maker and referral')])
    cons_type = fields.Selection(string="Consolidated Data Sub Type",
                                 selection=[('non_decs_maker', 'Non-Decision Maker'), ('deci_maker', 'Decision Maker')])


    def _compute_class_code(self):
        for file in self:
            if file.division_id:
                file.class_code = file.division_id.class_code


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    customer_type = fields.Selection(string="Type", selection=[('interested_meet', 'Interested and Ready to meet'), (
        'interested_nmeeting', 'Interested and  not willing to meet'), ('interested_long_dist',
                                                                        'Interested and cannot meet due to location constraints'),
                                                               ('not_interested', 'Not Interested'),
                                                               ('r_more_info', 'Requires More information / Undecided'),
                                                               ('only_quote', 'Only wants a quote'),
                                                               ('other', 'Other')])


class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'


    def mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.expiration_date and i.state != 'closed':
                exp_date = fields.Date.from_string(i.expiration_date) - timedelta(days=90)
                exp_date_60 = fields.Date.from_string(i.expiration_date) - timedelta(days=60)
                exp_date_30 = fields.Date.from_string(i.expiration_date) - timedelta(days=30)
                exp_date_7 = fields.Date.from_string(i.expiration_date) - timedelta(days=7)
                if date_now == exp_date or date_now == exp_date_60 or date_now == exp_date_30 or date_now == exp_date_7:
                    mail_content = "Dear HR,<br>" + str(i.vehicle_id.model_id.brand_id.name) + "/" + str(
                        i.vehicle_id.model_id.name) + "/" + str(i.vehicle_id.license_plate) + "'s " + str(
                        i.cost_subtype_id.name) + " is going to expire on " + \
                                   str(i.expiration_date) + ". Please renew it before expiry date."
                    main_content = {
                        'subject': _('Document-%s Will Expire On %s') % (i.cost_subtype_id.name, i.expiration_date),
                        'body_html': mail_content,
                        'email_to': "hr@ntf-group.com",
                        'email_cc': "a.bajunaid@ntf-group.com,mostafa.gad@ntf-group.com,rizwan@ntf-group.com,m.vaseem@ntf-group.com,pt.firos@ntf-group.com",
                    }
                    self.env['mail.mail'].create(main_content).send()

    @api.constrains('expiration_date')
    def check_expr_date(self):
        for each in self:
            if each.expiration_date:
                exp_date = fields.Date.from_string(each.expiration_date)
                if exp_date < date.today():
                    raise Warning('Document Is Expired.')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    store_name = fields.Char(string="File Name")
    attachment = fields.Binary(string="Attachment", attachment=True, help="Upload your supporting document here")

#
# class AccountInvoiceLine(models.Model):
#     _inherit = 'account.invoice.line'
#
#     store_name = fields.Char(string="File Name")
#     attachment = fields.Binary(string="Attachment", attachment=True, help="Upload your supporting document here")

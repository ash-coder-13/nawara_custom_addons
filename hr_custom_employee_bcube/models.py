# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime as dt
from dateutil import relativedelta as rd
from datetime import datetime, date, timedelta
from odoo.exceptions import Warning


# Hr_Employee
class Hr_Employee(models.Model):
    _inherit = 'hr.employee'

    def port_mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.port_pass_exp:
                exp_date = fields.Date.from_string(i.port_pass_exp) - timedelta(days=90)
                exp_date_60 = fields.Date.from_string(i.port_pass_exp) - timedelta(days=60)
                exp_date_30 = fields.Date.from_string(i.port_pass_exp) - timedelta(days=30)
                exp_date_7 = fields.Date.from_string(i.port_pass_exp) - timedelta(days=7)
                if date_now == exp_date or date_now == exp_date_60 or date_now == exp_date_30 or date_now == exp_date_7:
                    mail_content = "Dear HR,<br>" + i.name + "'s Port Pass is going to expire on " + \
                                   str(i.port_pass_exp) + ". Please renew it before expiry date."
                    main_content = {
                        'subject': _('Port Pass Will Expire On %s') % (i.port_pass_exp),
                        'body_html': mail_content, 'email_to': "hr@ntf-group.com",
                        'email_cc': "a.bajunaid@ntf-group.com,mostafa.gad@ntf-group.com,pt.firos@ntf-group.com,rizwan@ntf-group.com,m.vaseem@ntf-group.com",
                    }
                    self.env['mail.mail'].create(main_content).send()

    @api.constrains('port_pass_exp')
    def check_expr_date(self):
        for each in self:
            if each.port_pass_exp:
                exp_date = fields.Date.from_string(each.port_pass_exp)
                if exp_date < date.today():
                    raise Warning('Port Pass Is Already Expired.')

    def _document_count(self):
        for each in self:
            document_ids = self.env['employee.iqama'].sudo().search([('employee', '=', each.id)])
            each.document_count = len(document_ids)

    def document_view(self):
        for rec in self:
            domain = [
                ('employee', '=', rec.id)]
            return {
                'name': _('Documents'),
                'domain': domain,
                'res_model': 'employee.iqama',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'tree,form',
                'help': _('''<p class="oe_view_nocontent_create">
                                   Click to Create for New Documents
                                </p>'''),
                'limit': 80,
                'context': "{'default_employee': '%s'}" % rec.id
            }

    document_count = fields.Integer(compute='_document_count', string='# Documents')

    port_pass_type = fields.Selection(string="Port Pass Type",
                                      selection=[('Yanbu', 'Yanbu'), ('Rabigh', 'Rabigh'), ('Jeddah', 'Jeddah'),
                                                 ('Dammam', 'Dammam')])
    port_pass_exp = fields.Date(string="Expiry Date")
    employee_no = fields.Char(string="Employee Number")
    laptop_des = fields.Many2one('maintenance.equipment', string='Laptop/Desktop')
    name_as_pass = fields.Char('Name(As in Passport)')
    iqama_num = fields.Many2one('employee.iqama', 'Iqama Number / ID Number')
    employee_code = fields.Char()
    arabic_name = fields.Char()
    office = fields.Many2one('office.office')
    work_fax = fields.Char('Work Fax')
    serial_num = fields.Char('Serial No.')
    performence_manager = fields.Many2one('hr.employee', 'Performance Manager')
    grade = fields.Char()
    head = fields.Many2one('hr.employee', 'Head of Function')
    line_man = fields.Many2one('hr.employee', 'Line Manager')
    is_head = fields.Boolean('Is Head  of Function')
    is_line_man = fields.Boolean('Is Line Manager')
    religion = fields.Char()
    gosi_no = fields.Many2one('employee.grops', 'GOSI NO')
    spouse_no = fields.Char('Spouse Phone No.')
    joining_date = fields.Date('Joining Date', required=False)
    leaving_date = fields.Date()
    serv_year = fields.Char('Total Service Year')
    vendor_no = fields.Char("Vendor No")
    other_asset = fields.Many2many('maintenance.equipment', string='Other Assets')
    project = fields.Many2one('projects.projects')
    mol_no = fields.Char("MOL No")
    iban = fields.Char("IBAN")
    bank_code = fields.Char("Bank Code")
    dependent_id = fields.One2many('hr.dependent', 'dependent_relation', string="Dependent")
    qualifiction_id = fields.One2many('hr.qualification', 'qualification_relation_name', string="Qualifications")
    certification_id = fields.One2many('hr.certification', 'certification_relation', string="Certification")
    insurance_id = fields.One2many('hr.insurance', 'insurance_relation', string="Insurance")
    trainings_id = fields.One2many('hr.trainings', 'trainings_relation', string="Trainings")
    documents_id = fields.One2many('hr.documents', 'documents_relation', string="Documents")
    emergency_id = fields.One2many('hr.emergency', 'relation', string="Emergency Contact")
    issue = fields.Date("Issue Date", required=False)
    expiry = fields.Date("Expiry Date", required=False)
    job_idd = fields.Many2one('designation.info', string="Job Id")
    passport_idd = fields.Many2one('hr.documents', string="Passport No")
    depend = fields.Boolean("Have Dependent")
    fn = fields.Char("First Name", required=False)
    mn = fields.Char("Middle Name")
    ln = fields.Char("Last Name")
    bg = fields.Char("Blood Group")
    a_email = fields.Char("Alternate Email ID")
    airport = fields.Char("Nearest Airport")
    street = fields.Char("Street", required=False)
    street2 = fields.Char("Street2")
    zip_code = fields.Char("Zip Code")
    city = fields.Char("City", required=False)
    state_id = fields.Many2one('res.country.state', string="Fed. State")
    country_idd = fields.Many2one('res.country', string="Country", required=False)
    contact_no = fields.Char("Contact No")
    p_street = fields.Char("Street", required=False)
    p_street2 = fields.Char("Street2")
    p_zip_code = fields.Char("Zip Code")
    p_city = fields.Char("City", required=False)
    p_state_id = fields.Many2one('res.country.state', string="Fed. State")
    p_country_id = fields.Many2one('res.country', string="Country", required=False)
    p_contact_no = fields.Char("Contact No")
    designation = fields.Many2one('designation.info', string="Designation Info", required=False)
    id_prof = fields.Char("ID Profession", required=False)
    category = fields.Many2one('category.info', string="Category")
    department = fields.Many2one('hr.department', string="Department", required=False)
    r_manager = fields.Many2one('hr.employee', string="Reporting Manager")
    division = fields.Many2one('division.info', string="Division", required=False)
    mol_location = fields.Char(string="MOL Location", required=False)
    sponsor = fields.Many2one('res.sponsor', string="Sponsor", required=False)
    r_name = fields.Char("Name")
    rc_name = fields.Char("Company Name")
    r_designation = fields.Many2one('designation.info', "Designation")
    r_mobile = fields.Char("Mobile No")
    r_phone = fields.Char("Phone No")
    r_mail = fields.Char("Email")
    r_remark = fields.Char("Remarks")
    reason = fields.Char(string="Reason")
    same_add = fields.Boolean(string="Same Address")
    status_id = fields.Many2one(comodel_name="status", string="Status", required=False, )

    c_athu = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No'), ], string="Clearing Authority", required=False)

    fc_athu = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No'), ], default='no', string="Final Clearing Authority", required=False)

    emp_status = fields.Selection([(
        'Active', 'Active'),
        ('Inactive', 'Inactive'), ], 'Employee Status', required=False)

    # --------------------------------------------------

    @api.onchange('same_add')
    def _onchange_same_add(self):
        if self.same_add == True:
            self.p_street = self.street
            self.p_street2 = self.street2
            self.p_zip_code = self.zip_code
            self.p_city = self.city
            self.p_state_id = self.state_id
            self.p_country_id = self.country_idd
            self.p_contact_no = self.contact_no

    @api.onchange('state_id')
    def _onchange_state(self):
        self.country_idd = self.state_id.country_id

    @api.onchange('job_idd')
    def onchange_job_idd(self):
        if self.job_idd:
            self.designation = self.job_idd
            self.r_designation = self.job_idd
            self.id_prof = self.job_idd.profession

    @api.onchange('department_id')
    def onchange_department_id(self):
        if self.department_id:
            self.department = self.department_id

    @api.onchange('line_man')
    def onchange_line_man(self):
        self.r_manager = self.line_man

    @api.onchange('p_state_id')
    def _onchange_state(self):
        self.p_country_id = self.p_state_id.country_id

    @api.onchange('joining_date', 'leaving_date')
    def onchange_dates(self):
        if self.joining_date:
            if self.leaving_date:
                start_date_1 = dt.strptime(self.joining_date, "%Y-%m-%d")
                end_date_1 = dt.strptime(self.leaving_date, "%Y-%m-%d")
                r = rd.relativedelta(end_date_1, start_date_1)
                if r.years > 0:
                    years = r.years
                    months = r.months
                    self.serv_year = "%s Years %s Months" % (years, months)
                else:
                    years = r.years
                    months = r.months
                    self.serv_year = "%s Months" % months


# Dependent
class Emergency(models.Model):
    _name = 'hr.emergency'
    _rec_name = 'e_name'

    e_name = fields.Char("Name", required=True)
    e_relationship = fields.Char("Relationship", required=True)
    e_mobile = fields.Char("Mobile No", required=True)
    ea_mobile = fields.Char("Alternate No", required=True)
    e_phone = fields.Char("Phone No")
    e_mail = fields.Char("Email")
    e_remark = fields.Char("Remarks")
    relation = fields.Many2one('hr.employee')


# Dependent
class Dependent(models.Model):
    _name = 'hr.dependent'
    _rec_name = 'name'
    d_passport = fields.Many2one('hr.documents', "Passport No", required=True)
    name = fields.Char('Name(As in Passport)', required="True")
    employee = fields.Char()
    arabic_name = fields.Char()
    dob = fields.Date('Date of Birth', required=True)
    pob = fields.Char('Place of Birth')
    date_issue = fields.Date('Date of Issue')
    date_expiry = fields.Date('Date of Expiry')
    nationality = fields.Many2one('res.country', "Nationality")
    relation = fields.Many2one('relation.relation')
    religion = fields.Many2one('religion.religion')
    iqama_num = fields.Char('Iqama Number')
    issue_place = fields.Many2one('issued_place.issued_place')
    fn = fields.Char("First Name", required=True)
    mn = fields.Char("Middle Name", required=True)
    ln = fields.Char("Last Name", required=True)
    dependent_relation = fields.Many2one('hr.employee')

    d_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string="Gender", required=True)

    # --------------------------------------------------

    @api.onchange('name')
    def _onchange_name(self):
        self.employee = self.dependent_relation.name


# Qualification
class Qualification(models.Model):
    _name = 'hr.qualification'
    _rec_name = 'uni_name'

    uni_name = fields.Many2one('office.office', string='University Name', required=True)
    prg_status = fields.Char('Program Status')
    comp_date = fields.Date('Completion Date')
    contact_name = fields.Char('Contact Name')
    contact_phn = fields.Char('Contact Phone No')
    contact_email = fields.Char('Contact Email')
    qualification_relation_name = fields.Many2one('hr.employee', string='Qualification Relation Name')


# Certification
class Certification(models.Model):
    _name = 'hr.certification'
    _rec_name = 'car_name'

    car_name = fields.Char('Certification Name', required=True)
    issue_org = fields.Char('Issuing Organization', required=True)
    issue_date = fields.Date('Date of Issue')
    exp_date = fields.Date('Date of Expiry')
    regis_no = fields.Char('Registration No.')
    contact_name = fields.Char()
    contact_phn = fields.Char('Contact Phone No')
    contact_email = fields.Char()
    certification_relation = fields.Many2one('hr.employee', string='Certification Relation')


# EmployeeCard
class EmployeeCard(models.Model):
    _name = 'employee.card'
    _rec_name = 'employee'

    employee = fields.Many2one('hr.employee', required=True)
    employee_code = fields.Char(string='Employee Code')
    department = fields.Many2one('hr.department')
    job_title = fields.Many2one('designation.info', string='Job Title')
    office = fields.Char()
    card_no = fields.Char(string='Card No.')
    requested_date = fields.Char(string='Requesed Date')
    reason = fields.Char()
    status = fields.Char()
    access_type = fields.Char(string='Access Type')
    period_stay = fields.Date(string='Period of Stay')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')

    card_type = fields.Selection([(
        'Acces Card', 'Access Card'),
        ('Business Card', 'Business Card'),
        ('Id Card', 'Id Card')], required=True, string='Card Type')

    # --------------------------------------------------

    @api.onchange('employee')
    def onchange_date_id(self):
        if self.employee:
            self.employee_code = self.employee.employee_code
            self.job_title = self.employee.job_idd
            self.department = self.employee.department_id
            self.office = self.employee.office.name


# Employee Amedment
class Employee_Amedment(models.Model):
    _name = 'contract.amedment'
    _rec_name = 'employee'

    employee = fields.Many2one('hr.employee', required=True)
    employee_code = fields.Char("Employee Code", required=True)
    contract = fields.Many2one('hr.contract', required=True)
    effective_date = fields.Date()
    office = fields.Many2one('office.office', required=True)
    department = fields.Many2one('hr.department', required=True)
    grade = fields.Char()
    job = fields.Many2one('designation.info', string="Designation", required=True)
    to_office = fields.Many2one('office.office', string="To Office", required=True)
    to_department = fields.Many2one('hr.department', string="To Department", required=True)
    to_grade = fields.Char("To Grade")
    to_job = fields.Many2one('designation.info', string="To Designation", required=True)
    c_location = fields.Many2one('res.partner', string="Current Location", required=True)
    mol_location = fields.Char("MOL Location", required=True)
    r_manager = fields.Many2one('hr.employee', string="Reporting Manager", required=True)
    n_location = fields.Many2one('res.partner', string="New Location", required=True)
    nmol_location = fields.Char("MOL Location", required=True)
    nr_manager = fields.Many2one('hr.employee', string="Reporting Manager", required=True)
    remark = fields.Char("Remarks")

    @api.onchange('employee')
    def onchange_employee(self):
        if self.employee:
            self.office = self.env['office.office'].search([('name', '=', self.employee.office.name)])
            self.grade = self.employee.grade
            self.employee_code = self.employee.employee_code
            self.contract = self.env['hr.contract'].search([('name', '=', self.employee.name)])
            self.department = self.env['hr.department'].search([('name', '=', self.employee.department_id.name)])
            self.grade = self.employee.grade
            self.job = self.env['designation.info'].search([('job', '=', self.employee.job_idd.job)])
            self.mol_location = self.employee.mol_location
            self.c_location = self.employee.address_id
            self.r_manager = self.employee.performence_manager.id
            self.to_department = self.to_office = self.to_grade = self.to_job = self.c_location = self.mol_location = ''

    def validate_changes(self):
        self.employee.department_id = self.to_department.id
        self.employee.office = self.to_office.id
        self.employee.grade = self.to_grade
        self.employee.job_idd = self.to_job.id
        self.nmol_location = self.mol_location
        self.n_location = self.c_location
        self.nr_manager = self.r_manager


# Employee Iqama
class Iqama(models.Model):
    _name = 'employee.iqama'
    _rec_name = 'iqama_no'

    employee = fields.Many2one('hr.employee', required=True)
    employee_code = fields.Char()
    office = fields.Char()
    department = fields.Char()
    job = fields.Char('Job Position')
    name = fields.Char('Name(As in Passport)')
    arabic_name = fields.Char()
    nationality = fields.Char()
    relegion = fields.Char('Religion')
    dob = fields.Date('Date of Birth')
    pob = fields.Char('Place of Birth')
    iqama_no = fields.Char("Iqama/ID No", required=True)
    serial_no = fields.Char()
    iqama_position = fields.Char()
    place_issue = fields.Char('Place of Issue')
    issue_date = fields.Date(required=True)
    expiry_date = fields.Date(required=True)
    arrival_date = fields.Date('Arrival Date in Suadi')
    in_saudi = fields.Boolean('Is Saudi?')
    t_link = fields.One2many('employee.family.iqama', 'link', string="Family Iqama/ID Details")

    def mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.expiry_date:
                exp_date = fields.Date.from_string(i.expiry_date) - timedelta(days=90)
                exp_date_60 = fields.Date.from_string(i.expiry_date) - timedelta(days=60)
                exp_date_30 = fields.Date.from_string(i.expiry_date) - timedelta(days=30)
                exp_date_7 = fields.Date.from_string(i.expiry_date) - timedelta(days=7)
                if date_now == exp_date or date_now == exp_date_60 or date_now == exp_date_30 or date_now == exp_date_7:
                    mail_content = "Dear HR,<br>" + i.employee.name + "'s Iqama is going to expire on " + \
                                   str(i.expiry_date) + ". Please renew it before expiry date."
                    main_content = {
                        'subject': _('Document-Iqama Will Expire On %s') % (i.expiry_date),
                        'body_html': mail_content,
                        'email_to': "hr@ntf-group.com",
                        'email_cc': "a.bajunaid@ntf-group.com,mostafa.gad@ntf-group.com,pt.firos@ntf-group.com",
                    }
                    self.env['mail.mail'].create(main_content).send()

    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            if each.expiry_date:
                exp_date = fields.Date.from_string(each.expiry_date)
                if exp_date < date.today():
                    raise Warning('Your Document Is Expired.')

    @api.onchange('employee')
    def onchange_employee(self):
        if self.employee:
            self.employee_code = self.employee.employee_code
            self.job = self.employee.job_idd.job
            self.name = self.employee.name_as_pass
            self.arabic_name = self.employee.arabic_name
            self.department = self.employee.department_id.name
            self.office = self.employee.office.name
            self.dob = self.employee.birthday
            self.pob = self.employee.place_of_birth
            self.relegion = self.employee.religion
            self.serial_no = self.employee.serial_num
            self.name = self.employee.name_as_pass
            self.iqama_no = self.employee.iqama_num.id
            self.arabic_name = self.employee.arabic_name
            self.nationality = self.employee.country_id.name
            self.issue_date = self.employee.iqama_num.issue_date
            self.expiry_date = self.employee.iqama_num.expiry_date


class FamliyIqama(models.Model):
    _name = 'employee.family.iqama'
    _rec_name = 'iqama_no'

    iqama_no = fields.Char("Iqama/ID No", required=True)
    serial_no = fields.Char()
    iqama_position = fields.Char()
    place_issue = fields.Char('Place of Issue')
    issue_date = fields.Date(required=True)
    expiry_date = fields.Date(required=True)
    arrival_date = fields.Date('Arrival Date in Suadi')
    in_saudi = fields.Boolean('Is Saudi?')
    link = fields.Many2one('employee.iqama')


# Employee Clearance
class EmployeeClearance(models.Model):
    _name = 'employee.clearance'
    _rec_name = 'employee'

    employee = fields.Many2one('hr.employee', required=True)
    employee_code = fields.Char()
    department = fields.Many2one('hr.department')
    office = fields.Char()
    email = fields.Char()
    contact_phone = fields.Char()
    seniority_date = fields.Date()
    res_date = fields.Date('Resignation/Term Date')
    last_country_day = fields.Date()
    last_day_work = fields.Date('Last Day of Work')
    letter_to_client = fields.Char()
    it_department = fields.One2many('it.department', 'department_relation')

    @api.onchange('employee')
    def onchange_employee(self):
        if self.employee:
            self.employee_code = self.employee.employee_code
            self.department = self.employee.department_id.id
            self.office = self.employee.office.name
            self.email = self.employee.work_email
            self.contact_phone = self.employee.work_phone


# Employee Gosi
class Gosi(models.Model):
    _name = 'employee.grops'
    _rec_name = 'gosi_no'

    employee = fields.Many2one('hr.employee', required=True)
    employee_code = fields.Char()
    department = fields.Char()
    office = fields.Char()
    passport_no = fields.Many2one('hr.documents')
    nationality = fields.Many2one('res.country')
    iqama_no = fields.Char("Iqama/ID No")
    expiry_date = fields.Date()
    issue_date = fields.Date()
    dob = fields.Date('Date of Birth')
    pob = fields.Char('Place of Birth')
    gosi_no = fields.Char('GOSI No', required=True)
    grops_id = fields.One2many('employee.payslip', 'grops_relation')

    @api.onchange('employee')
    def onchange_employee(self):
        if self.employee:
            self.employee_code = self.employee.employee_code
            self.department = self.employee.department_id.name
            self.office = self.employee.office.name
            self.passport_no = self.employee.passport_idd
            self.nationality = self.employee.country_id.id
            self.iqama_no = self.employee.iqama_num.iqama_no
            self.issue_date = self.employee.iqama_num.issue_date
            self.expiry_date = self.employee.iqama_num.expiry_date
            self.dob = self.employee.birthday
            self.pob = self.employee.place_of_birth


# Employee Leaving
class EOSLeaving(models.Model):
    _name = 'eos.leaving'
    _rec_name = 'employee'

    employee = fields.Many2one('hr.employee', required=True)
    employee_code = fields.Char()
    department = fields.Char()
    office = fields.Char()
    reason = fields.Char(required=True)
    requested_date = fields.Date()
    notice_date = fields.Date('Notice Start Date')
    end_date = fields.Date('Notice End Date')
    interview_date = fields.Date('Exit Interview Date')
    contact_person = fields.Char('GOSI No')
    description = fields.Char()
    employee_clearence_ref = fields.Many2one('employee.clearance', string="Employee Clearence Ref", readonly=True)

    @api.onchange('employee')
    def onchange_employee(self):
        if self.employee:
            self.employee_code = self.employee.employee_code
            self.department = self.employee.department_id.name
            self.office = self.employee.office.name
            self.contact_person = self.employee.gosi_no.gosi_no

    def create_emp_clearence(self):
        clearence_recs = self.env['employee.clearance'].search([])
        if self.employee_clearence_ref.id == 0:
            new = clearence_recs.create({'employee': self.employee.id})
            self.employee_clearence_ref = new
            self.employee_clearence_ref.employee_code = self.employee_code
            self.employee_clearence_ref.department = self.department
            self.employee_clearence_ref.office = self.office
            self.employee_clearence_ref.email = self.employee.work_email
            self.employee_clearence_ref.contact_phone = self.employee.work_phone

        else:
            self.employee_clearence_ref.employee = self.employee.id
            self.employee_clearence_ref.employee_code = self.employee_code
            self.employee_clearence_ref.department = self.department
            self.employee_clearence_ref.office = self.office
            self.employee_clearence_ref.email = self.employee.work_email
            self.employee_clearence_ref.contact_phone = self.employee.work_phone


# EOS
class EOS(models.Model):
    _name = 'employee.eos'
    _rec_name = 'employee'

    employee = fields.Many2one('hr.employee', required=True)
    department = fields.Char()
    job = fields.Char()
    contract = fields.Char()
    joining_date = fields.Date('Joining Date')
    leaving_date = fields.Date()
    employee_code = fields.Char()
    currency = fields.Char()
    year = fields.Char()
    date = fields.Date()
    type_d = fields.Char('Type')
    payslip = fields.Char()
    remaining_leave = fields.Float()
    no_year = fields.Char('No of Years')
    no_month = fields.Char('No of Months')
    no_days = fields.Char('No of Days')
    total_award = fields.Float()
    leave_balance = fields.Float()
    salary = fields.Float('Salary of Current Month')
    others = fields.Float()
    total_amount = fields.Float()

    @api.onchange('employee')
    def onchange_employee(self):
        if self.employee:
            self.department = self.employee.department_id.name
            self.job = self.employee.job_idd.job
            self.contract = self.employee.work_phone
            self.joining_date = self.employee.joining_date
            self.leaving_date = self.employee.leaving_date
            self.employee_code = self.employee.employee_code


# Contract
class Contract(models.Model):
    _inherit = 'hr.contract'

    employee_code = fields.Char()
    allow_mbl = fields.Boolean('Allow Mobile Allowance')
    sign_bonous = fields.Boolean('Sign on Bounus')
    loan_allow = fields.Boolean('Allow Loan Allowance')
    air_allow = fields.Boolean('Air Allowance')
    adults = fields.Integer('Adult(s)')
    job_idd = fields.Many2one('designation.info', string="Job Id")
    infants = fields.Integer()
    vac_des = fields.Many2one('vac_des.vac_des', string='Vacation Destination')
    package = fields.Float()
    gosi = fields.Boolean('GOSI')
    vehicle_attendance = fields.Integer('Vehicle Attendance')
    system_attendance = fields.Integer('System Attendance')
    line_manager_attendance = fields.Integer('Line Manager Attendance')
    incentive = fields.Float()
    expense_claim = fields.Float('Expense Claim')
    hr_visa_ticket = fields.Float('HR Visa/Ticket')
    other_allowances = fields.Float('Other Allowances', )
    advance_salary = fields.Float('Advance AGT Salary')
    hr_expense = fields.Float('Hr Expense')
    cash_sales = fields.Float('Cash Sales')
    traffic_fine = fields.Float('Traffic Fine')
    bk_balance = fields.Float('Bank Balance')
    other_deductions = fields.Float('Other Deductions')
    fn = fields.Char("First Name")
    ln = fields.Char("Last Name")
    dn = fields.Char("Display Name")
    e_date = fields.Date("Effective Date")
    hra = fields.Char("HRA")
    t_allow = fields.Float("Transport Allowance")
    f_allow = fields.Float("Food Allowance")
    f_ot = fields.Float("Fixed OT")
    departure = fields.Char("Departure Air Port")
    destination = fields.Char("Destination Air Port")

    status = fields.Selection([(
        'bachelor', 'Bachelor'),
        ('family', 'family')], string='Status')

    medical = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No')], string='Medical')

    c_accommodation = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No')], string='Company Accommodation')

    c_vehicle = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No')], string='Company Vehicle')

    c_vacation = fields.Selection([(
        '12', '12 Months'),
        ('18', '18 Months'),
        ('24', '24 Months')], string='Contractual Vacation')

    nod = fields.Selection([(
        '12', '12 Months'),
        ('18', '18 Months'),
        ('24', '24 Months')], string='Number of days')

    probation = fields.Selection([(
        '3', '3 Months'),
        ('6', '6 Months')], string='Probation')

    n_period = fields.Selection([(
        '1', '1 Months'),
        ('2', '2 Months'),
        ('3', '3 Months')], string='Notice Period')

    dependent = fields.Selection([(
        '1', '1+1 '),
        ('2', '1+2 '),
        ('3', '1+3 '),
        ('all', 'All ')], string='Dependent')

    incentive = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No')], string='Incentive')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.employee_code = self.employee_id.employee_code
            self.fn = self.employee_id.fn
            self.mn = self.employee_id.mn
            self.ln = self.employee_id.ln
            self.job_idd = self.employee_id.job_idd
            self.dn = self.employee_id.name

            if self.employee_id.gosi_no:
                self.gosi = True


# Insurance
class Insurance(models.Model):
    _name = 'hr.insurance'
    _rec_name = 'member_name'

    card_code = fields.Char(required=True)
    member_name = fields.Char(required=True)
    dob = fields.Date('Date of Birth', required=True)
    pob = fields.Char('Place of Birth')
    clas_n = fields.Char('Class')
    relation = fields.Many2one('relation.relation')
    premium = fields.Float()
    start_date = fields.Date()
    expiry_date = fields.Date("End Date")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ])

    insurance_relation = fields.Many2one('hr.employee')


# Trainings
class Trainings(models.Model):
    _name = 'hr.trainings'
    _rec_name = 'training_sum'

    training_sum = fields.Char('Training Summary')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    type_training = fields.Char('Type of Training')
    training_company = fields.Char('Training Company')
    training_place = fields.Char('Training Place')
    status = fields.Char()
    trainings_relation = fields.Many2one('hr.employee', string='Training Relation')


# Documents
class Documents(models.Model):
    _name = 'hr.documents'

    e_name = fields.Char("Employee Name")
    name = fields.Char("Doc Name", required=True)
    number = fields.Char("Doc No")
    type_d = fields.Many2one('documents.typed', 'Type', required=True)
    notes = fields.Char()
    place_issue = fields.Char("Place of Issue", required=True)
    issue_date = fields.Date("Issue Date", required=True)
    dor = fields.Date("Renewed Date")
    expiry_date = fields.Date("Expiry Date", required=True)
    nod = fields.Integer("No Of Days", required=True)
    dfr = fields.Integer("Due for Renewal", required=True)
    alert = fields.Char("Alert To")
    attach = fields.Binary("Attach File")
    remark = fields.Char("Remarks")
    status = fields.Char("Status")
    documents_relation = fields.Many2one('hr.employee')

    category = fields.Selection([(
        'gernal', 'Gernal'),
        ('positive', 'Positive'),
        ('negative', 'Negative')], required=True, string='Category')

    holder = fields.Selection([(
        'self', 'Self'),
        ('dep', 'Dependent')], required=True, string='Holder')


# IT Department
class ItDepartment(models.Model):
    _name = 'it.department'
    _rec_name = 'item'

    item = fields.Char()
    status = fields.Char()
    handled_by = fields.Char()
    remarks = fields.Char()
    department_relation = fields.Many2one('employee.clearance')


# Employee Payslip
class Payslip(models.Model):
    _name = 'employee.payslip'

    payslip = fields.Char()
    date = fields.Date()
    gosi_ammount = fields.Char('GOSI Amount')
    grops_relation = fields.Many2one('employee.grops')


#######################################
# ==>Helping Classes
#######################################

# office
class office(models.Model):
    _name = 'office.office'
    _rec_name = 'name'
    name = fields.Char()


# uni_name
class uni_name(models.Model):
    _name = 'uni_name.uni_name'
    _rec_name = 'name'
    name = fields.Char()


# vac_des
class vac_des(models.Model):
    _name = 'vac_des.vac_des'
    _rec_name = 'name'
    name = fields.Char()


# relation
class relation(models.Model):
    _name = 'relation.relation'
    _rec_name = 'name'
    name = fields.Char()


# religion
class religion(models.Model):
    _name = 'religion.religion'
    _rec_name = 'name'
    name = fields.Char()


# issue_place
class issue_place(models.Model):
    _name = 'issued_place.issued_place'
    _rec_name = 'name'
    name = fields.Char()


# documentstype
class xxdocumentstype(models.Model):
    _name = 'documents.typed'
    _rec_name = 'type_c'
    type_c = fields.Char('Type', required=True)


# project
class Project(models.Model):
    _name = 'projects.projects'
    _rec_name = 'name'
    name = fields.Char()


# Vehicle
class Vehicle(models.Model):
    _name = 'vehicles.vehicles'
    _rec_name = 'vehicle_model'
    vehicle_model = fields.Char("Vehicle Model")
    vehicle_no = fields.Char("Vehicle No")


class ResCompanyExt(models.Model):
    _inherit = 'res.company'

    _rec_name = 'location'

    flip = fields.Boolean("/ ")
    po_no = fields.Char(string="P.O Box No", required=True)
    location = fields.Char(string="Location Code")
    company_link = fields.One2many('res.company.tree1', 'company_tree', string="License Documents")
    sponsor_link = fields.One2many('res.sponsor', 'sponsor_tree', string="Sponsors")


class ResCompanyExtTree(models.Model):
    _name = 'res.company.tree1'

    doc_type = fields.Many2one('documents.typed', string="Doc Type")
    issue_date = fields.Date("Issue Date", required=True)
    latest_renewal_date = fields.Date("Latest Renewal Date")
    expiry_date = fields.Date("Expiry Date", required=True)
    renewal = fields.Date("Due for Renewal", required=True)
    company_tree = fields.Many2one('res.company')


class Sponsor(models.Model):
    _name = 'res.sponsor'

    name = fields.Char(string='Sponsor Name', required=True, store=True)
    sponsor_id = fields.Integer(string='Sponsor ID', required=True)
    partner_id = fields.Many2one('res.partner', string='Contact Person', required=True)
    cr_no = fields.Char(string='CR No')
    street = fields.Char()
    street2 = fields.Char()
    zip_code = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', string="Fed. State")
    country_id = fields.Many2one('res.country', string="Country")
    pob = fields.Char(string='P.O Box No')
    email = fields.Char(related='partner_id.email', store=True)
    phone = fields.Char(related='partner_id.phone', store=True)
    website = fields.Char(related='partner_id.website')
    fax = fields.Char(string="Fax")
    mobile = fields.Char(string='Mobile No')
    sponsor_tree = fields.Many2one('res.company')

    @api.onchange('state_id')
    def _onchange_state(self):
        self.country_id = self.state_id.country_id


class DivisionInfo(models.Model):
    _name = 'division.info'
    _rec_name = 'division'

    company_name = fields.Many2one('res.company', string="Company Name", required=True)
    branch_name = fields.Many2one('res.company', string="Branch Name")
    division = fields.Char("Division", required=True)


class DepartmentInfo(models.Model):
    _name = 'department.info'
    _rec_name = 'department'

    company_name = fields.Many2one('res.company', string="Company Name")
    branch_name = fields.Many2one('res.company', string="Branch Name")
    division = fields.Many2one('division.info', string="Division")
    department = fields.Char("Department", required=True)
    parent_dep = fields.Many2one('hr.department', "Parent Department")
    manager = fields.Many2one('hr.employee', "Manager", required=True)


class CategoryInfo(models.Model):
    _name = 'category.info'
    _rec_name = 'category'

    company_name = fields.Many2one('res.company', string="Company Name", required=True)
    branch_name = fields.Many2one('res.company', string="Branch Name")
    division = fields.Many2one('division.info', string="Division")
    department = fields.Many2one('department.info', string="Department")
    category = fields.Char("Category Info")


class DesignationInfo(models.Model):
    _name = 'designation.info'
    _rec_name = 'job'

    company_name = fields.Many2one('res.company', string="Company Name", required=True)
    branch_name = fields.Many2one('res.company', string="Branch Name")
    division = fields.Many2one('division.info', string="Division")
    department = fields.Many2one('department.info', string="Department")
    category = fields.Many2one('category.info', string="Category Info")
    job = fields.Char("Job Title", required=True)
    profession = fields.Char("ID Profession", required=True)


class DocumentList(models.Model):
    _name = 'document.list'

    name = fields.Char("Document Name", required=True)
    alert = fields.Char("Alert Days", required=True)
    category = fields.Selection([(
        'com', 'Company'),
        ('emp', 'Employee'),
        ('asst', 'Asset')], required=True, string='Category')


class CompanyDocument(models.Model):
    _name = 'document.com'

    comp_name = fields.Many2one('res.company', string="Company Name", required=True)
    bran_name = fields.Many2one('res.company', string="Branch Name", required=True)
    bran_code = fields.Char(string="Branch Code", required=True)
    name = fields.Char("Doc Name", required=True)
    doc_no = fields.Char("Doc No")
    poi = fields.Char("Place of Issue", required=True)
    doi = fields.Date("Issue Date", required=True)
    dor = fields.Date("Renewed Date")
    doe = fields.Date("Expiry Date", required=True)
    nod = fields.Integer("No Of Days", required=True)
    dfr = fields.Integer("Due for Renewal", required=True)
    alert = fields.Char("Alert To")
    attach = fields.Binary("Attach File")
    remark = fields.Char("Remarks")

    @api.onchange('bran_name')
    def _onchange_branch(self):
        self.bran_code = self.bran_name.id

    @api.model
    def create(self, vals):
        vals['doc_no'] = self.env['ir.sequence'].next_by_code('document.com')
        new_record = super(CompanyDocument, self).create(vals)

        return new_record


class AssetsDocument(models.Model):
    _name = 'document.asset'

    name = fields.Char("Doc Name", required=True)
    doc_no = fields.Char("Doc No")
    doc_type = fields.Many2one('documents.typed', string="Doc Type")
    dor = fields.Date("Renewed Date")
    doe = fields.Date("Expiry Date", required=True)
    nod = fields.Integer("No Of Days", required=True)
    dfr = fields.Integer("Due for Renewal", required=True)
    alert = fields.Char("Alert To")
    attach = fields.Binary("Attach File")
    remark = fields.Char("Remarks")
    documents_relation = fields.Many2one('maintenance.equipment')


class AssetsDocumentExt(models.Model):
    _inherit = 'maintenance.equipment'

    documents_id = fields.One2many('document.asset', 'documents_relation', string="Documents")
    make = fields.Char("Make")
    owner_user_id = fields.Many2one('hr.employee')
    model = fields.Char("Model")
    color = fields.Char("Color")
    plate_no = fields.Char("Plate No")
    door_no = fields.Char("Door No")
    chasi_no = fields.Char("Chassis No")
    reg_no = fields.Char("Registration No")
    s_name = fields.Many2one('res.sponsor', string="Sponsor")
    sponsor = fields.Char(string="Sponsor Name")
    location = fields.Char("Location")
    p_price = fields.Char("Purchase Price")
    i_value = fields.Char("Insured Value")
    sponsor_id = fields.Many2one('res.sponsor', string="Sponsor ID")
    c_name = fields.Many2one('res.company', string="Company Name")
    cr_no = fields.Char("Insured Value")
    lease_expiry = fields.Date(string="Lease Expiry")
    remark = fields.Char("Remarks")

    ownership = fields.Selection([(
        'own', 'Owned'),
        ('leas', 'Leased')], default='own', string='Ownership')

    @api.onchange('s_name')
    def _onchange_s_name(self):
        self.sponsor = self.s_name.sponsor_id


class HRTicket(models.Model):
    _name = 'hr.ticket'

    name = fields.Many2one('hr.employee', "Employee Name", required=True)
    emp_no = fields.Char("Employee No", required=True)
    leave_from = fields.Char("Leave From", required=True)
    leave_to = fields.Char("Leave To", required=True)
    fn = fields.Char("First Name", required=True)
    mn = fields.Char("Middle Name", required=True)
    ln = fields.Char("Last Name", required=True)
    dob = fields.Date("DOB", required=True)
    pob = fields.Char('Place of Birth')
    mobile = fields.Char("Mobile No", required=True)
    contact_no = fields.Char("Contact No", required=True)
    nationality = fields.Many2one('res.country', "Nationality", required=True)
    passport = fields.Many2one('hr.documents', "Passport No", required=True)
    issue = fields.Date("Issue Date", required=True)
    expiry = fields.Date("Expiry Date", required=True)
    departure = fields.Char("Departure Air Port", required=True)
    destination = fields.Char("Destination Air Port", required=True)
    departure_date = fields.Date("Departure Date", required=True)
    return_date = fields.Date("Return Date", required=True)
    remarks = fields.Char("Remarks", required=True)
    dependent_id = fields.One2many('hr.ticket.dependent', 'dependent_ticket', string="Dependent")
    reissue_ticket = fields.One2many('hr.ticket.reissue', 'reissue_ticket', string="Re issue")
    create_book = fields.Boolean("Create Booking")
    conf_book = fields.Boolean("Confirm Booking")
    re_issue = fields.Boolean("Re Issue")
    cancel_ticket = fields.Boolean("Cancel Ticket")
    req_no = fields.Char("Request No", required=True)
    agent = fields.Char("Travel Agent", required=True)
    book_date = fields.Date("Booking Date", required=True)
    book_by = fields.Char("Booked By", required=True)
    piad_amt = fields.Float("Paid Amount", required=True)
    receive_date = fields.Date("Received Date", required=True)
    cutt_date = fields.Date("Cutt Off Date", required=True)
    desc = fields.Char("Description", required=True)
    attach = fields.Binary("Attach", required=True)
    sent_by = fields.Char("Sent for confirmation By", required=True)
    sent_by_date = fields.Char("Sent for confirmation Date", required=True)

    priority = fields.Selection([(
        'critical', 'Critical'),
        ('high', 'High'),
        ('normal', 'Normal')], required=True, string='Priority')

    break_jun = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No'), ], string="Break Journey", required=True)

    receive = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No'), ], string="Booking Received", required=True)

    status = fields.Selection([(
        'bachelor', 'Bachelor'),
        ('family', 'Family')], required=True, string='Status')

    dependent = fields.Selection([(
        '1', '1+1 '),
        ('2', '1+2 '),
        ('3', '1+3 '),
        ('all', 'All ')], required=True, string='Dependent')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string="Gender", required=True)
    cancellation = fields.Selection([(
        'full', 'Full Ticket'),
        ('part', 'Part Ticket'), ], string="Cancel Ticket", required=True)

    refund = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No'), ], string="Refundable", required=True)
    cnr = fields.Char("Credit Note Number")

    @api.onchange('conf_book')
    def _onchange_conf_book(self):
        if self.conf_book == True:
            self.create_book = False

    @api.onchange('create_book')
    def _onchange_create_book(self):
        if self.create_book == True:
            self.conf_book = False

    @api.onchange('name')
    def _onchange_name(self):

        dent = self.env['hr.contract'].search([('employee_id', '=', self.name.id)])

        self.dependent = dent.dependent
        self.status = dent.status
        self.emp_no = self.name.employee_code
        self.fn = self.name.fn
        self.mn = self.name.mn
        self.ln = self.name.ln
        self.gender = self.name.gender
        self.dob = self.name.birthday
        # self.pob = self.name.pob
        self.mobile = self.name.mobile_phone
        self.contact_no = self.name.work_phone
        self.nationality = self.name.country_id
        self.passport = self.name.passport_idd
        self.issue = self.name.iqama_num.issue_date
        self.expiry = self.name.iqama_num.expiry_date
        # self.remarks = self.name.e_remark

        if self.name.dependent_id:
            dependent_list = []
            for x in self.name.dependent_id:
                dependent_list.append({
                    'passport': x.d_passport,
                    'dob': x.dob,
                    'fn': x.fn,
                    'mn': x.mn,
                    'ln': x.ln,
                    'ticket_req': 'yes',
                    'name': x.name,
                })
            self.dependent_id = dependent_list
            dependent_list = []


class HRTicketDependent(models.Model):
    _name = 'hr.ticket.dependent'

    name = fields.Char('Name(As in Passport)')
    passport = fields.Many2one('hr.documents', "Passport No", required=True)
    dob = fields.Date('Date of Birth', required=True)
    pob = fields.Char('Place of Birth')
    date_issue = fields.Date('Date of Issue')
    date_expiry = fields.Date('Date of Expiry')
    nationality = fields.Many2one('res.country', "Nationality")
    fn = fields.Char("First Name", required=True)
    mn = fields.Char("Middle Name", required=True)
    ln = fields.Char("Last Name", required=True)
    departure_date = fields.Date("Departure Date", required=True)
    return_date = fields.Date("Return Date", required=True)
    dependent_ticket = fields.Many2one('hr.ticket')

    ticket_req = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No'), ], default='yes', string="Ticket Required", required=True)


class HRTicketReissue(models.Model):
    _name = 'hr.ticket.reissue'

    departure = fields.Char("Departure Air Port", required=True)
    destination = fields.Char("Destination Air Port", required=True)
    departure_date = fields.Date("Departure Date", required=True)
    return_date = fields.Date("Return Date", required=True)
    reasons = fields.Char("Reasons")
    reissue_ticket = fields.Many2one('hr.ticket')

    change_sec = fields.Selection([(
        'yes', 'Yes'),
        ('no', 'No'), ], default='yes', string="Change Sector", required=True)


class HRExitReentry(models.Model):
    _name = 'hr.exit.reentry'

    name = fields.Many2one('hr.employee', "Employee Name", required=True)
    nationality = fields.Many2one('res.country', "Nationality", required=True)
    department = fields.Many2one('hr.department', string="Department", required=True)
    rejoin_date = fields.Date("Rejoin Date", required=True)
    leave_date = fields.Date("Leave Date", required=True)
    leave_from = fields.Char("Leave From", required=True)
    leave_to = fields.Char("Leave To", required=True)
    govt_fee = fields.Float("Govt. Fee", required=True)

    leave_type = fields.Selection([(
        'contract', 'Contractual Leave'),
        ('emergency', 'Emergency Leave'),
        ('medical', 'Medical Leave'),
        ('others', 'Others'), ], string="Leave Type", required=True)

    months = fields.Selection([(
        '1', '1 Months'),
        ('2', '2 Months'),
        ('3', '3 Months'),
        ('4', '4 Months'),
        ('5', '5 Months'),
        ('6', '6 Months')], required=True, string='Months')

    paid_by = fields.Selection([(
        'personnel', 'personnel'),
        ('office', 'Office'), ], string="Paid By", required=True)

    stage = fields.Selection([(
        'new', 'Issue New'),
        ('wait', 'Waiting For Payment'),
        ('done', 'Done'), ], default='new')

    def in_wait(self):
        self.stage = "wait"

    def in_done(self):
        self.stage = "done"

    def cancel(self):
        self.stage = "new"

    @api.onchange('name')
    def _onchange_employee(self):
        self.nationality = self.name.country_id
        self.department = self.name.department_id


class HRHolidays(models.Model):
    _inherit = 'hr.leave'

    replace_by = fields.Many2one('hr.employee', "Replace By")
    emp_id = fields.Integer("id")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    attachment = fields.Binary(string="Attachment")
    re_entry_req = fields.Selection(string="Re-Entry Required ?", selection=[('yes', 'Yes'), ('no', 'No')])
    vacation_days = fields.Char(string="Vacation Days")

    @api.onchange('start_date', 'end_date')
    def days_between(self):
        if self.start_date and self.end_date:
            d1 = datetime.strptime(self.start_date, "%Y-%m-%d")
            d2 = datetime.strptime(self.end_date, "%Y-%m-%d")
            days = abs((d2 - d1).days)
            self.number_of_days_temp = days

    @api.onchange('employee_id')
    def _onchange_employee(self):
        self.department_id = self.employee_id.department_id
        self.emp_id = self.employee_id.id


class HRDep(models.Model):
    _inherit = 'hr.department'

    dep_link = fields.Many2one('department.info')

    @api.model
    def create(self, vals):
        new_record = super(HRDep, self).create(vals)
        data = self.env['department.info'].create({
            'department': new_record.name,
            'parent_dep': new_record.parent_id.id,
            'manager': new_record.manager_id.id,

        })
        new_record.dep_link = data.id

        return new_record

    def write(self, vals):
        super(HRDep, self).write(vals)
        if self.dep_link:
            self.dep_link.department = self.name
            self.dep_link.parent_dep = self.parent_id.id
            self.dep_link.manager = self.manager_id.id

        return True

    def unlink(self):
        self.dep_link.unlink()
        super(HRDep, self).unlink()
        return True


class Status(models.Model):
    _name = 'status'
    _rec_name = 'name'

    name = fields.Char(string="Status", required=True)

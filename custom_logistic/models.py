# -*- coding: utf-8 -*-
import re
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PortTerminal(models.Model):
    _name = 'port.terminal'
    _rec_name = 'name'

    name = fields.Char('Terminal Name', required=True)


class ExportLogic(models.Model):
    _name = 'export.logic'
    _rec_name = 'sr_no'

    customer = fields.Many2one('res.partner', string="Customer", required=True)
    by_customer = fields.Many2one('by.customer', string="By Customer", requried=True)
    sr_no = fields.Char(string="SR No", readonly=True)
    bill_bol = fields.Boolean(string="B/L")
    cont_bol = fields.Boolean(string="Cont")
    contain = fields.Boolean(string="Contain")
    bill_types = fields.Selection([('B/L Number', 'B/L Number'), ('Container Wise', 'Container Wise')],
                                  string="Billing Type")
    our_job_no = fields.Char(string="Our Job No", readonly=True, )
    customer_ref = fields.Char(string="Customer Ref")
    cust_ref_inv = fields.Char(string="Customer Ref Inv No")
    shipper_date = fields.Date(string="DOC Received Date", default=date.today())
    mani_date = fields.Date(string="Manifest Received Date")
    date = fields.Date(string="Date", required=True, default=date.today())
    bill_no = fields.Char(string="B/L Number")
    rot_no = fields.Char(string="Rotation Number/Sequence Number")
    bill_attach = fields.Binary(string=" ")
    eta = fields.Date(string="ETA")
    etd = fields.Date(string="ETD")
    about = fields.Char(string="On Or About")
    bayan_no = fields.Char(string="Bayan No")
    bayan_attach = fields.Binary(string=" ")
    final_bayan = fields.Char(string="Final Bayan")
    final_attach = fields.Binary(string="Final Bayan")
    pre_bayan = fields.Date(string="Pre Bayan Date")
    custom_exam = fields.Boolean(string="Open Custom Examination")
    bayan_date = fields.Date(string="Initial Bayan Date")
    filed_officer = fields.Many2one('filed.officer', string="Assign to", required=False)
    shutl_start_date = fields.Date(string="Shuttling Start Date")
    fin_bayan_date = fields.Date(string="Final Bayan Date")
    shutl_end_date = fields.Date(string="Shuttling End Date")
    acc_link = fields.Many2one('account.move', string="Invoice", readonly=True)
    status = fields.Many2one('import.status', string="Status")
    fri_id = fields.Many2one('freight.forward', string="Freight Link")
    site = fields.Many2one('import.site', string="Site", required=True)
    remarks = fields.Text(string="Remarks")
    vessel_date = fields.Date(string="Vessel Arrival Date")
    vessel_name = fields.Char(string="Vessel Name")
    s_supplier = fields.Many2one('res.partner', string="Shipping Line")
    export_link = fields.One2many('logistic.export.tree', 'export_tree')
    export_id = fields.One2many('export.tree', 'crt_tree')
    export_serv = fields.One2many('logistic.service.tree', 'service_tree')
    cont_serv = fields.One2many('logistic.contain.tree', 'service_tree_cont')
    tick = fields.Boolean()
    export_other_charges = fields.One2many('import.other_charges', 'export_tree')
    export_gov_charges = fields.One2many('gov.charges', 'export_tree')
    tos = fields.Many2many(comodel_name="sale.order", string="Transportation Orders", )
    warn_invoice = fields.Integer(string="Warn Invoice", )
    house_bl = fields.Char(string="House B/L")
    terminal = fields.Many2one('port.terminal', string="Terminal")
    port = fields.Many2one(comodel_name="res.port", string="Port", required=False, )
    no_invoice = fields.Boolean(string="No Invoice", )
    to_mails = fields.Char(string="mail To", required=False, )
    container_num = fields.Char(string="Container Num", required=False, store=True, compute="_compute_container_num")

    demurrage = fields.Date(string="Demurrage Date", store=True, default=datetime.today())
    free_time_days = fields.Integer(string="Free Time Days", default='10')
    detention_date = fields.Date(string="Detention Date", store=True,
                                 compute='_compute_export_demurrage_detention_dates')

    @api.onchange('vessel_date')
    def _onchange_demurrage(self):
        for file in self:
            if file.vessel_date:
                file.demurrage = (datetime.strptime(str(file.vessel_date), '%Y-%m-%d') + timedelta(days=5)).date()

    @api.depends('vessel_date', 'free_time_days')
    def _compute_export_demurrage_detention_dates(self):
        for rec in self:
            if rec.vessel_date and rec.free_time_days:
                rec.detention_date = (datetime.strptime(str(rec.vessel_date), '%Y-%m-%d') +
                                       timedelta(days=rec.free_time_days)).date()


    @api.depends('state')
    def _compute_sale_order(self):
        for rec in self:
            if rec.state == 'done':
                rec.tos = self.env['sale.order'].search([('partner_id', '=', rec.customer.id),
                                                      ('sales_id', '=', rec.id),
                                                      ('bill_no', '=', rec.bill_no)]).ids
            else:
                rec.tos = False


    @api.depends('export_id')
    def _compute_container_num(self):

        """
        @api.depends() should contain all fields that will be used in the calculations.
        """
        for rec in self:
            crt_list = []
            if rec.export_id:
                for x in rec.export_id:
                    if x.crt_no:
                        crt_list.append(x.crt_no.encode('ascii', 'ignore'))
                rec.container_num = crt_list

    state = fields.Selection([
        ('pre', 'Pre Bayan'),
        ('initial', 'Initial Bayan'),
        ('final', 'Final Bayan'),
        ('done', 'Done'),
    ], default="pre")

    _sql_constraints = [
        ('customer_ref', 'unique(customer_ref)', 'This customer reference already exists!')]

    def create_account_journal(self):
        if not self.env['account_journal.configuration'].search([]):
            record = self.env['account_journal.configuration'].create({
                'name': "Accounts and Journals Configuration"
            })

    @api.onchange('customer', 'by_customer', 'bill_types', 'port')
    def get_tree_value(self):
        """Get Billing Type of Selected customer, get data in Custom Chargers Tree according to customer and by_
        Customer"""

        if self.customer:
            # self.bill_types = self.customer.bill_type
            if self.bill_types == "B/L Number":
                self.bill_bol = True
                self.cont_bol = False
                inv = []
                for x in self.customer.bl_id:
                    if self.by_customer == x.by_customer:
                        # / Delete Previous Records in Custom Charges Tree/
                        delete = []
                        delete = delete.append(2)
                        self.export_serv = delete

                        for invo in x:
                            inv.append({
                                'sevr_charge': invo.charges_serv,
                                'sevr_type': invo.charges_type.id,
                                'service_tree': self.id,
                            })

                self.export_serv = inv
            if self.bill_types == "Container Wise":
                self.cont_bol = True
                self.bill_bol = False
                inv = []
                for x in self.customer.cont_id:
                    if self.by_customer == x.by_customer and x.service_type == 'export' and self.port == x.port:
                        delete = []
                        delete = delete.append(2)
                        self.cont_serv = delete
                        # / Delete Previous Records in Custom Charges Tree/

                        for invo in x:
                            inv.append({
                                'sevr_charge_cont': invo.charges_serv,
                                'sevr_type_cont': invo.charges_type.id,
                                'type_contt': invo.cont_type,
                                'service_tree_cont': self.id,
                            })

                self.cont_serv = inv

    @api.model
    def create(self, vals):
        """SR No Sequence"""
        vals['sr_no'] = self.env['ir.sequence'].next_by_code('export.logics')
        vals['our_job_no'] = self.env['ir.sequence'].next_by_code('export.job.num')
        new_record = super(ExportLogic, self).create(vals)

        return new_record

    # @api.onchange('export_id')
    # def onchange_method_export_id(self):
    #     print(self.export_id)
    #     for counter, x in enumerate(self.export_id, 0):
    #         x.number = x.number + counter
    #         print(x.number)

    def initialbay(self):
        for rec in self:
            rec.state = "initial"

    def finalbay(self):
        for rec in self:
            rec.state = "final"

    def over(self):
        for rec in self:
            rec.state = "done"

    def create_sale(self):
        for rec in self:
            """Create Transport Order"""

            if not rec.tos and not rec.acc_link:
                # / Get Product having name is Container/
                value = self.env['product.template'].search([('name', '=', 'Transportation Charge')])[0].id
                # / Create Transport Order/
                for data in rec.export_id:
                    if data.crt_no:
                        records = self.env['sale.order'].create({
                            'partner_id': rec.customer.id,
                            'by_customer': rec.by_customer.id,
                            'date_order': date.today(),
                            'bill_type': rec.bill_types,
                            'bill_no': rec.bill_no,
                            'suppl_name': data.transporter.id,
                            'suppl_freight': data.trans_charge,
                            'form': data.form.name,
                            'to': data.to.name,
                            'sales_id': rec.id,
                            'our_job': rec.our_job_no,
                            'sr_no': rec.sr_no,
                            'customer_ref': rec.customer_ref,
                            'custom_dec': '',
                            'bayan_no': rec.bayan_no,
                            'customer_site': rec.site.id,
                            'final_date': rec.fin_bayan_date,
                            'no_invoice': True,
                            'demurrage': rec.demurrage,
                        })

                        records.order_line.create({
                            'product_id': value,
                            'weight': data.weight,
                            'name': 'Container',
                            'product_uom_qty': 1.0,
                            'price_unit': data.custm_charge,
                            'crt_no': data.crt_no,
                            'product_uom': 1,
                            'order_id': records.id,
                            'form': data.form.id,
                            'to': data.to.id,
                            'fleet_type': data.fleet_type.id,
                        })
                email_rec = self.env['multi.mails'].search([])
                template = self.env.ref('custom_logistic.cct_email_template_1')
                for email in email_rec.sale_support:
                    rec.to_mails = email.name
                    self.env['mail.template'].browse(template.id).send_mail(rec.id)
            else:
                raise UserError(_('Transportation or Invoice is Already Created'))

    def get_order_name(self, sale_ids):
        for rec in self:
            return str([sale.name.encode('ascii', 'ignore') for sale in sale_ids]).replace('[', '').replace(']','').replace("'",'')

    def create_custom_charges(self):
        """ Creating the invoice as per billing type B/L or Container wise"""
        for rec in self:

            if rec.warn_invoice == 0:
                rec.warn_invoice += 1
                view = self.env.ref('sh_message.sh_message_wizard').id
                context = dict(rec._context or rec)
                context['message'] = "Do you Really Want To Create Invoice, If yes then click Create Invoice Button Again."
                return {'name': 'Warning',
                        'type': 'ir.actions.act_window',

                        'view_mode': 'form',
                        'res_model': 'sh.message.wizard',
                        'views': [(view, 'form')],
                        'view_id': view,
                        'target': 'new',
                        'context': context,
                        }

            sale = self.env['sale.order'].search([('sales_id', '=', rec.id)])
            check = 0
            for x in sale:
                if x.state == 'done':
                    check += 1

            if check == len(sale):
                if not rec.acc_link and not rec.fri_id:
                    create_invoice = ''
                    account = self.env['account_journal.configuration'].search([])
                    invoice = self.env['account.move'].search([])
                    invoice_lines = self.env['account.move.line'].search([])
                    # / B/L Wise invoice/

                    if rec.bill_types == "B/L Number":
                        create_invoice = invoice.create({
                            'journal_id': account.e_invoice_journal.id,
                            'partner_id': rec.customer.id,
                            'by_customer': rec.by_customer.id,
                            'date_invoice': date.today(),
                            'billng_type': rec.bill_types,
                            'bill_num': rec.bill_no,
                            'our_job': rec.our_job_no,
                            'sr_no': rec.sr_no,
                            'customer_ref': rec.customer_ref,
                            'custom_dec': '',
                            'bayan_no': rec.bayan_no,
                            'customer_site': rec.site.id,
                            'final_date': rec.fin_bayan_date,
                            'type': 'out_invoice',
                            'invoice_from': 'exp',
                            'export_link': rec.id,
                            'property_account_receivable_id': rec.customer.property_account_receivable_id.id,
                        })

                        for x in rec.export_serv:
                            create_invoice_lines = invoice_lines.create({
                                'quantity': 1,
                                'price_unit': x.sevr_charge,
                                'account_id': account.e_invoice_account.id,
                                'name': x.sevr_type.name,
                                'move_id': create_invoice.id,
                                # 'invoice_line_tax_ids': [1],
                            })

                    # / B/L Wise invoice/
                    if rec.bill_types == "Container Wise":
                        data = []
                        for x in rec.export_id:
                            if x.types not in data:
                                data.append(x.types)

                        create_invoice = invoice.create({
                            'journal_id': account.e_invoice_journal.id,
                            'partner_id': rec.customer.id,
                            'by_customer': rec.by_customer.id,
                            'date_invoice': date.today(),
                            'billng_type': rec.bill_types,
                            'bill_num': rec.bill_no,
                            'our_job': rec.our_job_no,
                            'sr_no': rec.sr_no,
                            'customer_ref': rec.customer_ref,
                            'custom_dec': '',
                            'bayan_no': rec.bayan_no,
                            'customer_site': rec.site.id,
                            'final_date': rec.fin_bayan_date,
                            'type': 'out_invoice',
                            'invoice_from': 'exp',
                            'export_link': rec.id,
                            'property_account_receivable_id': rec.customer.property_account_receivable_id.id,
                        })

                        for line in data:
                            value = 0
                            for x in rec.export_id:
                                if x.types == line:
                                    value = value + 1
                            get_unit = 0
                            get_type = ' '
                            for y in rec.cont_serv:
                                if y.type_contt == line:
                                    get_unit = y.sevr_charge_cont
                                    get_type = y.sevr_type_cont.name

                            create_invoice_lines = invoice_lines.create({
                                'quantity': value,
                                'price_unit': get_unit,
                                'account_id': account.e_invoice_account.id,
                                'name': 'Custom Clearance Charges  -   اجور تخليص  الجمركي',
                                'service_type': get_type,
                                'move_id': create_invoice.id,
                                # 'invoice_line_tax_ids': [1],
                            })

                    for x in rec.export_other_charges:
                        create_invoice_lines = invoice_lines.create({
                            'quantity': 1,
                            'price_unit': x.charges,
                            'account_id': account.e_invoice_account.id,
                            'name': x.name.name,
                            'move_id': create_invoice.id,
                        })

                    for x in rec.export_gov_charges:
                        create_invoice_lines = invoice_lines.create({
                            'quantity': 1,
                            'price_unit': x.charges,
                            'account_id': account.g_invoice_account.id,
                            'name': x.name.name,
                            'move_id': create_invoice.id,
                        })
                    rec.acc_link = create_invoice.id

                    if rec.tos:
                        for x in rec.tos:
                            x.invoice_status = 'invoiced'
                            create_invoice.invoice_line_ids.create({
                                'quantity': 1,
                                'price_unit': x.amount_total,
                                'account_id': account.same_custom_invoice_account.id,
                                'name': str(x.name) + " Transportation Charges" + ' اجور نقل '.decode('utf-8'),
                                'crt_no': x.order_line.crt_no,
                                'move_id': create_invoice.id
                            })

                            if x.pullout_type == 'Customer':
                                create_invoice.invoice_line_ids.create({
                                    'quantity': 1,
                                    'price_unit': x.partner_id.pullout_charges,
                                    'account_id': account.t_pullout_account.id,
                                    'name': str(x.name) + " PullOut Charges",
                                    'move_id': create_invoice.id
                                })

                            if x.pull_out and x.pullout_status == 'Completed':
                                if datetime.now().date() >= (
                                        datetime.strptime(str(x.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                                    days=x.partner_id.free_day)).date():
                                    day = datetime.now().date() - (
                                            datetime.strptime(str(x.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                                        days=x.partner_id.free_day)).date()

                                    if day.days > 0:
                                        create_invoice.invoice_line_ids.create({
                                            'quantity': day.days,
                                            'price_unit': x.partner_id.storage_charges,
                                            'account_id': account.t_storage_account.id,
                                            'name': "Storage Charges for " + str(day.days) + " Days",
                                            'move_id': create_invoice.id
                                        })

                    # vendor bill creation
                    partner = self.env['res.partner'].search([('name', '=', 'Government Charges Vendor')])

                    if rec.export_gov_charges:
                        create_invoice = self.env['account.move'].create({
                            'journal_id': account.g_invoice_journal.id,
                            'partner_id': partner.id,
                            'date_invoice': date.today(),
                            'type': 'in_invoice',
                            'export_link': rec.id,
                            'invoice_from': 'exp',
                            'account_id': partner.property_account_payable_id.id
                        })
                        for x in rec.export_gov_charges:
                            create_invoice_lines = create_invoice.invoice_line_ids.create({
                                'quantity': 1,
                                'price_unit': x.charges,
                                'account_id': account.g_invoice_account.id,
                                'name': x.name.name,
                                'move_id': create_invoice.id,
                            })
                    email_rec = self.env['multi.mails'].search([])
                    template = self.env.ref('custom_logistic.tie_email_template')
                    for email in email_rec.finance:
                        rec.to_mails = email.name
                        self.env['mail.template'].browse(template.id).send_mail(rec.id)
                else:
                    raise UserError(_('Invoice Is Already Created or Maybe This Export Is Linked With Project.'))
            else:
                raise UserError(_('Transportation in Process Wait until Transport order not complete'))


class logistics_export_tree(models.Model):
    _name = 'logistic.export.tree'

    container_no = fields.Char(string="Container No.", required=True)
    new_seal = fields.Char(string="New Seal No")
    broker = fields.Many2one('res.partner', string="Broker")
    amt_paid = fields.Float(string="Paid Amount")
    export_tree = fields.Many2one('export.logic')


class service_export_tree(models.Model):
    _name = 'logistic.service.tree'

    sevr_type = fields.Many2one('serv.types', string="Service Type")
    sevr_charge = fields.Integer(string="Service Charges")
    service_tree = fields.Many2one('export.logic')


class service_cont_tree(models.Model):
    _name = 'logistic.contain.tree'

    sevr_type_cont = fields.Many2one('serv.types', string="Service Type")
    sevr_charge_cont = fields.Integer(string="Service Charges")
    type_contt = fields.Char(string="Container Size")
    service_tree_cont = fields.Many2one('export.logic')


class FiledOfficer(models.Model):
    _name = 'filed.officer'

    name = fields.Char(string="Filed Officer Name", required=True)



    def unlink(self):
        for rec in self:
            if self.env['export.logic'].search_count([('filed_officer', '=', rec.id)]):
                raise ValidationError('filed officer is in use you can not Delete')
            return super(FiledOfficer, self).unlink()


class export_tree(models.Model):
    _name = 'export.tree'

    crt_no = fields.Char(string="Container No.", size=11)
    weight = fields.Float()
    des = fields.Char(string="Description", required=False, )
    form = fields.Many2one('from.qoute', string="From")
    to = fields.Many2one('to.quote', string="To")
    fleet_type = fields.Many2one('fleet', string="Fleet Type")
    transporter = fields.Many2one('res.partner', string="Transporter", required=False, )
    trans_charge = fields.Char(string="Transporter Charges")
    custm_charge = fields.Char(string="Customer Charges")
    types = fields.Selection([
        ('20 ft', '20 ft'),
        ('40 ft', '40 ft')], string="Size")

    crt_tree = fields.Many2one('export.logic')
    p_date = fields.Date(string="Pay Date", required=False, )
    amount = fields.Float(string="Deposit Amount", required=False, )
    status = fields.Selection(string="Status", selection=[('Waiting EIR', 'Waiting EIR'),
                                                          ('Under Refunding', 'Under Refunding'),
                                                          ('Refunded', 'Refunded'), ], required=False, )
    e_date = fields.Date(string="EIR Date", required=False, )

    @api.onchange('crt_no')
    def container_no_check_onchange(self):
        if self.crt_no:
            if re.match('^[A-Z]{4}[0-9]{7,}$', self.crt_no.upper()):
                self.crt_no = self.crt_no.upper()
            else:
                raise ValidationError("You have Entered a Wrong Container Number or Format: %s \nFormat is AAAA0000000"
                                      "\nFirst Four Character Must be Alphabet and Last Seven Character Must be Numeric"
                                      % self.crt_no.upper())

    @api.constrains('crt_no')
    def container_no_check_constrains(self):
        if self.crt_no:
            if re.match('^[A-Z]{4}[0-9]{7,}$', self.crt_no.upper()):
                return True
            else:
                raise ValidationError("You have Entered a Wrong Container Number or Format: %s \nFormat is AAAA0000000,"
                                      "\nFirst Four Character Must be Alphabet and Last Seven Character Must be Numeric"
                                      % self.crt_no.upper())

    @api.onchange('transporter', 'form', 'to', 'fleet_type')
    def add_charges(self):
        """ Calculating Charges As per Transporter, To, From, and fleet_type for selected customer"""

        if self.transporter.id and self.form.id and self.to.id and self.fleet_type:
            trans = self.env['res.partner'].search([('id', '=', self.transporter.id)])
            for x in trans.route_id:
                if self.form.id == x.form.id and self.to.id == x.to.id and self.fleet_type == x.fleet_type and x.service_type == "export":
                    self.trans_charge = x.trans_charges
            rec = self.env['res.partner'].search([('id', '=', self.crt_tree.customer.id)])
            for x in rec.route_id:
                if self.form.id == x.form.id and self.to.id == x.to.id and self.fleet_type == x.fleet_type and x.service_type == "export":
                    self.custm_charge = x.trans_charges


# ===========================================Import-Start===============================
# ===========================================Import-Start===============================


class ImportLogic(models.Model):
    _name = 'import.logic'
    _rec_name = 's_no'

    delivery_date = fields.Date(string="Arrival Date", compute='_compute_dates')
    delivery = fields.Date(string="Delivery Date", compute='_compute_dates')
    eir_date = fields.Date(string="EIR Date", compute='_compute_dates')



    def _compute_dates(self):
        for rec in self:
            # rec.ensure_one()
            sales_order = self.env['sale.order'].search([('sales_imp_id', '=', rec.id)], limit=1,
                                                        order='create_date desc')

            for item in sales_order:
                if sales_order:
                    rec.delivery_date = item.delivery_date
                    rec.delivery = item.delivery
                    rec.eir_date = item.eir_date
            else:
                rec.delivery_date = False
                rec.delivery = False
                rec.eir_date = False


    customer = fields.Many2one('res.partner', string="Customer", required=True)
    by_customer = fields.Many2one('by.customer', string="By Customer")
    # bill_types = fields.Char(string="Billing Type")
    bill_types = fields.Selection([('B/L Number', 'B/L Number'), ('Container Wise', 'Container Wise')],
                                  string="Billing Type")
    bill_bol = fields.Boolean(string="B/L")
    contt_bol = fields.Boolean(string="B/L")
    contain = fields.Boolean(string="Contain")
    s_no = fields.Char(string="SR No", readonly=True)
    job_no = fields.Char(string="Job No", readonly=True)
    date = fields.Date(string="Date", required=True, default=date.today())
    customer_ref = fields.Char(string="Customer Ref")
    cust_ref_inv = fields.Char(string="Customer Ref Inv No")
    site = fields.Many2one('import.site', string="Site", required=True)
    fri_id = fields.Many2one('freight.forward', string="Freight Link")
    shipper_date = fields.Date(string="By Email DOC Received Date", default=date.today())
    org_date = fields.Date(string="Original DOC Received Date")
    vessel_date = fields.Date(string="Vessel Arrival Date")
    vessel_name = fields.Char(string="Vessel Name")
    s_supplier = fields.Many2one('res.partner', string="Shipping Line")
    bill_attach = fields.Binary(string=" ")
    bill_no = fields.Char(string="BL / AWB Number")
    rot_no = fields.Char(string="Rotation Number/Sequence Number")
    do_attach = fields.Binary(string=" ")
    do_no = fields.Date(string="DO Date")
    do_num = fields.Char(string="DO Number")
    acc_link = fields.Many2one('account.move', string="Invoice", readonly=True)
    bayan_attach = fields.Binary(string=" ")
    final_bayan = fields.Char(string="Final Bayan")
    final_attach = fields.Binary(string="Final Bayan")
    bayan_no = fields.Char(string="Bayan No.")
    bayan_date = fields.Date(string="Bayan Date")
    fin_bayan_date = fields.Date(string="Final Bayan Date")
    status = fields.Many2one('import.status', string="Status")
    import_id = fields.One2many('import.tree', 'crt_tree')
    import_serv = fields.One2many('import.service.tree', 'import_tree')
    import_other_charges = fields.One2many('import.other_charges', 'import_tree')
    import_gov_charges = fields.One2many('gov.charges', 'import_tree')
    imp_contt = fields.One2many('import.contain.tree', 'imp_tree_cont')
    remarks = fields.Text(string="Remarks")
    eta = fields.Date(string="ETA")
    etd = fields.Date(string="ETD")
    saddad = fields.Date(string="Saddad")
    inspect_Date = fields.Date(string="Inspection Date", required=False, )
    duty_Date = fields.Date(string="Duty Paid Date", required=False, )
    gate_Date = fields.Date(string="Gate Pass Date", required=False, )
    des_Port = fields.Many2one(comodel_name="res.country", string="Discharging Port", required=False, )
    lan_Port = fields.Many2one(comodel_name="res.country", string="Landing Port", required=False, )
    tasdeer = fields.Boolean(string="Tasdeer", )
    BRZ_In = fields.Date(string="BRZ In Date", required=False, )
    BRZ_Out = fields.Date(string="BRZ Out Date", required=False, )
    SDO_Date = fields.Date(string="SDO Collection Date", required=False, )
    ship_Type = fields.Selection(string="Shipment Type", selection=[('lcl', 'LCL'), ('fcl', 'FCL'), ], required=False, )
    sale_link = fields.Many2one(comodel_name="sale.order", string="sale link", required=False, )
    bill_link = fields.Many2one(comodel_name="account.move", string="Vendor bill", required=False, )
    tick = fields.Boolean()
    tos = fields.Many2many(comodel_name="sale.order", string="Transportation Orders", compute='_compute_sale_order')
    warn_invoice = fields.Integer(string="Warn Invoice", )
    filed_officer = fields.Many2one('filed.officer', string="Assign to", required=False)
    house_bl = fields.Char(string="House B/L")
    terminal = fields.Many2one('port.terminal', string="Terminal")
    port = fields.Many2one(comodel_name="res.port", string="Port", required=False, )
    no_invoice = fields.Boolean(string="No Invoice", )
    to_mails = fields.Char(string="mail To", required=False, )
    container_num = fields.Char(string="Container Num", required=False, store=True, compute="_compute_container_num")
    shipper_name = fields.Char(string="Shipper Name")
    vsl_exp_arvl_date = fields.Date(string="Vessel Expected Arrival Date")
    vsl_disch_date = fields.Date(string="Vessel Discharge Date")

    demurrage = fields.Date(string="Demurrage Date", store=True, default=datetime.today())
    free_time_days = fields.Integer(string="Free Time Days", default='10')
    detention_date = fields.Date(string="Detention Date", store=True,
                                 compute='_compute_import_demurrage_detention_dates')

    @api.depends('vessel_date', 'free_time_days')
    def _compute_import_demurrage_detention_dates(self):
        for rec in self:
            if rec.vessel_date and rec.free_time_days:
                rec.detention_date = (datetime.strptime(str(rec.vessel_date), '%Y-%m-%d') + timedelta(days=rec.free_time_days)).date()

    @api.onchange('vessel_date')
    def _onchange_demurrage(self):
        for file in self:
            if file.vessel_date:
                file.demurrage = (datetime.strptime(str(file.vessel_date), '%Y-%m-%d') + timedelta(days=5)).date()

    count_crt = fields.Integer(string="Count Of Container", required=False, compute='_compute_container_num',
                               store=True)


    @api.depends('import_id')
    def _compute_container_num(self):
        """
        @api.depends() should contain all fields that will be used in the calculations.
        """
        for rec in self:
            crt_list = []
            if rec.import_id:
                for x in rec.import_id:
                    if x.crt_no:
                        crt_list.append(x.crt_no.encode('ascii', 'ignore'))
                rec.container_num = crt_list
                rec.count_crt = len(crt_list)

    stages = fields.Selection([
        ('pre', 'Pre Bayan'),
        ('initial', 'Initial Bayan'),
        ('final', 'Final Bayan'),
        ('done', 'Done'),
    ], default="pre")

    _sql_constraints = [
        ('customer_ref', 'unique(customer_ref)', 'This customer reference already esixts!')
    ]

    @api.model
    def create(self, vals):
        """Creating Sequence for SR No and Job No"""
        vals['s_no'] = self.env['ir.sequence'].next_by_code('import.logics')
        vals['job_no'] = self.env['ir.sequence'].next_by_code('import.job.num')
        new_record = super(ImportLogic, self).create(vals)

        return new_record

    @api.onchange('customer', 'by_customer', 'bill_types', 'port')
    def get_import_tree_value(self):
        if self.customer:
            # self.bill_types = self.customer.bill_type
            if self.bill_types == "B/L Number":
                self.bill_bol = True
                self.contt_bol = False
                for x in self.customer.bl_id:
                    if self.by_customer == x.by_customer:
                        delete = []
                        delete = delete.append(2)
                        self.import_serv = delete

                        inv = []
                        for invo in x:
                            inv.append({
                                'charge_serv': invo.charges_serv,
                                'type_serv': invo.charges_type.id,
                                'import_tree': self.id,
                            })
                        self.import_serv = inv

            if self.bill_types == "Container Wise":
                self.contt_bol = True
                self.bill_bol = False
                contt = []
                for x in self.customer.cont_id:
                    if self.by_customer == x.by_customer and x.service_type == 'import' and self.port == x.port:
                        delete = []
                        delete = delete.append(2)
                        self.imp_contt = delete
                        for line in x:
                            contt.append({
                                'sevr_charge_imp': line.charges_serv,
                                'sevr_type_imp': line.charges_type.id,
                                'type_contt_imp': line.cont_type,
                                'imp_tree_cont': self.id,
                            })
                self.imp_contt = contt


    def initialbay(self):
        self.stages = "initial"


    def finalbay(self):
        self.stages = "final"


    def over(self):
        self.stages = "done"

    @api.depends('stages')
    def _compute_sale_order(self):
        for rec in self:
            if rec.stages == 'done':
                rec.tos = self.env['sale.order'].search([('partner_id', '=', rec.customer.id),
                                                          ('sales_imp_id', '=', rec.id),
                                                          ('bill_no', '=', rec.bill_no)]).ids
            else:
                rec.tos = False


    def create_sale(self):
        """Create Transport Order"""

        if not self.tos and not self.acc_link:
            # / Get Product having name is Container/
            value = self.env['product.template'].search([('name', '=', 'Transportation Charge')])[0].id
            # / Create Transport Order/
            for data in self.import_id:
                if data.crt_no:
                    records = self.env['sale.order'].create({
                        'partner_id': self.customer.id,
                        'by_customer': self.by_customer.id, 'date_order': date.today(), 'bill_type': self.bill_types,
                        'bill_no': self.bill_no, 'import_chk': True, 'suppl_name': data.transporter.id,
                        'suppl_freight': data.trans_charge,
                        'sales_imp_id': self.id, 'our_job': '', 'sr_no': '', 'customer_ref': self.customer_ref,
                        'custom_dec': '', 'bayan_no': self.bayan_no, 'customer_site': self.site.id,
                        'final_date': self.fin_bayan_date, 'no_invoice': True, 'demurrage': self.demurrage,
                    })

                    records.order_line.create({
                        'product_id': value, 'name': 'Container', 'weight': data.weight, 'product_uom_qty': 1.0,
                        'price_unit': data.custm_charge, 'crt_no': data.crt_no, 'product_uom': 1, 'form': data.form.id,
                        'to': data.to.id, 'fleet_type': data.fleet_type.id, 'order_id': records.id,
                    })
            email_rec = self.env['multi.mails'].search([])
            template = self.env.ref('custom_logistic.cct_email_template')
            for email in email_rec.sale_support:
                self.to_mails = email.name
                self.env['mail.template'].browse(template.id).send_mail(self.id)
        else:
            raise UserError(_('Transportation or Invoice is Already Created'))


    def get_order_name(self, sale_ids):
        return str([sale.name.encode('ascii', 'ignore') for sale in sale_ids]).replace('[', '').replace(']',
                                                                                                        '').replace("'",
                                                                                                                    '')


    def create_custom_charges(self):
        if self.warn_invoice == 0:
            self.warn_invoice += 1
            view = self.env.ref('sh_message.sh_message_wizard').id
            context = dict(self._context or self)
            context['message'] = 'Do you Really Want To Create Invoice, If yes then click Create Invoice Button Again'
            return {'name': 'Warning', 'type': 'ir.actions.act_window', 'view_type': 'form', 'view_mode': 'form',
                    'res_model': 'sh.message.wizard', 'views': [(view, 'form')], 'view_id': view, 'target': 'new',
                    'context': context, }

        account = self.env['account_journal.configuration'].search([])
        invoice = self.env['account.move']
        invoice_lines = self.env['account.move.line']
        sale = self.env['sale.order'].search([('sales_imp_id', '=', self.id)])
        check = 0
        for x in sale:
            if x.state == 'done':
                check += 1

        if check == len(sale):

            # / B/L Wise invoice/
            if not self.acc_link and not self.fri_id:
                if self.bill_types == "B/L Number":
                    create_invoice = invoice.create({
                        'journal_id': account.i_invoice_journal.id,
                        'partner_id': self.customer.id,
                        'by_customer': self.by_customer.id,
                        'date_invoice': date.today(),
                        'billng_type': self.bill_types,
                        'bill_num': self.bill_no,
                        'our_job': self.job_no,
                        'sr_no': self.s_no,
                        'customer_ref': self.customer_ref,
                        'custom_dec': '',
                        'bayan_no': self.bayan_no,
                        'customer_site': self.site.id,
                        'final_date': self.fin_bayan_date,
                        'type': 'out_invoice',
                        'invoice_from': 'imp',
                        'import_link': self.id,
                        'property_account_receivable_id': self.customer.property_account_receivable_id.id,

                    })

                    for x in self.import_serv:
                        create_invoice_lines = invoice_lines.create({
                            'quantity': 1,
                            'price_unit': x.charge_serv,
                            'account_id': account.i_invoice_account.id,
                            'name': x.type_serv.name,
                            'move_id': create_invoice.id,

                        })
                    for x in self.import_id:
                        create_invoice_lines = invoice_lines.create({
                            'quantity': 1,
                            'price_unit': x.custm_charge,
                            'account_id': account.i_invoice_account.id,
                            'name': x.des,
                            'crt_no': x.crt_no,
                            'move_id': create_invoice.id,
                            # 'invoice_line_tax_ids': [1],
                        })

                # / Container Wise invoice/
                if self.bill_types == "Container Wise":
                    entry = []
                    for x in self.import_id:
                        if x.types not in entry:
                            entry.append(x.types)

                    create_invoice = invoice.create({
                        'journal_id': account.i_invoice_journal.id,
                        'partner_id': self.customer.id,
                        'by_customer': self.by_customer.id,
                        'date_invoice': date.today(),
                        'billng_type': self.bill_types,
                        'bill_num': self.bill_no,
                        'our_job': self.job_no,
                        'sr_no': self.s_no,
                        'customer_ref': self.customer_ref,
                        'custom_dec': '',
                        'bayan_no': self.bayan_no,
                        'customer_site': self.site.id,
                        'final_date': self.fin_bayan_date,
                        'type': 'out_invoice',
                        'invoice_from': 'imp',
                        'import_link': self.id,
                        'property_account_receivable_id': self.customer.property_account_receivable_id.id,
                    })
                    if create_invoice:
                        self.acc_link = create_invoice.id
                    for line in entry:
                        value = 0
                        for x in self.import_id:
                            if x.types == line:
                                value += 1
                        get_unit = 0
                        get_type = ' '
                        for y in self.imp_contt:
                            if y.type_contt_imp == line:
                                get_unit = y.sevr_charge_imp
                                get_type = y.sevr_type_imp.name

                        create_invoice_lines = invoice_lines.create({
                            'quantity': value,
                            'price_unit': get_unit,
                            'account_id': account.i_invoice_account.id,
                            'name': 'Custom Clearance Charges  -   اجور تخليص  الجمركي',
                            'service_type': get_type,
                            'move_id': create_invoice.id,
                            # 'invoice_line_tax_ids': [1],
                        })

                for x in self.import_other_charges:
                    create_invoice_lines = invoice_lines.create({
                        'quantity': 1,
                        'price_unit': x.charges,
                        'account_id': account.i_invoice_account.id,
                        'name': x.name.name,
                        'move_id': create_invoice.id,
                    })
                for x in self.import_gov_charges:
                    create_invoice_lines = invoice_lines.create({
                        'quantity': 1,
                        'price_unit': x.charges,
                        'account_id': account.g_invoice_account.id,
                        'name': x.name.name,
                        'move_id': create_invoice.id,
                    })
                self.acc_link = create_invoice.id

                if self.tos:
                    for x in self.tos:
                        x.invoice_status = 'invoiced'
                        create_invoice.invoice_line_ids.create({
                            'quantity': 1,
                            'price_unit': x.amount_total,
                            'account_id': x.trans_account,
                            'name': str(x.name) + " Transportation Charges" + ' اجور نقل '.decode('utf-8'),
                            'crt_no': x.order_line.crt_no,
                            'move_id': create_invoice.id
                        })

                        if x.pullout_type == 'Customer':
                            create_invoice.invoice_line_ids.create({
                                'quantity': 1,
                                'price_unit': x.partner_id.pullout_charges,
                                'account_id': account.t_pullout_account.id,
                                'name': str(x.name) + " PullOut Charges",
                                'move_id': create_invoice.id
                            })

                        if x.pull_out and x.pullout_status == 'Completed':
                            if datetime.now().date() >= (
                                    datetime.strptime(str(x.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                                days=x.partner_id.free_day)).date():
                                day = datetime.now().date() - (
                                        datetime.strptime(str(x.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                                    days=x.partner_id.free_day)).date()

                                if day.days > 0:
                                    create_invoice.invoice_line_ids.create({
                                        'quantity': day.days,
                                        'price_unit': x.partner_id.storage_charges,
                                        'account_id': account.t_storage_account.id,
                                        'name': "Storage Charges for " + str(day.days) + " Days",
                                        'move_id': create_invoice.id
                                    })
                partner = self.env['res.partner'].search([('name', '=', 'Government Charges Vendor')])

                # vendor bill
                if self.import_gov_charges:
                    create_invoice = self.env['account.move'].create({
                        'journal_id': account.g_invoice_journal.id,
                        'partner_id': partner.id,
                        'date_invoice': date.today(),
                        'billng_type': self.bill_types,
                        'bill_num': self.bill_no,
                        'type': 'in_invoice',
                        'import_link': self.id,
                        'invoice_from': 'imp',
                        'account_id': partner.property_account_payable_id.id
                    })
                    for x in self.import_gov_charges:
                        create_invoice_lines = create_invoice.invoice_line_ids.create({
                            'quantity': 1,
                            'price_unit': x.charges,
                            'attachment': x.attachment,
                            'account_id': account.g_invoice_account.id,
                            'name': x.name.name,
                            'move_id': create_invoice.id,
                        })
                email_rec = self.env['multi.mails'].search([])
                template = self.env.ref('custom_logistic.tii_email_template')
                for email in email_rec.finance:
                    self.to_mails = email.name
                    self.env['mail.template'].browse(template.id).send_mail(self.id)

            else:
                raise UserError(_('Invoice Is Already Created or Maybe This Import Is Linked With Project.'))
        else:
            raise UserError(_('Transportation in Process Wait until Transport order not complete'))


class import_charges(models.Model):
    _name = 'import.other_charges'
    _rec_name = 'name'

    name = fields.Many2one('charges.des', string="Other Charges Description", required=False, )
    charges = fields.Float(string="Amount", required=True, )
    import_tree = fields.Many2one('import.logic')
    export_tree = fields.Many2one('export.logic')


class OtherChargesDes(models.Model):
    _name = 'charges.des'
    _rec_name = 'name'

    name = fields.Char(string="Other Charges Description", required=False, )


class Gov_Charges(models.Model):
    _name = 'gov.charges'
    _rec_name = 'name'

    name = fields.Many2one('charges.des', string="Gov. Charges Description", required=False, )
    attachment = fields.Binary(string="Attachment")
    charges = fields.Float(string="Amount", required=True, )
    import_tree = fields.Many2one('import.logic')
    export_tree = fields.Many2one('export.logic')
    freight_tree = fields.Many2one('freight.forward')


class ImportTree(models.Model):
    _name = 'import.tree'

    crt_no = fields.Char(string="Container No.", size=11)
    weight = fields.Float()
    des = fields.Char(string="Description", required=False, )
    form = fields.Many2one('from.qoute', string="From")
    to = fields.Many2one('to.quote', string="To")
    fleet_type = fields.Many2one('fleet', string="Fleet Type")
    # sev_typ_charg	= fields.Many2one('imp.type.tree',string="Service Type & Charges")
    transporter = fields.Many2one('res.partner', string="Transporter")
    trans_charge = fields.Char(string="Transporter Charges")
    custm_charge = fields.Char(string="Customer Charges")
    crt_tree = fields.Many2one('import.logic')
    types = fields.Selection([
        ('20 ft', '20 ft'),
        ('40 ft', '40 ft')], string="Size")
    p_date = fields.Date(string="Pay Date", required=False, )
    amount = fields.Float(string="Deposit Amount", required=False, )
    status = fields.Selection(string="Status", selection=[('Waiting EIR', 'Waiting EIR'),
                                                          ('Under Refunding', 'Under Refunding'),
                                                          ('Refunded', 'Refunded'), ], required=False, )
    e_date = fields.Date(string="EIR Date", required=False, )

    @api.onchange('crt_no')
    def container_no_check_onchange(self):
        if self.crt_no:
            if re.match('^[A-Z]{4}[0-9]{7,}$', self.crt_no.upper()):
                self.crt_no = self.crt_no.upper()
            else:
                raise ValidationError("You have Entered a Wrong Container Number or Format: %s \nFormat is AAAA0000000"
                                      "\nFirst Four Character Must be Alphabet and Last Seven Character Must be Numeric"
                                      % self.crt_no.upper())

    @api.constrains('crt_no')
    def container_no_check_constrains(self):
        if self.crt_no:
            if re.match('^[A-Z]{4}[0-9]{7,}$', self.crt_no.upper()):
                return True
            else:
                raise ValidationError("You have Entered a Wrong Container Number or Format: %s \nFormat is AAAA0000000,"
                                      "\nFirst Four Character Must be Alphabet and Last Seven Character Must be Numeric"
                                      % self.crt_no.upper())

    @api.onchange('transporter', 'form', 'to', 'fleet_type')
    def add_charges(self):
        """ Calculating Charges As per Transporter, To, From, and fleet_type for selected customer"""
        if self.transporter.id and self.form.id and self.to.id and self.fleet_type:
            trans = self.env['res.partner'].search([('id', '=', self.transporter.id)])
            for x in trans.route_id:
                if self.form.id == x.form.id and self.to.id == x.to.id and self.fleet_type == x.fleet_type and x.service_type == "import":
                    self.trans_charge = x.trans_charges
            rec = self.env['res.partner'].search([('id', '=', self.crt_tree.customer.id)])
            for x in rec.route_id:
                if self.form.id == x.form.id and self.to.id == x.to.id and self.fleet_type == x.fleet_type and x.service_type == "import":
                    self.custm_charge = x.trans_charges


class ServiceImportTree(models.Model):
    _name = 'import.service.tree'

    type_serv = fields.Many2one('serv.types', string="Service Type")
    charge_serv = fields.Integer(string="Service Charges")
    import_tree = fields.Many2one('import.logic')


class ImportContTree(models.Model):
    _name = 'import.contain.tree'

    sevr_type_imp = fields.Many2one('serv.types', string="Service Type")
    sevr_charge_imp = fields.Integer(string="Service Charges")
    type_contt_imp = fields.Char(string="Container Size")
    imp_tree_cont = fields.Many2one('import.logic')


class SiteLogic(models.Model):
    _name = 'import.site'

    site_name = fields.Char(string="Name")
    name = fields.Char(string="Site Name")
    city = fields.Char(string="City")
    address = fields.Char(string="Address")
    cnt_num = fields.Char(string="Contact No")


# @api.model
# def _getName(self):
# 	for rec in self.env['import.site'].search([]):
# 		rec.name = rec.site_name
# 		print rec.name


class StatusLogic(models.Model):
    _name = 'import.status'
    comment = fields.Char(string="status")
    name = fields.Char(string="Status Name")



    def unlink(self):
        for rec in self:
            if self.env['import.logic'].search_count([('status', '=', rec.id)]) or self.env['export.logic'].search_count([('status', '=', rec.id)]):
                raise ValidationError('Status is in use you can not Delete')
            return super(StatusLogic, self).unlink()


# @api.model
# def _getName(self):
# 	for rec in self.env['import.status'].search([]):
# 		rec.name = rec.comment
# 		print rec.name


class AccInvLineExt(models.Model):
    _inherit = 'account.move.line'

    attachment = fields.Binary(string="Attachment", attachment=True)
    afterTaxAmt = fields.Float(string='Tax Amount', required=False, digits=(6, 3))

    # @api.onchange('price_subtotal', 'quantity', 'price_unit', 'invoice_line_tax_ids')
    # def onchange_price_subtotal(self):
    #     if self.invoice_line_tax_ids:
    #         amt = 0
    #         for x in self.invoice_line_tax_ids:
    #             tax = x.amount / 100
    #             amt = amt + (tax * self.price_subtotal)
    #         self.afterTaxAmt = amt


class SaleLineExt(models.Model):
    _inherit = 'sale.order.line'

    afterTaxAmt = fields.Float(string='Tax Amount', required=False, digits=(6, 3))

    @api.onchange('price_subtotal', 'product_uom_qty', 'price_unit', 'tax_id')
    def onchange_price_subtotal(self):
        if self.tax_id:
            amt = 0
            for x in self.tax_id:
                tax = x.amount / 100
                amt = amt + (tax * self.price_subtotal)
            self.afterTaxAmt = amt


class ResPartnerExt(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(string="VAT", required=False, )
    arabic_name = fields.Char(string="Arabic Name", required=False, )


class ResCompanyExt(models.Model):
    _inherit = 'res.company'

    vat = fields.Char(string="VAT", required=False, )


class AccountConfiguration(models.Model):
    _name = 'account_journal.configuration'
    _rec_name = 'name'

    name = fields.Char(default="Accounts and Journals Configuration")

    e_vendor_account = fields.Many2one(comodel_name="account.account", string="Broker Bills Account", required=False, )
    e_vendor_journal = fields.Many2one(comodel_name="account.journal", string="Broker Bills Journal", required=False, )

    e_invoice_account = fields.Many2one(comodel_name="account.account", string="Customer Invoice Account",
                                        required=False, )
    e_custom_invoice_account = fields.Many2one(comodel_name="account.account",
                                               string="Export Custom Clearance Invoice Account", required=False, )
    e_custom_exm_invoice_account = fields.Many2one(comodel_name="account.account",
                                                   string="Export Custom Examination Invoice Account")
    e_invoice_journal = fields.Many2one(comodel_name="account.journal", string="Customer Invoice Journal")
    i_custom_invoice_account = fields.Many2one(comodel_name="account.account",
                                               string="Import Custom Clearance Invoice Account")
    i_invoice_account = fields.Many2one(comodel_name="account.account", string="Customer Invoice Account")
    i_invoice_journal = fields.Many2one(comodel_name="account.journal", string="Customer Invoice Journal")
    t_vendor_account = fields.Many2one(comodel_name="account.account", string="Driver Trip Account")
    t_vendor_journal = fields.Many2one(comodel_name="account.journal", string="Driver Trip Journal")
    t_vendor_account_ex = fields.Many2one(comodel_name="account.account", string="3PL Supplier Account")
    t_customer_account_ex = fields.Many2one(comodel_name="account.account", string="3PL Revenue Account")
    t_pullout_account = fields.Many2one(comodel_name="account.account", string="PullOut Revenue Account")
    t_storage_account = fields.Many2one(comodel_name="account.account", string="Storage Revenue Account")
    t_vendor_journal_ex = fields.Many2one(comodel_name="account.journal", string="3PL Supplier Journal")
    same_custom_invoice_account = fields.Many2one(comodel_name="account.account", string="Transport Invoice Account")
    freight_invoice_account = fields.Many2one(comodel_name="account.account", string="Freight Invoice Account")
    storage_invoice_account = fields.Many2one(comodel_name="account.account", string="Storage Invoice Account")
    transport_invoice_account = fields.Many2one(comodel_name="account.account",
                                                string="Transport Order Invoice Account")
    p_invoice_journal = fields.Many2one(comodel_name="account.journal", string="Customer Invoice Journal")
    g_invoice_account = fields.Many2one(comodel_name="account.account", string="Gov. Charges Account")
    g_invoice_journal = fields.Many2one(comodel_name="account.journal", string="Gov. Charges Journal")


class Change_Date_Status(models.TransientModel):
    _name = "change.date_status"

    date = fields.Date(string="Date", required=True, )
    status = fields.Many2one(comodel_name="import.status", string="Status", required=True, )
    m_name = fields.Char()


    def pre(self):
        active_class = self.env[self.m_name].browse(self._context.get('active_id'))
        if active_class:
            if self.m_name == 'import.logic':
                for x in active_class:
                    x.bayan_date = self.date;
                    x.status = self.status.id
            if self.m_name == 'export.logic':
                for x in active_class:
                    x.pre_bayan = self.date;
                    x.status = self.status.id


    def final(self):
        active_class = self.env[self.m_name].browse(self._context.get('active_id'))
        if active_class:
            for x in active_class:
                x.fin_bayan_date = self.date;
                x.status = self.status.id


class FleetVehicleAccident(models.Model):
    _name = 'fleet.vehicle.accident'
    _rec_name = 'driver_id'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    driver_id = fields.Many2one('res.partner', 'Driver', required=True)
    accident_date = fields.Datetime('Date', required=True)
    location = fields.Char('Location')
    remarks = fields.Char('Remarks')
    attachments = fields.One2many('vehicle.accident.attachment', 'vehicle_accident_id', 'Accident Ref')


class VehicleAccidentAttachment(models.Model):
    _name = 'vehicle.accident.attachment'

    vehicle_accident_id = fields.Many2one('fleet.vehicle.accident', 'Accident Ref')
    attachment = fields.Binary('Attachment')
    attachment_name = fields.Char('Attachment Name')
    sale_attachments = fields.Many2one(comodel_name="sale.order", string="Sale Attachments", required=False, )
    breakdown_sale_attachments = fields.Many2one(comodel_name="sale.order", string="Sale Attachments", required=False, )


class FleetVehicleExt(models.Model):
    _inherit = 'fleet.vehicle'

    vechicle_accident_detail = fields.One2many('fleet.vehicle.accident', 'vehicle_id', 'Vehicle')
    sales_order_ids = fields.One2many('sale.order', 'vehicle_id', string='TransPort sales')
    sales_order_pullout = fields.One2many('sale.order', 'p_vehicle_id', string='PullOut sales')
    sales_order_breakdown = fields.One2many('sale.order', 'b_vehicle_id', string='BreakDown sales')
    city = fields.Many2one('from.qoute', string="Belong to", ondelete='restrict')
    is_reserved = fields.Boolean(string="Reserved", readonly=True, default=False)
    analytic_account = fields.Many2one('account.analytic.account', string="Analytic Account",
                                       required=False, ondelete='restrict')
    breakdown = fields.Boolean(string="BreakDown", )


class FleetVehicleLogServicesTire(models.Model):
    _name = 'fleet.vehicle.log.services.tire'

    t_date = fields.Date(string="Tire Change Date", required=False, )
    truck_num = fields.Char(string="Truck Number", required=False, )
    trailer_num = fields.Char(string="Trailer Number", required=False, )
    tire_size = fields.Char(string="Tire Size", required=False, )
    t_brand = fields.Char(string="Tire Brand", required=False, )
    t_location = fields.Char(string="Location", required=False, )
    t_serial = fields.Char(string="Tire Serial Number", required=False, )
    t_price = fields.Integer(string="Price", required=False, )
    t_vat = fields.Integer(string="Vat", required=False, )
    tire_details = fields.Many2one('fleet.vehicle.log.services', 'Vehicle')


class FleetVehicleLogServicesExt(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    vehicle_tire_detail = fields.One2many('fleet.vehicle.log.services.tire', 'tire_details', 'Vehicle Tire Details')


class FleetVehicleCostExt(models.Model):
    _inherit = 'fleet.vehicle.cost'
    vat = fields.Integer(string="Vat", required=False, )


class AccountMoveLineExt(models.Model):
    _inherit = 'account.move.line'

    branch = fields.Many2one('account.analytic.account', string="Branch")


class AccountAnalyticalExt(models.Model):
    _inherit = 'account.analytic.account'

    is_parent = fields.Boolean(string="Is Parent?")


# class AccountAssetExt(models.Model):
#     _inherit = 'account.asset.asset'
#
#     acc_dep = fields.Float(string="Accumulated Depreciation", compute="_compute_acc_dep_amount")
#
#     @api.depends('depreciation_line_ids', 'depreciation_line_ids.move_check', 'depreciation_line_ids.move_id')
#     def _compute_acc_dep_amount(self):
#         for rec in self:
#             for line in rec.depreciation_line_ids:
#                 if line.move_check and line.move_id.name != '/':
#                     rec.acc_dep += line.amount

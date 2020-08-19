# -*- coding: utf-8 -*-
import re
from datetime import datetime, date
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountMoveLineInher(models.Model):
    _inherit = 'res.partner'

    route_id = fields.One2many('route.transport', 'route_trans')
    bl_id = fields.One2many('bl.tree', 'bl_tree')
    cont_id = fields.One2many('container.tree', 'bl_tree')
    charge_id = fields.One2many('charg.vender', 'charge_tree')
    brooker = fields.Boolean(string="Broker")
    checks = fields.Boolean(string="check")
    types = fields.Selection(
        [('trnas', 'Transporter'), ('freight_fwd', 'Freight Forwarder'), ('ship_line', 'Shipping Line'),
         ('storage', 'Storage')], string="Type")
    by_customer = fields.One2many(comodel_name="by.customer", inverse_name="main_class",
                                  string="By Customer", required=False, )
    is_driver = fields.Boolean('Is Driver')
    sales_order_ids = fields.One2many('sale.order', 'driver_id', string='Driver Sales')
    vechile_accident_ids = fields.One2many('fleet.vehicle.accident', 'driver_id', 'Accident Ref')
    is_reserved = fields.Boolean(string="Reserved", readonly=True, default=False)
    free_day = fields.Integer(string="Charges Free Days", required=False, )
    storage_charges = fields.Integer(string="Storage Charges", required=False, )
    storage_mail = fields.Char(string="Email", required=False, )
    pullout_charges = fields.Integer(string="Pullout Charges", required=False, )
    BAN = fields.Char(string="Broker Authorization Number", required=False, )
    BAN_expiry_date = fields.Date(string=" Expiry Date", required=False, )
    invoice_to = fields.Char('Invoice TO', required=True, default="Mr.")
    fleet_ids = fields.Many2many('fleet.vehicle', 'fleet_vehicle_transport_relation', string='Associated Vehicle')
    credit_limit = fields.Float(string="Max Credit Limit",  required=False, )

    def send_ban_mail(self):
        for rec in self:
            mails = self.env['res.partner'].search([('BAN_expiry_date', '!=', False)])
            for x in mails:
                if datetime.now() + timedelta(days=15) >= datetime.strptime(str(x.BAN_expiry_date), '%Y-%m-%d'):
                    template = x.env.ref('custom_logistic.BAN_email_template')
                    self.env['mail.template'].browse(template.id).send_mail(x.id)

    @api.onchange('types')
    def get_trans(self):
        if self.types == "freight_fwd":
            self.checks = True
        else:
            self.checks = False


class ByCustomer(models.Model):
    _name = 'by.customer'
    _rec_name = 'name'
    _description = 'By Customers of Customer'

    name = fields.Char()
    customer = fields.Many2one(comodel_name="res.partner", string="Customer", required=False, )
    main_class = fields.Many2one(comodel_name="res.partner", string="By Customer", required=False, )

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.customer = self.main_class.id


class BlnumberTree(models.Model):
    _name = 'bl.tree'

    charges_serv = fields.Float(string="Service Charges")
    charges_type = fields.Many2one('serv.types', string="Service Type")
    by_customer = fields.Many2one('by.customer', string="By Customer")

    bl_tree = fields.Many2one('res.partner')


class ContainerTree(models.Model):
    _name = 'container.tree'

    charges_serv = fields.Float(string="Service Charges")
    charges_type = fields.Many2one('serv.types', string="Service Type")
    by_customer = fields.Many2one('by.customer', string="By Customer")
    service_type = fields.Selection([('import', 'Import'), ('export', 'Export')], string="Service Name")
    cont_type = fields.Selection([('20 ft', '20 ft'), ('40 ft', '40 ft')], string="Container Size")
    bl_tree = fields.Many2one('res.partner')
    port = fields.Many2one(comodel_name="res.port", string="Port", required=False, )


class Ports(models.Model):
    _name = 'res.port'
    _rec_name = 'name'
    name = fields.Char('Port Name', required=True)


class transport_info(models.Model):
    _name = 'route.transport'
    # _rec_name   = 'company_name'

    form = fields.Many2one('from.qoute', string="From")
    to = fields.Many2one('to.quote', string="To")
    fleet_type = fields.Many2one('fleet', string="Fleet Type")
    service_type = fields.Selection([('import', 'Import'), ('export', 'Export')], string="Service Name")
    trans_charges = fields.Float(string="Charges")
    by_customer = fields.Many2one('by.customer', string="By Customer")

    route_trans = fields.Many2one('res.partner')


class ChargesVender(models.Model):
    _name = 'charg.vender'

    charges_vend = fields.Char(string="Charges")
    contain_type = fields.Selection([('20 ft', '20 ft'), ('40 ft', '40 ft')], string="Container Type")

    charge_tree = fields.Many2one('res.partner')


class From(models.Model):
    _name = 'from.qoute'

    name = fields.Char('name')


class To(models.Model):
    _name = 'to.quote'

    name = fields.Char('name')


class Fleet(models.Model):
    _name = 'fleet'

    name = fields.Char('Fleet Type')


class AccountExtend(models.Model):
    _inherit = 'account.move'

    # billng_type = fields.Char(string="Billing Type")
    billng_type = fields.Selection([('B/L Number', 'B/L Number'), ('Container Wise', 'Container Wise')],
                                   string="Billing Type")
    by_customer = fields.Many2one('by.customer', string="By Customer")
    customer_site = fields.Many2one('import.site', string="Site")
    bill_num = fields.Char(string="B/L Number")
    our_job = fields.Char(string="Our Job No", required=False, )
    sr_no = fields.Char(string="Sr No", required=False, )
    customer_ref = fields.Char(string="Customer Ref", required=False, )
    custom_dec = fields.Char(string="Custom Dec", required=False, )
    bayan_no = fields.Char(string="Bayan No", required=False, )
    final_date = fields.Date(string="Final Date", required=False, )
    import_link = fields.Many2one(comodel_name="import.logic", string="Import Link", required=False, )
    export_link = fields.Many2one(comodel_name="export.logic", string="Export Link", required=False, )
    frieght_link = fields.Many2one(comodel_name="freight.forward", string="Freight Link", required=False, )
    invoice_from = fields.Selection([('imp', 'Import'), ('exp', 'Export'), ('trans', 'Transportation')
                                        , ('trans_pro', 'Transportation Project'), ('pro', 'Project')],
                                    string="Invoice/Bill From")
    container_num = fields.Char(string="Container Number", required=False, compute='_compute_container_num', store=True)
    count_crt = fields.Integer(string="Count Of Container", required=False, compute='_compute_container_num',
                                     store=True)
    customer_id = fields.Many2one('res.partner', string='Customer')
    check = fields.Boolean()
    sale_link = fields.Many2one(comodel_name="sale.order", string="Sale Link", required=False, )
    ship_link = fields.Many2one(comodel_name="shipment.order", string="Shipment Link", required=False, )

    @api.onchange('partner_id')
    def get_cust(self):
        if self.partner_id:
            if "Custom Duty" in self.partner_id.name:
                self.check = True
            else:
                self.check = False


    @api.depends('invoice_line_ids')
    def _compute_container_num(self):
        """
        @api.depends() should contain all fields that will be used in the calculations.
        """
        for rec in self:
            crt_list = []
            if rec.invoice_line_ids:
                for x in rec.invoice_line_ids:
                    if x.crt_no:
                        crt_list.append(x.crt_no.encode('ascii', 'ignore'))
                rec.container_num = crt_list
                rec.count_crt = len(crt_list)


    def reg_pay(self):
        for rec in self:
            return {'name': 'Receipt',
                    'domain': [],
                    'res_model': 'customer.payment.bcube',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form', 'view_type': 'form',
                    'context': {
                        'default_partner_id': rec.partner_id.id,
                        'default_receipts': True,
                        'default_invoice_link': rec.id,
                        'default_amount': rec.residual},
                    'target': 'new', }


class AccountTreeExtend(models.Model):
    _inherit = 'account.move.line'

    crt_no = fields.Char(string="Container No.")
    service_type = fields.Char(string="Service Name")


class Charges_service(models.Model):
    _name = 'serv.types'

    name = fields.Char(string="Service Type")


class FreightForwarding(models.Model):
    _name = 'freight.forward'
    _rec_name = 'sr_no'

    customer = fields.Many2one('res.partner', string="Customer", required=True)
    s_supplier = fields.Many2one('res.partner', string="Shipping Line")
    sr_no = fields.Char(string="SR No", readonly=True)
    book_date = fields.Date(string="Booking Date")
    eta_date = fields.Date(string="ETA Date")
    etd_date = fields.Date(string="ETD Date")
    cro = fields.Integer(string="CRO")
    cro_date = fields.Date(string="CRO Date")
    no_of_con = fields.Integer(string="No of Containers")
    form = fields.Many2one('res.country', string="Country of Origin")
    to = fields.Many2one('res.country', string="Destination")
    acct_link = fields.Many2one('account.move', string="Invoice", readonly=True)
    implink = fields.Many2one('import.logic', string="Import Link", readonly=True)
    explink = fields.Many2one('export.logic', string="Export Link", readonly=True)
    freight = fields.Boolean(string="Freight Forwarding")
    trans = fields.Boolean(string="Transportation")
    smart = fields.Boolean(string="Smart")
    store = fields.Boolean(string="Storage")
    custm = fields.Boolean(string="Custom Clearance")
    inv_chk = fields.Boolean(string="Invoice")
    frieght_id = fields.One2many('freight.tree', 'freight_tree')
    status = fields.Many2one('import.status', string="Status")
    trans_order = fields.Many2one('sale.order', string="Transport Order")
    recharge_count = fields.Integer(string="Recharge", compute='act_show_log_recharge_trip')
    customer_site = fields.Many2one('import.site', string="Site", required=True)
    demurrage = fields.Date(string="Demurrage", required=False, )
    des_Port = fields.Char(string="Discharging Port", required=False, )
    lan_Port = fields.Char(string="Landing Port", required=False, )
    freight_charges = fields.Float(string="Freight Charges", required=False, )
    customer_ref = fields.Char(string="Customer Ref", required=False, )
    types = fields.Selection([
        ('imp', 'Import'),
        ('exp', 'Export')
    ], string="Type")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft')
    btn_stage = fields.Selection([
        ('trans', 'Transportation'),
        ('custom', 'Custom Clearance'),
        ('invoice', 'Invoicing'),
        ('done', 'Done'),
    ], string=" Project Status", default='trans')

    pname = fields.Char(compute='act_show_log_recharge_trip')


    def act_show_log_recharge_trip(self):
        for rec in self:
            rec.recharge_count = self.env['sale.order'].search_count([('trans_link', '=', rec.id)])

    @api.model
    def create(self, vals):
        vals['sr_no'] = self.env['ir.sequence'].next_by_code('freight.forward')
        new_record = super(FreightForwarding, self).create(vals)

        return new_record

    def done(self):
        for rec in self:
            rec.state = 'done'

    def create_order(self):
        for rec in self:
            if not rec.smart:
                rec.btn_stage = 'custom'
                rec.smart = True
                value = 0
                get_id = self.env['product.template'].search([])
                for x in get_id:
                    if x.name == "Container":
                        value = x.id

                for data in rec.frieght_id:
                    if data.cont_no:
                        records = self.env['sale.order'].create({
                            'partner_id': rec.customer.id,
                            'suppl_name': rec.s_supplier.id,
                            'trans_link': rec.id,
                            'no_invoice': True,
                            'state': 'draft',
                            'customer_ref': rec.customer_ref
                        })

                        records.order_line.create({
                            'product_id': value,
                            'name': 'Transport Order from Project ' + str(rec.sr_no),
                            'product_uom_qty': 1.0,
                            'price_unit': 1,
                            'crt_no': data.cont_no,
                            'product_uom': 1,
                            'order_id': records.id,
                        })
                rec.trans = True
            else:
                raise UserError(_('Transportation is Already Created'))


    def create_invoice(self):
        account = self.env['account_journal.configuration'].search([])
        invoice = self.env['account.move'].search([])
        invoice_lines = self.env['account.move.line'].search([])
        sale = self.env['sale.order'].search([('trans_link', '=', self.id)])
        check = 0

        for x in sale:
            if x.state == 'done':
                check += 1

        create_invoice = invoice.create({
            'partner_id': self.customer.id,
            'date_invoice': self.book_date,
            'type': "out_invoice",
            'journal_id': account.p_invoice_journal.id,
            'freight_link': self.id,
            'customer_site': self.customer_site.id,
            'invoice_from': 'pro',
            'customer_ref': self.customer_ref
        })
        if check == len(sale):
            for x in sale:
                x.invoice_status = 'invoiced'
                invoice_lines.create({
                    'quantity': 1,
                    'price_unit': x.amount_total,
                    'account_id': x.trans_account,
                    'name': "Transportation Charges For " + str(x.name) + ' اجور نقل '.decode('utf-8'),
                    'invoice_id': create_invoice.id,
                    'crt_no': x.order_line.crt_no,
                    # 'invoice_line_tax_ids': [1],
                })
                if x.pullout_type == 'Customer':
                    invoice_lines.create({
                        'quantity': 1,
                        'price_unit': x.partner_id.pullout_charges,
                        'account_id': account.t_pullout_account.id,
                        'name': x.name,
                        'invoice_id': create_invoice.id
                    })
                if x.pull_out and x.pullout_status == 'Completed':
                    day = 0
                    if datetime.now().date() >= (
                            datetime.strptime(str(x.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                        days=x.partner_id.free_day)).date():
                        day = datetime.now().date() - (
                                datetime.strptime(str(x.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                            days=x.partner_id.free_day)).date()

                        if day.days > 0:
                            invoice_lines.create({
                                'quantity': day.days,
                                'price_unit': x.partner_id.storage_charges,
                                'account_id': account.t_storage_account.id,
                                'name': "Storage Charges for " + str(day.days) + " Days",
                                'invoice_id': create_invoice.id
                            })
            if self.freight and self.freight_charges > 0.0:
                invoice_lines.create({
                    'quantity': 1,
                    'price_unit': self.freight_charges,
                    'account_id': account.storage_invoice_account.id,
                    'name': "Freight Charges",
                    'invoice_id': create_invoice.id
                })

            self.acct_link = create_invoice.id
            if self.implink and self.implink.stages == 'done':
                if self.implink.bill_types == "B/L Number":
                    for x in self.implink.import_serv:
                        create_invoice_lines = invoice_lines.create({
                            'quantity': 1,
                            'price_unit': x.charge_serv,
                            'account_id': account.i_custom_invoice_account.id,
                            'name': x.type_serv.name,
                            'invoice_id': create_invoice.id,
                            # 'invoice_line_tax_ids': [1],
                        })
                    for x in self.implink.import_id:
                        create_invoice_lines = invoice_lines.create({
                            'quantity': 1,
                            'price_unit': x.custm_charge,
                            'account_id': account.i_custom_invoice_account.id,
                            'name': x.des,
                            'crt_no': x.crt_no,
                            'invoice_id': create_invoice.id,
                            # 'invoice_line_tax_ids': [1],
                        })

                # / Container Wise invoice/
                if self.implink.bill_types == "Container Wise":
                    entry = []
                    for x in self.implink.import_id:
                        if x.types not in entry:
                            entry.append(x.types)

                    for line in entry:
                        value = 0
                        for x in self.implink.import_id:
                            if x.types == line:
                                value += 1
                        get_unit = 0
                        get_type = ' '
                        for y in self.implink.imp_contt:
                            if y.type_contt_imp == line:
                                get_unit = y.sevr_charge_imp
                                get_type = y.sevr_type_imp.name

                        create_invoice_lines = invoice_lines.create({
                            'quantity': value,
                            'price_unit': get_unit,
                            'account_id': account.i_custom_invoice_account.id,
                            'name': line,
                            'service_type': get_type,
                            'invoice_id': create_invoice.id,
                            'invoice_line_tax_ids': [1],
                        })

                for x in self.implink.import_other_charges:
                    create_invoice_lines = invoice_lines.create({
                        'quantity': 1,
                        'price_unit': x.charges,
                        'account_id': account.i_custom_invoice_account.id,
                        'name': x.name,
                        'invoice_id': create_invoice.id,
                    })
                for x in self.implink.import_gov_charges:
                    create_invoice_lines = invoice_lines.create({
                        'quantity': 1,
                        'price_unit': x.charges,
                        'account_id': account.g_invoice_account.id,
                        'name': x.name,
                        'invoice_id': create_invoice.id,
                    })
                # vendor bill
                if self.implink.import_gov_charges:
                    partner = self.env['res.partner'].search([('name', '=', 'Government Charges Vendor')])
                    create_invoice = self.env['account.move'].create({
                        'journal_id': account.g_invoice_journal.id,
                        'partner_id': partner.id,
                        'date_invoice': date.today(),
                        'billng_type': self.implink.bill_types,
                        'bill_num': self.implink.bill_no,
                        'type': 'in_invoice',
                        'frieght_link': self.id,
                        'invoice_from': 'pro',
                        'customer_ref': self.customer_ref
                    })
                    for x in self.implink.import_gov_charges:
                        create_invoice_lines = create_invoice.invoice_line_ids.create({
                            'quantity': 1,
                            'price_unit': x.charges,
                            'account_id': account.g_invoice_account.id,
                            'name': x.name,
                            'invoice_id': create_invoice.id,
                        })

            elif self.explink and self.explink.state == 'done':
                if self.explink.bill_types == "B/L Number":
                    for x in self.explink.export_serv:
                        create_invoice_lines = invoice_lines.create({
                            'quantity': 1,
                            'price_unit': x.sevr_charge,
                            'account_id': account.e_custom_invoice_account.id,
                            'name': x.sevr_type.name,
                            'invoice_id': create_invoice.id,
                            'invoice_line_tax_ids': [1],
                        })

                    # / B/L Wise invoice/
                if self.explink.bill_types == "Container Wise":
                    data = []
                    for x in self.explink.export_id:
                        if x.types not in data:
                            data.append(x.types)

                    for line in data:
                        value = 0
                        for x in self.explink.export_id:
                            if x.types == line:
                                value = value + 1
                        get_unit = 0
                        get_type = ' '
                        for y in self.explink.cont_serv:
                            if y.type_contt == line:
                                get_unit = y.sevr_charge_cont
                                get_type = y.sevr_type_cont.name

                        create_invoice_lines = invoice_lines.create({
                            'quantity': value,
                            'price_unit': get_unit,
                            'account_id': account.e_custom_invoice_account.id,
                            'name': line,
                            'service_type': get_type,
                            'invoice_id': create_invoice.id,
                            'invoice_line_tax_ids': [1],
                        })

                for x in self.explink.export_other_charges:
                    create_invoice_lines = invoice_lines.create({
                        'quantity': 1,
                        'price_unit': x.charges,
                        'account_id': account.e_custom_invoice_account.id,
                        'name': x.name,
                        'invoice_id': create_invoice.id,
                    })

                for x in self.explink.export_gov_charges:
                    create_invoice_lines = invoice_lines.create({
                        'quantity': 1,
                        'price_unit': x.charges,
                        'account_id': account.g_invoice_account.id,
                        'name': x.name,
                        'invoice_id': create_invoice.id,
                    })

                if self.explink.export_gov_charges:
                    partner = self.env['res.partner'].search([('name', '=', 'Government Charges Vendor')])
                    create_invoice = self.env['account.move'].create({
                        'journal_id': account.g_invoice_journal.id,
                        'partner_id': partner.id,
                        'date_invoice': date.today(),
                        'type': 'in_invoice',
                        'frieght_link': self.id,
                        'invoice_from': 'pro',
                        'customer_ref': self.customer_ref
                    })
                    for x in self.explink.export_gov_charges:
                        create_invoice_lines = create_invoice.invoice_line_ids.create({
                            'quantity': 1,
                            'price_unit': x.charges,
                            'account_id': account.g_invoice_account.id,
                            'name': x.name,
                            'invoice_id': create_invoice.id,
                        })

            else:
                raise UserError(_('Custom Clearance is Under Process complete'))
        else:
            raise UserError(_('Transportation in Process Wait until Transport order not complete'))

        self.btn_stage = 'done'
        self.inv_chk = True

    def create_custm(self):

        if self.custm:
            sale = self.env['sale.order'].search([('trans_link', '=', self.id)])
            check = 0

            for x in sale:
                if x.state == 'done':
                    check += 1
            if check == len(sale):

                if self.types == 'imp':
                    records = self.env['import.logic'].create({
                        'customer': self.customer.id,
                        'fri_id': self.id,
                        'no_invoice': True,
                        'site': self.customer_site.id,
                        'customer_ref': self.customer_ref
                    })

                    self.implink = records.id

                    for x in self.frieght_id:
                        records.import_id.create({
                            'crt_no': x.cont_no,
                            'types': x.cont_type,
                            'crt_tree': records.id,
                        })

                if self.types == 'exp':
                    records = self.env['export.logic'].create({
                        'customer': self.customer.id,
                        'fri_id': self.id,
                        'no_invoice': True,
                        'site': self.customer_site.id,
                        'customer_ref': self.customer_ref
                    })

                    self.explink = records.id

                    for x in self.frieght_id:
                        records.export_id.create({
                            'crt_no': x.cont_no,
                            'types': x.cont_type,
                            'crt_tree': records.id,
                        })
                self.btn_stage = 'invoice'
            else:
                raise UserError(_('Transportation in Process Wait until Transport order not complete'))


class FreightTree(models.Model):
    _name = 'freight.tree'

    cont_no = fields.Char(string="Container No", size=11)
    cont_type = fields.Selection([('20 ft', '20 ft'), ('40 ft', '40 ft')], string="Container Size")
    freight_tree = fields.Many2one('freight.forward')

    @api.onchange('cont_no')
    def container_no_check_onchange(self):
        if self.cont_no:
            if re.match('^[A-Z]{4}[0-9]{7,}$', self.cont_no.upper()):
                self.cont_no = self.cont_no.upper()
            else:
                raise ValidationError("You have Entered a Wrong Container Number or Format: %s \nFormat is AAAA0000000"
                                      "\nFirst Four Character Must be Alphabet and Last Seven Character Must be Numeric"
                                      % self.cont_no.upper())

    @api.constrains('cont_no')
    def container_no_check_constrains(self):
        if self.cont_no:
            if re.match('^[A-Z]{4}[0-9]{7,}$', self.cont_no.upper()):
                return True
            else:
                raise ValidationError("You have Entered a Wrong Container Number or Format: %s \nFormat is AAAA0000000,"
                                      "\nFirst Four Character Must be Alphabet and Last Seven Character Must be Numeric"
                                      % self.cont_no.upper())

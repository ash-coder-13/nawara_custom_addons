# -*- coding: utf-8 -*-
import re
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _, exceptions
from odoo.fields import Selection
from odoo.exceptions import ValidationError, UserError, RedirectWarning


class AccountMoveLineInher(models.Model):
    _inherit = 'sale.order.line'

    crt_no = fields.Char('Container Number', size=11)
    weight = fields.Float()
    project_no = fields.Char('Seal Number')
    form = fields.Many2one('from.qoute', string="From")
    to = fields.Many2one('to.quote', string="To")
    fleet_type = fields.Many2one('fleet', string="Fleet Type")
    product_id = fields.Many2one('product.product', string='Product', required=False)

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

    @api.onchange('form', 'to', 'fleet_type')
    def add_charges(self):
        """ Calculating Charges As per Transporter, To, From, and fleet_type for selected customer"""

        if self.order_id.partner_id and self.form and self.to and self.fleet_type:
            trans = self.env['res.partner'].search([('id', '=', self.order_id.partner_id.id)])
            for x in trans.route_id:
                if self.order_id.by_customer:
                    if self.form.id == x.form.id and self.to.id == x.to.id and self.fleet_type == x.fleet_type \
                            and self.order_id.by_customer == x.by_customer:
                        self.price_unit = x.trans_charges
                else:
                    if self.form.id == x.form.id and self.to.id == x.to.id and self.fleet_type == x.fleet_type:
                        self.price_unit = x.trans_charges


class TransportInfo(models.Model):
    _inherit = 'sale.order'
    _order = "priority_type,name asc"

    def mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.sales_imp_id and i.detention and (i.state != 'done'):
                exp_date_3 = fields.Date.from_string(i.detention) - timedelta(days=3)
                exp_date_2 = fields.Date.from_string(i.detention) - timedelta(days=2)
                exp_date_1 = fields.Date.from_string(i.detention) - timedelta(days=1)
                if date_now == exp_date_3 or date_now == exp_date_2 or date_now == exp_date_1:
                    mail_content = "Dear team,<br><strong>" + str(
                        i.name) + "'s</strong> detention date is <strong>" + str(
                        i.detention) + "</strong>. Please clear this terminal operation as soon as possible to avoid the penalty.<br>Thanks &amp; Regards,<br>Odoo Reminder !"
                    main_content = {
                        'subject': _('DETENTION ALERT: Customer %s ( B/L Number-%s) Will Expire On %s') % (
                        i.partner_id.name, i.bill_no, i.detention),
                        'body_html': mail_content,
                        'email_to': "m.vaseem@ntf-group.com",
                        'email_cc': "operation@ntf-group.com",
                    }
                    self.env['mail.mail'].create(main_content).send()

    suppl_name = fields.Many2one('res.partner', string="Supplier Name", )
    suppl_freight = fields.Float(string='Supplier Freight')
    by_customer = fields.Many2one('by.customer', string="By Customer")
    no_by_customer = fields.Boolean(string="No By Customer", )
    bill_type = fields.Selection([('B/L Number', 'B/L Number'), ('Container Wise', 'Container Wise')],
                                 string="Billing Type")
    bill_no = fields.Char(string='B/L Number')
    inv_chk = fields.Boolean(string="inv")
    import_chk = fields.Boolean(string="Import Check")
    pod_chk = fields.Boolean(string="pod")
    freight_link = fields.Many2one('freight.forward', string='Freight Forwarding', readonly=True)
    trans_link = fields.Many2one('freight.forward', string='Freight Link', readonly=True)
    acc_link = fields.Many2one('account.move', string='Invoice', readonly=True)
    inter_num = fields.Integer(string="Internal Number")
    driver = fields.Char(string="Driver")
    driver_num = fields.Char(string="Driver Number")
    form_t = fields.Many2one('from.qoute', string="From")
    to_t = fields.Many2one('to.quote', string="To")
    fleet_type = fields.Many2one('fleet', string="Fleet Type")
    upload_date = fields.Date(string="Loading Date")
    delivery_date = fields.Date(string="Arrival Date")
    eir_date = fields.Date(string="EIR Date")
    return_date = fields.Date(string="Return Date")
    stuff_date = fields.Date(string="Stuffing Date")
    recive_name = fields.Char(string="Receiver Name")
    recive_mob = fields.Char(string="Receiver Mobile")
    sales_id = fields.Many2one('export.logic', "Export Link")
    sales_imp_id = fields.Many2one('import.logic', "Import Link")
    demurrage = fields.Date(string="Demurrage")
    detention = fields.Date(string="Detention", required=False, compute="_compute_demurrage_detention_dates")
    our_job = fields.Char(string="Our Job No", required=False, )
    sr_no = fields.Char(string="Sr No", required=False, )
    customer_ref = fields.Char(string="Customer Ref", required=False, )
    custom_dec = fields.Char(string="Custom Dec", required=False, )
    bayan_no = fields.Char(string="Bayan No", required=False, )
    final_date = fields.Date(string="Final Date", required=False, )
    customer_site = fields.Many2one('import.site', string="Site", required=False, )
    sale_status = fields.Many2one(comodel_name="import.status", string="Sale Status", required=False,
                                  ondelete='restrict')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Transportation Vehicle", ondelete='restrict')
    driver_id = fields.Many2one('res.partner', string="Transportation Driver", ondelete='restrict')
    trans_mode = fields.Selection(string="Transportation Mode", selection=[('in', 'Internal'), ('ex', 'External'), ],
                                  required=False, )
    attachments = fields.One2many(comodel_name="vehicle.accident.attachment", inverse_name="sale_attachments",
                                  string="POD's", required=False, )
    pull_out = fields.Boolean(string="Make Pull Out", )
    re_pull_out = fields.Boolean(string="Make Re Pull Out", )
    move_from = fields.Many2one(comodel_name="import.site", string="From Site", required=False, )
    move_to = fields.Many2one(comodel_name="stock.warehouse", string="To Warehouse", required=False, )
    p_vehicle_id = fields.Many2one('fleet.vehicle', string="PullOut Vehicle", ondelete='restrict', required=False, )
    p_driver_id = fields.Many2one('res.partner', string="PullOut Driver", ondelete='restrict', required=False, )
    driver_expenses = fields.Float(string="Driver TripMoney", required=False, )
    pullout_status = fields.Selection([('StartPullOut', 'StartPullOut'), ('InProcess', 'InProcess'),
                                       ('Completed', 'Completed')], default='StartPullOut', string="PullOut Status")
    pullout_charges = fields.One2many(comodel_name="customer.pullout", inverse_name="sale_pullout",
                                      string="PullOut Information", required=False, )
    pullout_mode = fields.Selection(string="Pullout Mode", selection=[('in', 'Internal'), ('ex', 'External'), ],
                                    required=False, )
    p_transporter_id = fields.Many2one('res.partner', string="Transporter", ondelete='restrict', required=False, )
    in_terminal = fields.Boolean(string="In Terminal", )
    in_storage = fields.Boolean(string="In Storage", )
    pullout_date = fields.Datetime(string="Pullout Complete Date", required=False, )
    no_invoice = fields.Boolean(string="No Invoice", )
    pullout_type = fields.Selection([('Self', 'Self'), ('Customer', 'Customer')], string="PullOut Type")
    service_type = fields.Selection([('import', 'Import'), ('export', 'Export')], string="Service Name")
    priority_type = fields.Selection([('0', 'High'), ('1', 'Low')], string="Priority Type")
    container_num = fields.Char(string="Container Number", required=False, compute='_compute_container_num', store=True)
    self_reason = fields.Char(string="Self PullOut Reason", required=False, )
    breakdown = fields.Boolean(string="BreakDown", )
    breakdown_complete = fields.Boolean(string="BreakDown Complete", )
    b_driver_id = fields.Many2one('res.partner', string="BreakDown Driver", ondelete='restrict', required=False, )
    b_vehicle_id = fields.Many2one('fleet.vehicle', string="BreakDown Vehicle", ondelete='restrict', required=False, )
    b_driver_expenses = fields.Float(string="Driver TripMoney", required=False, )
    breakdown_mode = fields.Selection(string="Breakdown Mode", selection=[('in', 'Internal'), ('ex', 'External'), ],
                                      default='in', required=False)
    b_transporter_id = fields.Many2one('res.partner', string="Breakdown Transporter", ondelete='restrict',
                                       required=False, )
    b_location = fields.Char('Location')
    b_remarks = fields.Char('Remarks')
    b_attachments = fields.One2many(comodel_name="vehicle.accident.attachment",
                                    inverse_name="breakdown_sale_attachments", string="Breakdown's Docs",
                                    required=False, )
    transportation_status = fields.Selection([('InProcess', 'InProcess'), ('Completed', 'Completed')],
                                             default='InProcess', string="Transportation Status")
    delivery = fields.Date(string="Delivery Date")
    ship_link = fields.Many2one(comodel_name="shipment.order", string="Shipment Link", required=False, )

    shuttling = fields.Boolean(string="Shuttling", )
    s_driver_id = fields.Many2one('res.partner', string="Shuttling Driver", ondelete='restrict', required=False, )
    s_vehicle_id = fields.Many2one('fleet.vehicle', string="Shuttling Vehicle", ondelete='restrict', required=False, )
    s_driver_expenses = fields.Float(string="Driver TripMoney", required=False, )
    shuttling_status = fields.Selection([('InProcess', 'InProcess'), ('Completed', 'Completed')],
                                        string="Shuttling Status")
    shuttling_mode = fields.Selection(string="Shuttling Mode", selection=[('in', 'Internal'), ('ex', 'External'), ],
                                      default='in', required=False)
    s_transporter_id = fields.Many2one('res.partner', string="Shuttling Transporter", ondelete='restrict',
                                       required=False, )
    emp_col = fields.Boolean(string="Empty Collection")
    emp_driver_id = fields.Many2one('res.partner', string="Empty Collection Driver", ondelete='restrict',
                                    required=False, )
    emp_vehicle_id = fields.Many2one('fleet.vehicle', string="Empty Collection Vehicle", ondelete='restrict',
                                     required=False, )
    emp_driver_expenses = fields.Float(string="Driver TripMoney", required=False, )
    emp_status = fields.Selection([('InProcess', 'InProcess'), ('Completed', 'Completed')],
                                  string="Empty Collection Status")
    emp_mode = fields.Selection(string="Empty Collection Mode", selection=[('in', 'Internal'), ('ex', 'External'), ],
                                default='in', required=False)
    emp_transporter_id = fields.Many2one('res.partner', string="Empty Collection Transporter", ondelete='restrict',
                                         required=False, )
    extra_charges = fields.Boolean(string="Extra Charges")
    extra_expenses = fields.Float(string="Extra Expenses", required=False, )
    extra_reason = fields.Char(string="Reasons")
    extra_paid = fields.Boolean(string="Extra Charges Paid")
    extra_driver_id = fields.Many2one('res.partner', string="Driver/Transporter", ondelete='restrict', required=False, )
    invoice_done = fields.Boolean(string="Invoice Done", )
    way_date = fields.Date(string="WayBill Date", required=False, )
    pod_date = fields.Date(string="POD Date", required=False, )
    lead_days = fields.Char(string="Lead Days", required=False, compute="_compute_lead_days", store=True)
    trans_account = fields.Integer(string="Trans Mode Account", required=False, )
    to_mails = fields.Char(string="mail To", required=False, )
    warn_shuttling = fields.Integer(string="Warn Invoice", )
    vessel_number = fields.Char(string="Vessel Name", required=False, )
    dispatch_date = fields.Date(string="Dispatch Date", required=False, )
    empty_collection_date = fields.Date(string="Empty Collection Date", required=False, )
    rescheduling = fields.Boolean(string="Make Rescheduling")
    start_rescheduling = fields.Boolean(string="Rescheduling")
    rescheduling_status = fields.Selection([('InProcess', 'InProcess'), ('Completed', 'Completed')],
                                           string="Rescheduling Status")
    ret_col = fields.Boolean(string="Empty Return Collection")
    ret_driver_id = fields.Many2one('res.partner', string="Empty Return Collection Driver", ondelete='restrict',
                                    required=False, )
    ret_vehicle_id = fields.Many2one('fleet.vehicle', string="Empty Return Collection Vehicle", ondelete='restrict',
                                     required=False, )
    ret_driver_expenses = fields.Float(string="Driver TripMoney", required=False, )
    ret_status = fields.Selection([('InProcess', 'InProcess'), ('Completed', 'Completed')],
                                  string="Empty Return Collection Status")
    ret_mode = fields.Selection(string="Empty Return Collection Mode",
                                selection=[('in', 'Internal'), ('ex', 'External'), ],
                                default='in', required=False)
    ret_transporter_id = fields.Many2one('res.partner', string="Empty Return Collection Transporter",
                                         ondelete='restrict',
                                         required=False, )
    re_pull_out_ids = fields.One2many(comodel_name="re.pullout", inverse_name="order_id", string="Re PullOut")


    @api.depends('sales_id.vessel_date', 'sales_imp_id.vessel_date')
    def _compute_demurrage_detention_dates(self):
        for rec in self:
            if rec.sales_imp_id.vessel_date:
                rec.detention = rec.sales_imp_id.detention_date
            if rec.sales_id.vessel_date:
                rec.detention = rec.sales_id.detention_date
            else:
                rec.detention = False


    def rescheduling_start(self):
        if self.trans_mode == 'in':
            self.driver_id.is_reserved = False
            self.vehicle_id.is_reserved = False
            self.pod_chk = False
            self.driver_id = None
            self.vehicle_id = None
        self.rescheduling = True
        self.rescheduling_status = 'InProcess'


    def send_overdue_mail(self):
        records = self.env['sale.order'].search([('delivery', '!=', False)])
        email_rec = self.env['multi.mails'].search([])
        template = self.env.ref('custom_logistic.transportation_overdue_template')
        for rec in records:
            if datetime.strptime(str(datetime.now().date()), '%Y-%m-%d') == datetime.strptime(str(rec.delivery),
                                                                                              '%Y-%m-%d'):
                for email in email_rec.ntf_terminal:
                    rec.to_mails = email.name
                    self.env['mail.template'].browse(template.id).send_mail(rec.id)

    @api.onchange('trans_mode')
    def onchange_trans_mode(self):
        account = self.env['account_journal.configuration'].search([])
        if self.trans_mode and self.trans_mode == 'ex':
            self.trans_account = account.t_customer_account_ex.id
        else:
            self.trans_account = account.same_custom_invoice_account.id


    def emp_trip(self):
        if self.emp_driver_expenses > 0:
            account = self.env['account_journal.configuration'].search([])
            invoice = self.env['account.move'].search([])
            if self.emp_mode == 'in':
                partner = self.emp_driver_id.id
                journal = account.t_vendor_journal.id
                account = account.t_vendor_account.id
            elif self.emp_mode == 'ex':
                partner = self.emp_transporter_id.id
                journal = account.t_vendor_journal_ex.id
                account = account.t_vendor_account_ex.id
            create_invoice = invoice.create({
                'journal_id': journal,
                'partner_id': partner,
                'invoice_date': date.today(),
                'type': "in_invoice",
                'sale_link': self.id,
                'invoice_from': 'trans',
            })
            create_invoice.invoice_line_ids.create({
                'quantity': 1,
                'price_unit': self.emp_driver_expenses,
                'account_id': account,
                'name': "Empty Collection " + self.name,
                'move_id': create_invoice.id,
                'crt_no': self.container_num

            })
            self.emp_status = 'InProcess'
            if self.emp_mode == 'in':
                self.emp_driver_id.is_reserved = True
                self.emp_vehicle_id.is_reserved = True
        self.empty_collection_date = datetime.today()


    def emp_complete(self):
        for rec in self:
            rec.emp_status = "Completed"
            if rec.emp_mode == 'in':
                rec.emp_driver_id.is_reserved = False
                rec.emp_vehicle_id.is_reserved = False


    def ret_trip(self):
        account = self.env['account_journal.configuration'].search([])
        invoice = self.env['account.move'].search([])
        if self.ret_mode == 'in':
            partner = self.ret_driver_id.id
            journal = account.t_vendor_journal.id
            account = account.t_vendor_account.id
        elif self.ret_mode == 'ex':
            partner = self.ret_transporter_id.id
            journal = account.t_vendor_journal_ex.id
            account = account.t_vendor_account_ex.id
        if partner and self.form_t and self.to_t and self.fleet_type:
            trans = self.env['res.partner'].search([('id', '=', partner)])
            for x in trans.route_id:
                if self.form_t.id == x.form.id and self.to_t.id == x.to.id and self.fleet_type == x.fleet_type and self.ret_col == False:
                    self.ret_driver_expenses = x.trans_charges
        if self.ret_driver_expenses > 0:
            create_invoice = invoice.create({
                'journal_id': journal,
                'partner_id': partner,
                'invoice_date': date.today(),
                'type': "in_invoice",
                'sale_link': self.id,
                'invoice_from': 'trans',
            })

            create_invoice.invoice_line_ids.create({
                'quantity': 1,
                'price_unit': self.ret_driver_expenses,
                'account_id': account,
                'name': "Empty Return Collection " + self.name,
                'move_id': create_invoice.id,
                'crt_no': self.container_num

            })
            self.ret_status = 'InProcess'
            if self.ret_mode == 'in':
                self.ret_driver_id.is_reserved = True
                self.ret_vehicle_id.is_reserved = True

        else:
            raise UserError(_('No Charges for this route for this driver or transporter'))


    def ret_complete(self):
        for rec in self:
            rec.ret_status = "Completed"
            if rec.ret_mode == 'in':
                rec.ret_driver_id.is_reserved = False
                rec.ret_vehicle_id.is_reserved = False


    def action_confirm(self):
        res = super(TransportInfo, self).action_confirm()
        if not self.driver_id and not self.vehicle_id and not self.to_t and not self.form_t and not self.fleet_type:
            raise ValidationError("You Must Add Driver and Other Information in 'Transportation Info' Before Confirm")
        filtered_records = self.env['account.move.line'].search([('partner_id', '=', self.partner_id.id),
                                                                 ('account_id.internal_type', '=', 'receivable'),
                                                                 ('balance', '!=', 0),
                                                                 ('full_reconcile_id', '=', False),
                                                                 ('account_id.reconcile', '=', True)
                                                                 ])
        amount = sum(line.debit for line in filtered_records)
        if self.partner_id.credit_limit:
            if self.partner_id.credit_limit <= amount:
                email_rec = self.env['multi.mails'].search([])
                template = self.env.ref('custom_logistic.credit_limit_email_template')
                for email in email_rec.sale_support:
                    self.to_mails = email.name
                    self.env['mail.template'].browse(template.id).send_mail(self.id)

        filtered_payment = self.env['account.move'].search([('partner_id', '=', self.partner_id.id),
                                                               ('state', '!=', 'paid'),
                                                               ('amount_total', '!=', 0),
                                                               ])
        if filtered_payment:
            email_rec = self.env['multi.mails'].search([])
            template = self.env.ref('custom_logistic.payment_term_email_template')
            for email in email_rec.sale_support:
                self.to_mails = email.name
                self.env['mail.template'].browse(template.id).send_mail(self.id)
        return res

    @api.onchange('partner_id')
    def onchange_method_partner_id(self):
        if self.partner_id:
            if not self.partner_id.by_customer:
                self.no_by_customer = True
            else:
                self.no_by_customer = False


    def shuttling_trip(self):

        if self.s_driver_expenses > 0 and self.order_line:
            account = self.env['account_journal.configuration'].search([])
            invoice = self.env['account.move'].search([])
            if self.shuttling_mode == 'in':
                partner = self.s_driver_id.id
                journal = account.t_vendor_journal.id
                account = account.t_vendor_account.id
            elif self.shuttling_mode == 'ex':
                partner = self.s_transporter_id.id
                journal = account.t_vendor_journal_ex.id
                account = account.t_vendor_account_ex.id

            create_invoice = invoice.create({
                'journal_id': journal,
                'partner_id': partner,
                'invoice_date': date.today(),
                'type': "in_invoice",
                'sale_link': self.id,
                'invoice_from': 'trans',
            })
            for x in self.order_line:
                create_invoice.invoice_line_ids.create({
                    'quantity': x.product_uom_qty,
                    'price_unit': self.s_driver_expenses,
                    'crt_no': x.crt_no,
                    'account_id': account,
                    'name': x.name + " Shuttling Charges",
                    'move_id': create_invoice.id
                })
            self.shuttling_status = 'InProcess'
            if self.shuttling_mode == 'in':
                self.s_driver_id.is_reserved = True
                self.s_vehicle_id.is_reserved = True

    def shuttling_complete(self):
        for rec in self:
            rec.shuttling_status = "Completed"
            if rec.shuttling_mode == 'in':
                rec.s_driver_id.is_reserved = False
                rec.s_vehicle_id.is_reserved = False
            rec.sale_status = 24


    def unlink(self):
        for rec in self:
            if rec.ship_link:
                rec.ship_link.container = self.env['sale.order'].search_count([('ship_link', '=', rec.ship_link.id)]) - 1
            return super(TransportInfo, self).unlink()

    def breakdown_button(self):
        if self.breakdown:
            if self.b_driver_expenses > 0.0:
                account = self.env['account_journal.configuration'].search([])

                if self.breakdown_mode == 'in':
                    partner = self.b_driver_id.id
                    journal = account.t_vendor_journal.id
                    account = account.t_vendor_account.id
                elif self.breakdown_mode == 'ex':
                    partner = self.b_transporter_id.id
                    journal = account.t_vendor_journal_ex.id
                    account = account.t_vendor_account_ex.id

                create_invoice = self.env['account.move'].create({
                    'journal_id': journal,
                    'partner_id': partner,
                    'invoice_date': date.today(),
                    'sale_id': self.id,
                    'type': "in_invoice",
                    'sale_link': self.id,
                    'invoice_from': 'trans',
                })
                create_invoice_lines = create_invoice.invoice_line_ids.create({
                    'quantity': 1,
                    'price_unit': self.b_driver_expenses,
                    'account_id': account,
                    'name': 'BreakDown Driver TripMoney',
                    'move_id': create_invoice.id
                })

            if self.trans_mode == 'in':
                self.driver_id.is_reserved = False
                self.vehicle_id.is_reserved = False
                self.vehicle_id.breakdown = True
            if self.breakdown_mode == 'in':
                self.env['fleet.vehicle.accident'].create({
                    'vehicle_id': self.b_vehicle_id.id,
                    'driver_id': self.b_driver_id.id,
                    'accident_date': date.today(),
                    'location': self.b_location,
                    'remarks': self.b_remarks,
                    'attachments': self.b_attachments,
                })
                self.b_driver_id.is_reserved = True
                self.b_vehicle_id.is_reserved = True
            self.breakdown_complete = True
            self.state = 'rec'

    @api.depends('order_line')
    def _compute_container(self):
        """
        @api.depends() should contain all fields that will be used in the calculations.
        """
        for rec in self:
            crt_list = []
            if rec.order_line:
                for x in rec.order_line:
                    if x.crt_no:
                        crt_list.append(x.crt_no.encode('ascii', 'ignore'))
                rec.container_num_m = crt_list
                rec.count_crt = len(crt_list)

    container_num_m = fields.Char(string="Container Number", required=False, compute='_compute_container', store=True)
    count_crt = fields.Integer(string="Count Of Container", required=False, compute='_compute_container', store=True)

    @api.depends('order_line')
    def _compute_container_num(self):
        """
        @api.depends() should contain all fields that will be used in the calculations.
        """
        for rec in self:
            if rec.order_line:
                rec.container_num = rec.order_line[0].crt_no

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('air', 'Issue AirWay Bill'),
        ('trip', 'Vendor Trip Money'),
        ('rec', 'Received POD'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


    def sent_terminal(self):
        amount = 0.0
        if self.partner_id.id and self.order_line.form and self.order_line.to and self.order_line.fleet_type:
            trans = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
            for x in trans.route_id:
                if self.order_line.form.id == x.form.id and self.order_line.to.id == x.to.id \
                        and self.order_line.fleet_type == x.fleet_type:
                    amount = x.trans_charges
        if not amount > 0.0:
            raise ValidationError('No Payment Defined For This Route, Kindly Check Your Order Line')
        self.in_terminal = True
        email_rec = self.env['multi.mails'].search([])
        template = self.env.ref('custom_logistic.tot_email_template')
        for email in email_rec.ntf_terminal:
            self.to_mails = email.name
            self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.sale_status = 3


    def sent_lock(self):
        self.priority_type = False
        if self.warn_shuttling == 0:
            self.warn_shuttling += 1
            view = self.env.ref('sh_message.sh_message_wizard').id
            context = dict(self._context or self)
            context['message'] = "Please make sure if it’s an export job the port shuttling is completed, " \
                                 "If yes then click Button Again."
            return {'name': 'Warning',
                    'type': 'ir.actions.act_window',

                    'view_mode': 'form',
                    'res_model': 'sh.message.wizard',
                    'views': [(view, 'form')],
                    'view_id': view,
                    'target': 'new',
                    'context': context,
                    }

        self.state = 'done'
        sale = ''
        if self.sales_imp_id:
            sale = self.env['sale.order'].search([('sales_imp_id', '=', self.sales_imp_id.id)])
        if self.sales_id:
            sale = self.env['sale.order'].search([('sales_id', '=', self.sales_id.id)])
        if self.ship_link:
            sale = self.env['sale.order'].search([('ship_link', '=', self.ship_link.id)])
        if self.trans_link:
            sale = self.env['sale.order'].search([('trans_link', '=', self.trans_link.id)])

        check = 0
        for x in sale:
            if x.state == 'done':
                check += 1
        if check == len(sale) and len(sale) > 0:
            email_rec = self.env['multi.mails'].search([])
            template = self.env.ref('custom_logistic.tcc_email_template')
            for email in email_rec.ntf_terminal:
                self.to_mails = email.name
                self.env['mail.template'].browse(template.id).send_mail(self.id)


    def get_sale_name(self):
        name = ' '
        if self.sales_imp_id:
            name = self.sales_imp_id.s_no
        if self.sales_id:
            name = self.sales_id.sr_no
        if self.ship_link:
            name = self.ship_link.name
        if self.trans_link:
            name = self.trans_link.sr_no

        return name


    def sent_storage(self):
        self.in_storage = True


    def airway(self):
        if self.order_line[0].crt_no:
            self.state = 'air'
            self.in_storage = False
            self.sale_status = 4
            if not self.way_date:
                self.way_date = date.today()
            return self.env.ref('airway_bill.module_report').report_action(self, data=None)

            # return self.env['report'].get_action(self, 'airway_bill.module_report')
        else:
            raise UserError(_("Please Add Container Number To Print WayBill"))


    def pay_extra_charges(self):
        if self.extra_charges and self.extra_expenses > 0.0:
            account = self.env['account_journal.configuration'].search([])
            invoice = self.env['account.move'].search([])
            acc = account.t_vendor_account.id
            jrl = account.t_vendor_journal.id
            if not self.extra_paid:

                create_invoice = invoice.create({
                    'journal_id': jrl,
                    'partner_id': self.extra_driver_id.id,
                    'invoice_date': self.date_order,
                    'customer_site': self.customer_site.id,
                    'type': "in_invoice",
                    'sale_link': self.id,
                    'invoice_from': 'trans',
                })
                create_invoice.invoice_line_ids.create({
                    'quantity': 1,
                    'price_unit': self.extra_expenses,
                    'account_id': acc,
                    'name': self.extra_reason,
                    'move_id': create_invoice.id
                })
                self.extra_paid = True
            else:
                raise ValidationError('Extra Charges Already Paid')


    def trip(self):
        if not self.pod_chk:
            self.pod_chk = True
            account = self.env['account_journal.configuration'].search([])
            invoice = self.env['account.move'].search([])
            partner_name = 0
            amount = 0

            if self.trans_mode == "in":
                acc = account.t_vendor_account.id
                jrl = account.t_vendor_journal.id
                partner_name = self.driver_id.id
                if self.driver_id.id and self.form_t.id and self.to_t.id and self.fleet_type:
                    trans = self.env['res.partner'].search([('id', '=', self.driver_id.id)])
                    for x in trans.route_id:
                        if self.form_t.id == x.form.id and self.to_t.id == x.to.id and self.fleet_type == x.fleet_type:
                            amount = x.trans_charges
                    if not amount > 0:
                        raise ValidationError('No Payment defined for this route')

            if self.trans_mode == "ex":
                acc = account.t_vendor_account_ex.id
                jrl = account.t_vendor_journal_ex.id
                partner_name = self.suppl_name.id
                if self.suppl_freight > 0.0:
                    amount = self.suppl_freight
                else:
                    raise ValidationError('No Payment defined for this route')

            create_invoice = invoice.create({
                'journal_id': jrl,
                'partner_id': partner_name,
                'invoice_date': self.date_order,
                'customer_site': self.customer_site.id,
                'type': "in_invoice",
                'sale_link': self.id,
                'invoice_from': 'trans',
            })
            for x in self.order_line:
                create_invoice_lines = create_invoice.invoice_line_ids.create({
                    'quantity': x.product_uom_qty,
                    'price_unit': amount,
                    'crt_no': x.crt_no,
                    'account_id': acc,
                    'name': x.name,
                    'move_id': create_invoice.id
                })
        self.dispatch_date = datetime.today()
        if self.state == 'air':
            self.state = 'trip'
        if self.rescheduling is True:
            self.rescheduling = False
            self.rescheduling_status = 'Completed'
        if self.trans_mode == 'in':
            self.driver_id.is_reserved = True
            self.vehicle_id.is_reserved = True


    def pull_out_trip(self):
        account = self.env['account_journal.configuration'].search([])
        invoice = self.env['account.move'].search([])

        if self.pullout_mode == 'in':
            partner = self.p_driver_id.id
            journal = account.t_vendor_journal.id
            account = account.t_vendor_account.id
        elif self.pullout_mode == 'ex':
            partner = self.p_transporter_id.id
            journal = account.t_vendor_journal_ex.id
            account = account.t_vendor_account_ex.id

        if self.driver_expenses > 0 and self.order_line:
            create_invoice = invoice.create({
                'journal_id': journal,
                'partner_id': partner,
                'invoice_date': self.date_order,
                'customer_site': self.move_from.id,
                'type': "in_invoice",
                'sale_link': self.id,
                'invoice_from': 'trans',
            })
            for x in self.order_line:
                create_invoice_lines = create_invoice.invoice_line_ids.create({
                    'quantity': x.product_uom_qty,
                    'price_unit': self.driver_expenses,
                    'crt_no': x.crt_no,
                    'account_id': account,
                    'name': x.name,
                    'move_id': create_invoice.id
                })
            self.pullout_status = 'InProcess'
            if self.pullout_mode == 'in':
                self.p_driver_id.is_reserved = True
                self.p_vehicle_id.is_reserved = True
        self.pullout_date = datetime.today()


    def pull_out_complete(self):
        for rec in self:
            if rec.pullout_mode == 'in':
                rec.p_driver_id.is_reserved = False
                rec.p_vehicle_id.is_reserved = False
            rec.pullout_status = "Completed"
            template = self.env.ref('custom_logistic.storage_email_template')
            self.env['mail.template'].browse(template.id).send_mail(rec.id)


    def receive(self):
        self.state = "rec"
        self.transportation_status = "Completed"
        self.priority_type = False
        if self.trans_mode == 'in':
            self.driver_id.is_reserved = False
            self.vehicle_id.is_reserved = False
        if not self.pod_date:
            self.pod_date = date.today()
        self.sale_status = 16

    @api.depends('way_date', 'pod_date')
    def _compute_lead_days(self):
        """
        @api.depends() should contain all fields that will be used in the calculations.
        """
        for rec in self:
            if rec.way_date and rec.pod_date:
                way = datetime.strptime(rec.way_date, '%Y-%m-%d').date()
                pod = datetime.strptime(rec.pod_date, '%Y-%m-%d').date()
                rec.lead_days = (pod - way).days


    def action_invoice_create(self):
        """Adding By_customer To Invoice"""
        account = self.env['account_journal.configuration'].search([])
        if self.shuttling is True and self.shuttling_status == 'Completed':
            new_record = super(TransportInfo, self).action_invoice_create()
            records = self.env['account.move'].search([('origin', '=', self.name)])
            if records:
                records.by_customer = self.by_customer.id
                records.our_job = self.our_job
                records.sr_no = self.sr_no
                records.customer_ref = self.customer_ref
                records.custom_dec = self.custom_dec
                records.bayan_no = self.bayan_no
                records.customer_site = self.customer_site.id
                records.final_date = self.final_date
                records.bill_num = self.bill_no
                records.billing_type = self.bill_type
                records.invoice_from = 'trans'
                self.acc_link = records.id
                records.sale_link = self.id,
                crt_list = []
                if self.trans_mode and self.trans_mode == 'ex':
                    line_account = account.t_customer_account_ex.id
                else:
                    line_account = account.same_custom_invoice_account.id

                for x, y in [(x, y) for x in records.invoice_line_ids for y in self.order_line]:
                    x.crt_no = y.crt_no
                    x.account_id = line_account
                    if x.crt_no:
                        crt_list.append(x.crt_no.encode('ascii', 'ignore'))
                records.container_num = crt_list

                if self.pullout_type == 'Customer':
                    self.acc_link.invoice_line_ids.create({
                        'quantity': 1,
                        'price_unit': self.partner_id.pullout_charges,
                        'account_id': account.t_pullout_account.id,
                        'name': "PullOut Charges",
                        'move_id': self.acc_link.id
                    })

            if self.pull_out and self.pullout_status == 'Completed':
                day = 0
                if datetime.now().date() >= (datetime.strptime(str(self.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                        days=self.partner_id.free_day)).date():
                    day = datetime.now().date() - (
                            datetime.strptime(str(self.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                        days=self.partner_id.free_day)).date()

                    if day.days > 0:
                        self.acc_link.invoice_line_ids.create({
                            'quantity': day.days,
                            'price_unit': self.partner_id.storage_charges,
                            'account_id': account.t_storage_account.id,
                            'name': "Storage Charges for " + str(day.days) + " Days",
                            'move_id': self.acc_link.id
                        })
            email_rec = self.env['multi.mails'].search([])
            template = self.env.ref('custom_logistic.ti_email_template')
            for email in email_rec.finance:
                self.to_mails = email.name
                self.env['mail.template'].browse(template.id).send_mail(self.id)
            return new_record

        elif not self.shuttling:
            new_record = super(TransportInfo, self).action_invoice_create()
            records = self.env['account.move'].search([('origin', '=', self.name)])
            if records:
                records.by_customer = self.by_customer.id
                records.our_job = self.our_job
                records.sr_no = self.sr_no
                records.customer_ref = self.customer_ref
                records.custom_dec = self.custom_dec
                records.bayan_no = self.bayan_no
                records.customer_site = self.customer_site.id
                records.final_date = self.final_date
                records.bill_num = self.bill_no
                records.billing_type = self.bill_type
                records.invoice_from = 'trans'
                self.acc_link = records.id
                records.sale_link = self.id,

                crt_list = []
                if self.trans_mode and self.trans_mode == 'ex':
                    line_account = account.t_customer_account_ex.id
                else:
                    line_account = account.same_custom_invoice_account.id
                for x, y in [(x, y) for x in records.invoice_line_ids for y in self.order_line]:
                    x.crt_no = y.crt_no
                    x.product_id = None
                    x.name = " Transportation Charges" + ' اجور نقل '.decode('utf-8')
                    x.account_id = line_account
                    if x.crt_no:
                        crt_list.append(x.crt_no.encode('ascii', 'ignore'))
                records.container_num = crt_list

                if self.pullout_type == 'Customer':
                    self.acc_link.invoice_line_ids.create({
                        'quantity': 1,
                        'price_unit': self.partner_id.pullout_charges,
                        'account_id': account.t_pullout_account.id,
                        'name': "PullOut Charges",
                        'move_id': self.acc_link.id
                    })

            if self.pull_out and self.pullout_status == 'Completed':
                day = 0
                if datetime.now().date() >= (datetime.strptime(str(self.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                        days=self.partner_id.free_day)).date():
                    day = datetime.now().date() - (
                            datetime.strptime(str(self.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                        days=self.partner_id.free_day)).date()

                    if day.days > 0:
                        self.acc_link.invoice_line_ids.create({
                            'quantity': day.days,
                            'price_unit': self.partner_id.storage_charges,
                            'account_id': account.t_storage_account.id,
                            'name': "Storage Charges for " + str(day.days) + " Days",
                            'move_id': self.acc_link.id
                        })
            email_rec = self.env['multi.mails'].search([])
            template = self.env.ref('custom_logistic.ti_email_template')
            for email in email_rec.finance:
                self.to_mails = email.name
                self.env['mail.template'].browse(template.id).send_mail(self.id)
            return new_record
        else:
            raise exceptions.except_orm(_('Shuttling in Process'), 'Wait until Shuttling not complete')


    def test_button(self):
        if self.pull_out and self.pullout_status == 'Completed':
            if datetime.now().date() >= (datetime.strptime(str(self.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                    days=self.partner_id.free_day)).date():
                day = datetime.now().date() - (
                        datetime.strptime(str(self.pullout_date), '%Y-%m-%d %H:%M:%S') + timedelta(
                    days=self.partner_id.free_day)).date()


    def new_create_invoice(self):
        """Creates invoices"""
        self.action_confirm()
        self.priority_type = False
        self.action_invoice_create()
        self.inv_chk = True
        self.state = 'done'

    @api.onchange('form_t', 'to_t', 'fleet_type', 'service_type')
    def add_charges(self):
        """ Calculating Charges As per Transporter, To, From, and fleet_type for selected Supplier"""
        if self.suppl_name and self.form_t and self.to_t and self.fleet_type and self.service_type:
            trans = self.env['res.partner'].search([('id', '=', self.suppl_name.id)])
            for x in trans.route_id:
                if self.form_t.id == x.form.id and self.to_t.id == x.to.id and self.fleet_type == x.fleet_type and \
                        self.service_type == x.service_type:
                    self.suppl_freight = x.trans_charges

        if self.suppl_name and self.form_t and self.to_t and self.fleet_type and self.service_type is False:
            trans = self.env['res.partner'].search([('id', '=', self.suppl_name.id)])
            for x in trans.route_id:
                if self.form_t.id == x.form.id and self.to_t.id == x.to.id and self.fleet_type == x.fleet_type:
                    self.suppl_freight = x.trans_charges


class CustomerPullOutCharges(models.Model):
    _name = 'customer.pullout'
    _rec_name = 'name'

    name = fields.Char(string="Charges Description", required=True, )
    amount = fields.Float(string="Amount", required=True, )
    sale_pullout = fields.Many2one(comodel_name="sale.order", string="Transport PullOut", required=False, )


class ShipmentOrder(models.Model):
    _name = 'shipment.order'
    _rec_name = 'name'
    _description = 'Shipment Order'
    _inherit = 'mail.thread'

    name = fields.Char(string="Shipment Number")
    container = fields.Integer(string="Number Of Shipments", required=True, default=1, track_visibility='onchange')
    customer = fields.Many2one(comodel_name="res.partner", string="Customer", required=True, )
    branch = fields.Many2one(comodel_name="res.branch", string="Branch", required=True, )
    vessel_number = fields.Char(string="Vessel Name", required=True, )
    bill_number = fields.Char(string="Bill Number", required=True, translate=True)
    state = fields.Selection(string="Shipment Status",
                             selection=[('draft', 'Draft'), ('in', 'In Process'), ('done', 'Done'), ], default='draft',
                             required=False, track_visibility='onchange')
    count = fields.Integer(string="Shipment Count", required=False, compute='shipment_count')
    invoice_id = fields.Many2one(comodel_name="account.move", string="Shipment Invoice", required=False, )
    c_ref = fields.Char(string="Customer Reference", required=False, )
    warn_add_shipment = fields.Integer(string="warn_add_shipment", required=False, )

    def create_account_journal(self):
        if not self.env['account_journal.configuration'].search([]):
            record = self.env['account_journal.configuration'].create({
                'name': "Accounts and Journals Configuration"
            })


    def create_shipment(self):
        self.shipment(self.container)


    def add_shipment(self):
        if self.warn_add_shipment == 0:
            self.warn_add_shipment += 1
            view = self.env.ref('sh_message.sh_message_wizard').id
            context = dict(self._context or self)
            context['message'] = "Do you Really Want To Add Shipment, If yes then click button again."
            return {'name': 'Warning',
                    'type': 'ir.actions.act_window',

                    'view_mode': 'form',
                    'res_model': 'sh.message.wizard',
                    'views': [(view, 'form')],
                    'view_id': view,
                    'target': 'new',
                    'context': context,
                    }
        self.shipment(1)
        self.container = self.count

    def shipment(self, shipment):
        self.warn_add_shipment = 0
        get_id = self.env['product.template'].search([])
        value = 0
        for x in get_id:
            if x.name == "Container":
                value = x.id
        for rec in range(shipment):
            records = self.env['sale.order'].create({
                'partner_id': self.customer.id,
                'ship_link': self.id,
                'vessel_number': self.vessel_number,
                'bill_number': self.bill_number,
                'state': 'draft',
                'no_invoice': True,
            })

            self.env['sale.order.line'].create({
                'name': 'Shipment Transportation',
                'order_id': records.id,
                'product_id': value,
                'product_uom_qty': 1.0,
                'product_uom': 1,
            })

        self.state = 'in'
        return True

    def create_invoice(self):
        sale = self.env['sale.order'].search([('ship_link', '=', self.id)])
        account = self.env['account_journal.configuration'].search([])
        amt = 0.0
        check = 0

        for x in sale:
            if x.state == 'done':
                check += 1
        if check > 0 and check == len(sale):
            origin = sale[0].name
            records = self.env['account.move'].create({
                'partner_id': self.customer.id,
                'invoice_date': date.today(),
                'type': "out_invoice",
                'journal_id': account.p_invoice_journal.id,
                'customer_ref': self.c_ref,
                'origin': origin,
                'ship_link': self.id,
                'invoice_from': 'trans_pro',
            })

            for x in sale:
                records.invoice_line_ids.create({
                    'name': 'Shipment Transportation Charges for ' + x.order_line.form.name + "--"
                            + x.order_line.to.name + ' for ' + x.name + ' اجور نقل '.decode('utf-8'),
                    'quantity': x.order_line.product_uom_qty,
                    'product_id': x.order_line.product_id.id,
                    'price_unit': x.order_line.price_unit,
                    'account_id': x.trans_account,
                    'crt_no': x.order_line.crt_no,
                    'move_id': records.id,
                })
                if x.pullout_type == 'Customer':
                    records.invoice_line_ids.create({
                        'quantity': 1,
                        'price_unit': x.partner_id.pullout_charges,
                        'account_id': account.t_pullout_account.id,
                        'name': x.name + "PullOut Charges",
                        'move_id': records.id
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
                            records.invoice_line_ids.create({
                                'quantity': day.days,
                                'price_unit': x.partner_id.storage_charges,
                                'account_id': account.t_storage_account.id,
                                'name': "Storage Charges for " + str(day.days) + " Days",
                                'move_id': records.id
                            })

                x.state = 'done'
                x.invoice_status = 'invoiced'
                x.invoice_done = True
                amt = amt + x.amount_total

            records.amount_total = amt
            records.state = 'draft'
            self.invoice_id = records.id
            self.state = 'done'
        else:
            raise exceptions.except_orm(_('Shipment in Process'), 'Wait until Shipment Transportation not complete')


    def unlink(self):
        for order in self:
            if order.state not in 'draft':
                raise exceptions.except_orm(_('Shipment in process or done!'),
                                            'You can not delete a Shipment in process or done! Try to cancel it'
                                            ' before.')
        return super(ShipmentOrder, self).unlink()


    def shipment_count(self):
        for rec in self:
            rec.count = self.env['sale.order'].search_count([('ship_link', '=', rec.id)])

    @api.model
    def create(self, vals):
        """Shipment Order Sequence"""
        vals['name'] = self.env['ir.sequence'].next_by_code('shipment.order')
        new_record = super(ShipmentOrder, self).create(vals)
        return new_record


class ResBranch(models.Model):
    _name = 'res.branch'
    _rec_name = 'name'

    name = fields.Char(string="Branch Name", required=True)


class RePullout(models.Model):
    _name = 're.pullout'
    _rec_name = 'order_id'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Re PullOut Vehicle", ondelete='restrict', required=False, )
    driver_id = fields.Many2one('res.partner', string="Re PullOut Driver", ondelete='restrict', required=False, )
    driver_expenses = fields.Float(string="Driver TripMoney", required=False, )
    pullout_status = fields.Selection([('StartPullOut', 'StartPullOut'), ('InProcess', 'InProcess'),
                                       ('Completed', 'Completed')], default='StartPullOut', string="Re PullOut Status")
    pullout_mode = fields.Selection(string="Re Pullout Mode", selection=[('in', 'Internal'), ('ex', 'External'), ],
                                    required=False, )
    transporter_id = fields.Many2one('res.partner', string="Transporter", ondelete='restrict', required=False, )
    order_id = fields.Many2one(comodel_name="sale.order", string="sale Order", required=False, )
    pullout_date = fields.Datetime(string="Re Pullout Complete Date", required=False, )
    pullout_type = fields.Selection([('Self', 'Self'), ('Customer', 'Customer')], string="Re PullOut Type")
    move_from = fields.Many2one(comodel_name="import.site", string="From Site", required=False, )
    move_to = fields.Many2one(comodel_name="stock.warehouse", string="To Warehouse", required=False, )
    self_reason = fields.Char(string="Self PullOut Reason", required=False, )


    def pull_out_trip(self):
        account = self.env['account_journal.configuration'].search([])
        invoice = self.env['account.move'].search([])

        if self.pullout_mode == 'in':
            partner = self.driver_id.id
            journal = account.t_vendor_journal.id
            account = account.t_vendor_account.id
        elif self.pullout_mode == 'ex':
            partner = self.transporter_id.id
            journal = account.t_vendor_journal_ex.id
            account = account.t_vendor_account_ex.id

        if self.driver_expenses > 0:
            create_invoice = invoice.create({
                'journal_id': journal,
                'partner_id': partner,
                'invoice_date': self.order_id.date_order,
                'customer_site': self.move_from.id,
                'type': "in_invoice",
                'sale_link': self.order_id.id,
                'invoice_from': 'trans',
            })
            for x in self.order_id.order_line:
                _ = create_invoice.invoice_line_ids.create({
                    'quantity': x.product_uom_qty,
                    'price_unit': self.driver_expenses,
                    'crt_no': x.crt_no,
                    'account_id': account,
                    'name': x.name,
                    'move_id': create_invoice.id
                })
            self.pullout_status = 'InProcess'
            if self.pullout_mode == 'in':
                self.driver_id.is_reserved = True
                self.vehicle_id.is_reserved = True

    def pull_out_complete(self):
        for rec in self:
            if rec.pullout_mode == 'in':
                rec.driver_id.is_reserved = False
                rec.vehicle_id.is_reserved = False
            rec.pullout_status = "Completed"
            rec.pullout_date = datetime.today()
            template = self.env.ref('custom_logistic.storage_email_template')
            self.env['mail.template'].browse(template.id).send_mail(rec.order_id.id)

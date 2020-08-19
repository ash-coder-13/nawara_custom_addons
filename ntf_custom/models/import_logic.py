# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, date, timedelta


class ImportLogic(models.Model):
    _inherit = 'import.logic'

    def mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.demurrage and not i.saddad and i.bayan_no:
                exp_date_3 = fields.Date.from_string(i.demurrage) - timedelta(days=3)
                exp_date_2 = fields.Date.from_string(i.demurrage) - timedelta(days=2)
                exp_date_1 = fields.Date.from_string(i.demurrage) - timedelta(days=1)
                if date_now == exp_date_3 or date_now == exp_date_2 or date_now == exp_date_1:
                    mail_content = "Dear team,<br>Import (<strong>" + str(i.s_no) + "</strong>) demurrage date is <strong>" + str(i.demurrage) + "</strong>. Please clear this shipment as soon as possible to avoid the penalty.<br>Thanks &amp; Regards,<br>Odoo Reminder !"
                    main_content = {
                        'subject': _('Demurrage for customer %s ( Bayan No-%s) Will Expire On %s') % (i.customer.name, i.bayan_no, i.demurrage),
                        'body_html': mail_content,
                        'email_to': "rayan.babaqi@ntf-group.com",
                        'email_cc': "m.zaki@ntf-group.com,cs@ntf-group.com",
                    }
                    self.env['mail.mail'].create(main_content).send()


    def get_company_details(self):
        result = []
        partner = self.env['res.partner'].sudo().search([('name', '=', 'NAPCO TRADING COMPANY')], limit=1)
        if partner:
            logic_rec = self.sudo().search([('customer', '=', partner.id)])
            if logic_rec:
                for rec in logic_rec:
                    container_no = ''
                    container_type = ''
                    for ctnr in rec.import_id:
                        container_no += str(ctnr.crt_no) + ','
                        container_type += str(ctnr.types) + ','

                    sale_order = self.env['sale.order'].sudo().search([('sales_imp_id', '=', rec.id)], limit=1)
                    result.append({
                        "shipmentType": str(rec.ship_Type).upper() or "",
                        "shipperName": rec.shipper_name or "",
                        "consigneeName": partner.name,
                        "vslexparvlDate": rec.vsl_exp_arvl_date or "",
                        "vsldischlDate": rec.vsl_disch_date or "",
                        "docRecvByMailDate": rec.shipper_date or "",
                        "orgDocRecvgDate": rec.org_date or "",
                        "vesselArvlDate": rec.vessel_date or "",
                        "bLAwbNumber": rec.bill_no or "",
                        "houseBL": rec.house_bl or "",
                        "dischargingPort": rec.port.name or "",
                        "landingPort": rec.lan_Port.name or "",
                        "containerNumber": container_no,
                        "delOrderDate": rec.do_no or "",
                        "delOrderNumber": rec.do_num or "",
                        "bayanNumber": rec.bayan_no or "",
                        "bayanDate": rec.bayan_date or "",
                        "containerType": container_type,  # size field from line
                        "dutyPaidDate": rec.fin_bayan_date or "",
                        "transportNTFTerminal": "Yes" if sale_order.in_storage else "No",
                        "transportDirCustomer": "Yes" if sale_order.in_terminal else "No",
                        "demmurageDate": sale_order.demurrage if sale_order else "",  # sale
                        "lastDetentionDate": sale_order.detention if sale_order else "",  # sale
                        "eIRReturnToShipLine": sale_order.eir_date if sale_order else "",  # sale
                        "eventUpdateStatus": sale_order.sale_status.name if sale_order else "",  # sales status
                    })
                return result
            else:
                return {
                    'status': 'Failed',
                    'message': "Record you're searching for is not found in the system !"
                }
        else:
            return {
                'status': 'Failed',
                'message': "Record you're searching for is not found in the system !"
            }

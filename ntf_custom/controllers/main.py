# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


def get_company_details():
    return request.env['import.logic'].get_company_details()


class NapcoApi(http.Controller):

    @http.route('/dataset/getCompanyDetails', type='json', auth='public')
    def web_get_company_details(self, **kw):
        return get_company_details()


class NapcoTracking(http.Controller):

    @http.route('/napcotracking/<string:bill_no>', type='json', auth="public")
    def tracking(self, bill_no):
        # get the information using the SUPER USER
        result = []
        partner = request.env['res.partner'].sudo().search([('name', '=', 'NAPCO TRADING COMPANY')], limit=1)
        if partner:
            logic_rec = request.env['import.logic'].sudo().search([('customer', '=', partner.id),('bill_no','=',bill_no)])
            if logic_rec:
                for rec in logic_rec:
                    container_no = ''
                    container_type = ''
                    for ctnr in rec.import_id:
                        container_no += str(ctnr.crt_no) + ','
                        container_type += str(ctnr.types) + ','

                    sale_order = request.env['sale.order'].sudo().search([('sales_imp_id', '=', rec.id)], limit=1)
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
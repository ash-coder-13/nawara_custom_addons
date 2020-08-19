# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError
import time


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.report.partner.ledger"
    _description = "Account Partner Ledger"

    @api.onchange('result_selection')
    def onchange_result_selection(self):
        domain_account = []
        domain_partner = []
        if self.result_selection == 'customer':
            domain_account = [('internal_type', '=', 'receivable')]
            domain_partner = [('customer','=', '1')]
        if self.result_selection == 'supplier':
            domain_account = [('internal_type', '=', 'payable')]
            domain_partner = [('supplier', '=', '1')]
        if self.result_selection == 'customer_supplier':
            domain_account = [('internal_type', 'in', ('payable', 'receivable'))]
            domain_partner = ['|',('customer', '=', '1'),('supplier', '=', '1')]
        return {'domain': {'partner_account_id': domain_account, 'partner_id': domain_partner}}

    partner_account_id = fields.Many2one('account.account', string='Account', domain=[('internal_type','=', 'receivable')])
    partner_id = fields.Many2one('res.partner', string='Partner', domain=[('customer','=', '1')])

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency,
                             'partner_account_id': self.partner_account_id.id,
                             'partner_account_name': self.partner_account_id.name,
                             'partner_id': self.partner_id.id,
                             'partner_name': self.partner_id.name,
                             })
        return self.env['report'].get_action(self, 'account.report_partnerledger', data=data)


class ReportPartnerLedger(models.AbstractModel):
    _inherit = 'report.account.report_partnerledger'

    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        data['computed'] = {}
        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']
        if data['form']['partner_account_id']:
            data['computed']['account_ids'] = [data['form']['partner_account_id']]
        else:
            self.env.cr.execute("""
                    SELECT a.id
                    FROM account_account a
                    WHERE a.internal_type IN %s
                    AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
            data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        if not data['form']['partner_id']:
            params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
            reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
            query = """
                    SELECT DISTINCT "account_move_line".partner_id
                    FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
                    WHERE "account_move_line".partner_id IS NOT NULL
                        AND "account_move_line".account_id = account.id
                        AND am.id = "account_move_line".move_id
                        AND am.state IN %s
                        AND "account_move_line".account_id IN %s
                        AND NOT account.deprecated
                        AND """ + query_get_data[1] + reconcile_clause
            self.env.cr.execute(query, tuple(params))
            partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
        if data['form']['partner_id']:
            params = [data['form']['partner_id'], tuple(data['computed']['move_state']),
                      tuple(data['computed']['account_ids'])] + query_get_data[2]
            reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
            query = """
                                SELECT DISTINCT "account_move_line".partner_id
                                FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
                                WHERE "account_move_line".partner_id = %s
                                    AND "account_move_line".account_id = account.id
                                    AND am.id = "account_move_line".move_id
                                    AND am.state IN %s
                                    AND "account_move_line".account_id IN %s
                                    AND NOT account.deprecated
                                    AND """ + query_get_data[1] + reconcile_clause
            self.env.cr.execute(query, tuple(params))
            partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref, x.name))
        docargs = {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data,
            'docs': partners,
            'time': time,
            'lines': self._lines,
            'sum_partner': self._sum_partner,
        }
        return self.env['report'].render('account.report_partnerledger', docargs)
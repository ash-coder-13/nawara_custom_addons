#-*- coding:utf-8 -*-

from odoo import models, fields, api

class PartnerLedgerReport(models.AbstractModel):
    _name = 'report.genral_ledger.genral_ledger_report'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('genral_ledger.genral_ledger_report')
        active_wizard = self.env['genral.ledger'].search([])
        records = self.env['account.account'].browse(docids)
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['genral.ledger'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['genral.ledger'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form
        typed = record_wizard.entry_type
        account = record_wizard.account

        def opening(bal):
            if typed == "all":
                opend = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','=',bal.id)])

            if typed == "posted":
                opend = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','=',bal.id),('move_id.state','=',"posted")])

            debit = 0
            credit = 0
            opening = 0
            for x in opend:
                debit = debit + x.debit
                credit = credit + x.credit

            if bal.nature == 'debit':
                opening = debit - credit

            if bal.nature == 'credit':
                opening = credit - debit

            return opening
        
        if typed == "all":
            entries = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','=',account.id)])

        if typed == "posted":
            entries = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','=',account.id),('move_id.state','=',"posted")])
        

        users = self.env['res.users'].search([('id','=',self._uid)]) 

        acc_num = self.env['account.account'].search([('id','=',account.id)]) 




        docargs = {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': account,
            'data': data,
            'form': form,
            'to': to,
            'opening': opening,
            'entries': entries,
            'users': users,
            'acc_num': acc_num,
        }

        return report_obj.render('genral_ledger.genral_ledger_report', docargs)
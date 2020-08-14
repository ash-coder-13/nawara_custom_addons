# -*- coding: utf-8 -*-

from odoo import models, fields, api

class hr_ext_allowances_contract(models.Model):
	_name = 'ext.contract.allowances'

	
	ext_contract_id = fields.Many2one('hr.contract', string='ID')
	amount = fields.Float(string="Amount" , required=True)
	date = fields.Date(string="Date" , required=True)
	name = fields.Char(string="Allowance Type" , required=True)
	salary_rule_id = fields.Many2one('hr.salary.rule',string='Code' , required=True)
	status = fields.Selection([(
		'running', 'Running'),
		('expired', 'Expired'), ], string="Status", required=True)


class hr_ext_deductions_contract(models.Model):
	_name = 'ext.contract.deductions'

	
	ext_deduct_id = fields.Many2one('hr.contract', string='ID')
	amount = fields.Float(string="Amount" , required=True)
	date = fields.Date(string="Date" , required=True)
	name = fields.Char(string="Allowance Type" , required=True)
	salary_rule_id = fields.Many2one('hr.salary.rule',string='Code' , required=True)
	status = fields.Selection([(
		'running', 'Running'),
		('expired', 'Expired'), ], string="Status", required=True)
	
	
class hr_contract(models.Model):
	_inherit = 'hr.contract'

	ext_allowances_contract = fields.One2many('ext.contract.allowances', 'ext_contract_id', string='Contract ID')
	ext_deductions_contract = fields.One2many('ext.contract.deductions', 'ext_deduct_id', string='Ded Contract ID')

class hr_payslip(models.Model):
	_inherit = 'hr.payslip'

	@api.multi
	def compute_sheet(self):
		res = super(hr_payslip, self).compute_sheet()
		for record in self:
			if record.contract_id.ext_deductions_contract:
				for line in record.contract_id.ext_deductions_contract:
					amount = (line.amount)*-1
					if line.status == 'running':
						record.create_salary_line(line, amount)
						for rec in record.line_ids.search([('code','=','NET')]):
							rec.amount -= line.amount
			if record.contract_id.ext_allowances_contract:
				for item in record.contract_id.ext_allowances_contract:
					if item.status == 'running':
						record.create_salary_line(item, item.amount)
						for rec in record.line_ids.search([('code','=','NET')]):
							rec.amount += item.amount


		return res

	def create_salary_line(self, line, amount):
		SalaryComputation = self.line_ids.create({
			'name':line.name,
			'code':line.salary_rule_id.code,
			'category_id':line.salary_rule_id.category_id.id,
			'rate':100,
			'salary_rule_id':line.salary_rule_id.id,
			'amount':amount,
			'slip_id':self.id,
			'employee_id':self.employee_id.id,
			'contract_id':self.contract_id.id,
			})
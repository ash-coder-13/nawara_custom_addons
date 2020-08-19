import os
import xlsxwriter
from dateutil.relativedelta import relativedelta
import datetime
import time
from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64
from num2words import num2words
import time
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class XlsxReportHeadOfficeAssesBAl(models.TransientModel):
	_name = 'assets.bal'

	date = fields.Date(default=date.today(), string="Report Date")
	name = fields.Char()
	file = fields.Binary('Download Report', )
	category = fields.Many2many('account.asset.category', string="Categories")
	assets = fields.Many2many('account.asset.asset', string="Assets")
	filters = fields.Selection([
		('cat', 'Category Wise'),
		('asset', 'Assest Wise')], string='Filter', required=True)
	cat_type = fields.Selection([
		('all', 'All'),
		('specfic', 'Specific')], string='Category Filter')
	assest_type = fields.Selection([
		('all', 'All'),
		('specfic', 'Specific')], string='Assets Filter')

	@api.onchange('filters')
	def select_one1(self):
		if self.filters == 'cat':
			self.assest_type = False
			self.assets = False
		if self.filters == 'asset':
			self.cat_type = False
			self.category = False

	@api.multi
	def print_report(self):
		lisst = []
		if self.filters == 'cat' and self.cat_type == 'all':
			lisst = self.env['account.asset.category'].search([])
		if self.filters == 'cat' and self.cat_type == 'specfic':
			for x in self.category:
				lisst.append(x)
		if self.filters == 'asset' and self.assest_type == 'all':
			asset = self.env['account.asset.asset'].search([])
			for x in asset:
				if x.category_id not in lisst:
					lisst.append(x.category_id)
		if self.filters == 'asset' and self.assest_type == 'specfic':
			for x in self.assets:
				if x.category_id not in lisst:
					lisst.append(x.category_id)
			
		self.xlsx_report(lisst)

	@api.multi
	def xlsx_report(self, input_records):
		with xlsxwriter.Workbook(config['data_dir'] + "/fixed_assets_balance_report.xlsx") as workbook:
			main_heading = workbook.add_format({
				"bold": 1,
				"border": 1,
				"align": 'center',
				"valign": 'vcenter',
				"font_color": 'white',
				"bg_color": '548235',
				'font_size': '10',
			})

			# Create a format to use in the merged range.
			merge_format = workbook.add_format({
				'bold': 1,
				'border': 1,
				'align': 'center',
				'valign': 'vcenter',
				'font_size': '16',
				"font_color": 'white',
				'fg_color': '7030a0'})

			main_data = workbook.add_format({
				"align": 'center',
				"valign": 'vcenter',
				'font_size': '8',
			})
			merge_format.set_shrink()
			main_heading.set_text_justlast(1)
			main_data.set_border()
			worksheet = workbook.add_worksheet('Fixed Assets Balance Report')
			head = "Fixed Assets Balance Report"

			for row in range(1, 1):
				worksheet.set_row(row, 9)
			worksheet.merge_range('A1:I1', head, merge_format)

			worksheet.write('A2', 'Type', main_heading)
			worksheet.write('B2', 'type', main_data)
			worksheet.write('H2', 'Report Date:', main_heading)
			worksheet.write('I2', str(self.date), main_data)

			worksheet.set_column('B:B', 35)
			worksheet.set_column('A:A', 25)
			worksheet.set_column('C:I', 18)
			worksheet.write('A4', 'Category', main_heading)
			worksheet.write('B4', 'Asset', main_heading)
			worksheet.write('C4', 'Reference', main_heading)
			worksheet.write('D4', 'Gross Value', main_heading)
			worksheet.write('E4', 'Salvage Value', main_heading)
			worksheet.write('F4', 'Residual Value', main_heading)
			worksheet.write('G4', 'Accumulated Value', main_heading)
			worksheet.write('H4', 'Depreciation', main_heading)
			worksheet.write('I4', 'Residual', main_heading)
			# worksheet.write('J4', 'Uom', main_heading)
			# worksheet.write('K4', 'Cost', main_heading)
			# worksheet.write('L4', 'Selling Price', main_heading)
			# worksheet.write('M4', 'Quantity in Hand', main_heading)

			row = 5
			col = 0

			records = input_records

			for line in records:

				worksheet.write_string(row, col, str(line.name), main_heading)

				row = row + 1
				col = 0

				asset_id = self.env['account.asset.asset'].search(
					[('category_id.id', '=', line.id)])

				sr = 1
				for y in asset_id:

					amt = 0
					remain = 0
					for z in y.depreciation_line_ids:
						if z.depreciation_date:
							if str(z.depreciation_date[:7]) == str(self.date[:7]):
								amt = z.depreciated_value
								remain = z.remaining_value


					worksheet.write_string(row, col + 1, str(y.name), main_heading)
					worksheet.write_string(row, col + 2, str(y.code), main_data)
					worksheet.write_string(row, col + 3, str(y.value), main_data)
					worksheet.write_string(row, col + 4, str(y.salvage_value), main_data)
					worksheet.write_string(row, col + 5, str(y.value_residual), main_data)
					worksheet.write_string(row, col + 6, str(y.acc_dep), main_data)
					worksheet.write_string(row, col + 7, str(amt), main_data)
					worksheet.write_string(row, col + 8, str(remain), main_data)

					row += 1

	def get_report(self):
		self.print_report()
		data_file = open(config['data_dir'] + "/fixed_assets_balance_report.xlsx", "rb")
		out = data_file.read()
		data_file.close()
		self.name = 'Fixed Assets Balance Report.xlsx'
		self.file = base64.b64encode(out)
		return {
			"type": "ir.actions.do_nothing",
		}

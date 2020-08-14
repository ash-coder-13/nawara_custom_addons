# -*- coding: utf-8 -*-
from odoo import http

# class NawaraContract(http.Controller):
#     @http.route('/nawara_contract/nawara_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nawara_contract/nawara_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nawara_contract.listing', {
#             'root': '/nawara_contract/nawara_contract',
#             'objects': http.request.env['nawara_contract.nawara_contract'].search([]),
#         })

#     @http.route('/nawara_contract/nawara_contract/objects/<model("nawara_contract.nawara_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nawara_contract.object', {
#             'object': obj
#         })
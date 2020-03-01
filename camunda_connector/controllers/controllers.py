# -*- coding: utf-8 -*-
from odoo import http

# class CamundaConnector(http.Controller):
#     @http.route('/camunda_connector/camunda_connector/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/camunda_connector/camunda_connector/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('camunda_connector.listing', {
#             'root': '/camunda_connector/camunda_connector',
#             'objects': http.request.env['camunda_connector.camunda_connector'].search([]),
#         })

#     @http.route('/camunda_connector/camunda_connector/objects/<model("camunda_connector.camunda_connector"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('camunda_connector.object', {
#             'object': obj
#         })

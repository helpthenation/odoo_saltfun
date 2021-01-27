# -*- coding: utf-8 -*-
# from odoo import http


# class MbModule(http.Controller):
#     @http.route('/mb_module/mb_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mb_module/mb_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mb_module.listing', {
#             'root': '/mb_module/mb_module',
#             'objects': http.request.env['mb_module.mb_module'].search([]),
#         })

#     @http.route('/mb_module/mb_module/objects/<model("mb_module.mb_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mb_module.object', {
#             'object': obj
#         })

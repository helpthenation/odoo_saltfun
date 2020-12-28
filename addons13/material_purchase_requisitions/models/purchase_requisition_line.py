# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaterialPurchaseRequisitionLine(models.Model):
    _name = "material.purchase.requisition.line"

    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    #     layout_category_id = fields.Many2one(
    #         'sale.layout_category',
    #         string='Section',
    #     )

    partner_id = fields.Many2one(
        'res.partner',
        string='Vendors', domain="[('supplier', '=', True)]"
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    qty = fields.Float(
        string='Quantity',
        required=True,
        readonly=True,
    )
    uom = fields.Many2one(
        'product.uom',  # product.uom in odoo11
        string='Unit of Measure',
        required=True,
    )

    # requisition_type = fields.Selection(
    #     selection=[
    #         ('internal', 'Internal Picking'),
    #         ('purchase', 'Purchase Order'),
    #     ],
    #     string='Requisition Action',
    #     # default='purchase',
    #     required=True,
    # )

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

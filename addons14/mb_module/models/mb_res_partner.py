from odoo import fields, models, api


class MbResPartner(models.Model):

    _inherit = 'res.partner'
    _description = 'Description'

    vat = fields.Char(string='ICE', index=True)

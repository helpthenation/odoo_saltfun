from odoo import fields, models


class MbRefused(models.Model):
    _name = 'mb.refused'
    _inherit = 'purchase.order'
    _description = 'Description'

    partner_id = fields.Many2one('purchase.order', String="Partner_id", required=False)
    expensive = fields.Boolean(string="Trop cher")
    improper = fields.Boolean(string="Non conforme")
    other = fields.Boolean(string="Autre")
    refused_note = fields.Text(string="Remarques")

    def mb_refused(self):
        self.env['purchase.order'].search([('id', '=', self.env.context.get('active_id', []))]).state = 'done'

    def mb_validate(self):
        print("-------------------------------------------------------------------------")

from odoo import fields, models, api


class MbBDCFournisseur(models.Model):
    _name = 'mb.bdcfournisseur'
    _inherit = 'purchase.order'
    _description = 'Description'

    partner_id = fields.Many2one('purchase.order', String="Partner_id", required=False)
    gd_validation = fields.Many2one('hr.employee', string="Directeur Général", required=True)
    gd_validation_validate = fields.Boolean(string="Validée")
    gd_validation_bloc = fields.Boolean(string="Bloqué")
    gd_validation_note = fields.Text(string="Remarques")

    def bdc_fournisseur_validatte(self):
        self.env['purchase.order'].search([('id', '=', self.env.context.get('active_id', []))]).state = 'purchase'

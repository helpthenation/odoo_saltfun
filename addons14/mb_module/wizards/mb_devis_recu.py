from odoo import fields, models, api


class MbDevisRecu(models.Model):
    _name = 'mb.devisrecu'
    _inherit = 'purchase.order'
    _description = 'Description'

    partner_id = fields.Many2one('purchase.order', String="Partner_id", required=False)
    devi_recu_note = fields.Text(string="Remarques", required=False)
    file = fields.Binary("Télécharger votre fichier", required=True)
    file_name = fields.Char('Devis Reçu')
    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, ondelete='cascade')

    def devi_recu(self):
        self.env['purchase.order'].search([('id', '=', self.env.context.get('active_id', []))]).state = 'to approve'

    def button_done(self):
        self.write({'state': 'cancel', 'priority': '0'})

    def get_data_quotation(self):
        print(self.env['purchase.order'].search([('id', '=', self.env.context.get('active_id', []))]))
        pv_validation_data = self.env['mb.devisrecu'].search([('order_id', '=', self.order_id)])
        print(pv_validation_data)
        return True

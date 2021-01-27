from odoo import fields, models, api


class MbDevisRecu(models.TransientModel):
    _name = 'mb.devisrecu'
    _description = 'Description'

    note = fields.Text(string="Note")
    file = fields.Binary("Devis Reçu")
    file_name = fields.Char('Devis Reçu')

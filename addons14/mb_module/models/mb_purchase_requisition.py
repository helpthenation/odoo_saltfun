from odoo import fields, models


class MbPurchase(models.Model):
    _inherit = 'purchase.requisition'

    business_unit = fields.Many2one('hr.department', string='Business Unit Concernée', required=True)
    applicant = fields.Many2one('res.users', string='Demandeur', required=True)

    state = fields.Selection(selection_add=[
        ('to approve', 'Controle de Gestion'),
        ('sign','BDC à signer'),
        ('signed', 'BDC Fournisseur')
    ],
        string='Status', tracking=True, required=True,
        copy=False, default='draft',ondelete={'to approve': 'cascade','sign':'cascade','signed':'cascade'})

    state_blanket_order = fields.Selection(selection_add=[
        ('to approve', 'Controle de Gestion'),
        ('sign', 'BDC à signer'),
        ('signed', 'BDC Fournisseur')
    ], compute='_set_state')
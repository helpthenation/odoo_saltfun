from odoo import fields, models


class MbPurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    business_unit = fields.Many2one(related='requisition_id.business_unit', string='Business Unit Concernée')
    applicant = fields.Many2one('res.users', related='requisition_id.applicant', string='Demandeur')

    state = fields.Selection(selection_add=[
        ('to approve', 'Devis reçus'),
        ('purchase', 'BDC Fournisseur'),
        ('done', 'Refusé')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def button_approve(self):
        for rec in self:
            rec.state = 'purchase'

    def button_confirm(self):
        for rec in self:
            rec.state = 'to approve'

    def button_done_mb(self):
        for rec in self:
            rec.state = 'done'

    def button_done(self):
        self.write({'state': 'cancel', 'priority': '0'})



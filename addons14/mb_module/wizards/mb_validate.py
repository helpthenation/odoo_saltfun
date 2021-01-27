from odoo import fields, models


class MbRequisition(models.Model):
    _name = 'mb.validate'
    _inherit = 'purchase.requisition'
    _description = 'Description'

    partner_id = fields.Many2one('purchase.requisition', String="Partner_id", required=False)
    business_unit = fields.Many2one('hr.department', string='Business Unit Concernée', required=False, default=5)
    applicant = fields.Many2one('res.users', string='Demandeur', required=False, default=5)

    def mb_validate(self):
        self.env['purchase.requisition'].search(
            [('id', '=', self.env.context.get('params').get('id'))]).state = 'to approve'

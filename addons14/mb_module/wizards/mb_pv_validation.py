from odoo import fields, models, api


class MbPvValidation(models.Model):
    _name = 'mb.pvvalidation'
    _inherit = 'purchase.requisition'
    _description = 'Description'

    business_unit = fields.Many2one('hr.department', string='Business Unit Concernée', default=1)
    applicant = fields.Many2one('res.users', string='Demandeur', default=1)

    partner_id = fields.Many2one('purchase.requisition', String="Partner_id", required=False)
    management_control = fields.Many2one('res.users', string="Contrôle de gestion", domain=lambda self: [("groups_id", "=", self.env.ref("mb_module.mb_control").id)])
    management_control_notes = fields.Text(string="Remarques")
    management_control_validate = fields.Boolean(string="Validée")
    management_control_bloc = fields.Boolean(string="Bloqué")
    order_id = fields.Many2one('purchase.requisition', string='Order Reference', index=True, ondelete='cascade')
    purchase_ids = fields.One2many('purchase.order', 'requisition_id', string='Purchase Orders',
                                   states={'done': [('readonly', True)]})

    def pv_validate(self):
        if  self.management_control_validate is True:
            self.env['purchase.requisition'].search([('id', '=', self.env.context.get('active_id', []))]).state = 'sign'
        elif self.management_control_bloc is True:
            self.env['purchase.requisition'].search([('id', '=', self.env.context.get('active_id', []))]).state = 'cancel'
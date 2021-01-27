from odoo import fields, models, api


class MbBdcSignature(models.Model):

    _name = 'mb.bdcsignature'
    _inherit = 'purchase.requisition'
    _description = 'Description'

    partner_id = fields.Many2one('purchase.order', String="Partner_id", required=False)
    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, ondelete='cascade')
    business_unit = fields.Many2one('hr.department', string='Business Unit Concernée', required=False, default=5)
    applicant = fields.Many2one('res.users', string='Demandeur',  required=False, default=5)
    signature = fields.Char(String="Signature", required=True)

    def bdc_signed(self):
        print("--------------------------------------------------------------------------------------------------")
        self.env['purchase.requisition'].search([('id', '=', self.env.context.get('active_id', []))]).state = 'signed'








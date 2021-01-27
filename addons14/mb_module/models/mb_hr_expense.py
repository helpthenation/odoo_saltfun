from odoo import fields, models, api


class MbAccount(models.Model):

    _inherit = 'hr.expense'

    business_unit = fields.Many2one('hr.department', string='Business Unit Concernée', required=True)
    applicant = fields.Many2one('hr.employee', string='Demandeur', required=True)


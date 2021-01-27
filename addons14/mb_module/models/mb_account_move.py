from odoo import api, fields, models


class MbAccount(models.Model):

    _inherit = 'account.move'

    business_unit = fields.Many2one('hr.department', string='Business Unit Concernée', required=True)
    applicant = fields.Many2one('hr.employee', string='Demandeur', required=True)


# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class PartnerExternalId(models.Model):
    _inherit = 'res.partner'

    remote_id = fields.Integer('Client identifier')

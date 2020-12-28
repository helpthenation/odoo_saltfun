# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import base64

from odoo import fields, models, api
import json
import shutil
import requests
from odoo.exceptions import ValidationError
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    remote_db = fields.Char('Instance')
    remote_url = fields.Char('Server')
    remote_user = fields.Char('Username')
    remote_pass = fields.Char('Password')
    remote_company_id = fields.Integer('Company Id')
    remote_product_name = fields.Char('Product name')

    from_chain_product_id = fields.Integer('From chain Product_id')

    last_connection_date = fields.Date('Last connection date')


    def reset_remote_id(self):
        partners = self.env['res.partner'].sudo().search([])
        for partner in partners:
            partner.remote_id = False
        for record in self:
            record.partner_id.remote_id = False


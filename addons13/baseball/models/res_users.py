# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import ValidationError
from datetime import datetime


class Res_users(models.Model):
    _inherit = 'res.users'

    current_partner_id = fields.Many2one('res.partner', string="Current partner", default=lambda self: self.partner_id)
    child_partner_ids = fields.One2many(related="partner_id.child_partner_ids", string="Child partners")
    # child_partner_ids = fields.One2many('res.partner', 'parent_user_id', string="Child partners")

    def set_current_partner(self, partner_id):
        for rec in self:
            rec.current_partner_id = partner_id

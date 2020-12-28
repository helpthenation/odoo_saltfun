# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import ValidationError
from datetime import datetime


class Club(models.Model):
    _inherit = 'res.company'

    def get_current_season(self):
        # FIXME Make it installable
        return False
        return self.env['baseball.season'].get_current_season()

    current_season_id = fields.Many2one('baseball.season', string="Current season", default=get_current_season)

class Roles(models.Model):
    _name = 'baseball.roles'
    _order = 'sequence' 

    name = fields.Char(string="Title", required=True, translate=True)
    sequence = fields.Integer('Sequence')
    published = fields.Boolean('Published on website')
    address_website = fields.Boolean('Address on website')
    description = fields.Html()
    partner_ids = fields.Many2many('res.partner', string="Members")

    @api.model
    def update_role_as_follower(self, vals):
        member_ids = self.env['res.partner'].search([])
        channel = self.env.ref('baseball.channel_registration')
        member_ids.message_unsubscribe()
        member_ids.message_subscribe(channel_ids=channel.ids)

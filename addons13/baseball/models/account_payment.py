# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import ValidationError
from datetime import datetime


class Payment(models.Model):
    _inherit = 'account.payment'

    membership_id = fields.Many2one('baseball.registration', string="Membership")

# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import ValidationError
from datetime import datetime

class Tab(models.Model):
    _name = 'baseball.tab'
    _order = 'date desc'

    member_id = fields.Many2one("res.partner", string="Member")
    to_pay = fields.Float(string="To pay",)
    paid = fields.Float(string="Paid")
    date = fields.Date(string="Date", required=True, default= lambda self: fields.Date.today())
    comment = fields.Char(string="Comment")

   
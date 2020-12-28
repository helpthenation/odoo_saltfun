# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import uuid
import pytz

import logging
_logger = logging.getLogger(__name__)


class Event(models.Model):
    _name = 'baseball.event'
    _order = "start_time"


    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    start_time = fields.Datetime(string="Start Time", required=True)
    end_time = fields.Datetime(string="End Time", required=True)
    venue_id = fields.Many2one('baseball.venue', string="Venue", required=True)

    @api.constrains('start_time', 'end_time')
    def _check_dates(self):
        for rec in self:
            if rec.start_time >= rec.end_time:
                raise ValidationError("Start Time must be before end time")
# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import ValidationError
from datetime import datetime


class Season(models.Model):
    _name = 'baseball.season'
    _order = 'sequence, id desc'

    @api.model
    def default_get(self, default_fields):
        res = super(Season, self).default_get(default_fields)
        res['fee_ids'] = [(0,0, {'fee': fee_id.fee, 'category_id': fee_id.category_id.id}) for fee_id in self.get_current_season().fee_ids]
        res['registration_description'] = self.get_current_season().registration_description
        return res

    name = fields.Char('Year', required=True)
    members_qty = fields.Integer('Members quantity', compute='_compute_members_qty')
    amount_left_to_collect = fields.Float('Amount to get', compute='_compute_to_collect')
    is_current = fields.Boolean('Current')
    certificate_id = fields.Many2one(
        'ir.attachment',
        'Certificate',
    )
    sequence = fields.Integer(string='Sequence')
    fee_ids = fields.One2many('baseball.fee', 'season_id', string='Fees')
    registration_description = fields.Html(string='Registration description', translate=True)


    @api.constrains('is_current')
    def _check_current(self):
        if len(self.search([('is_current','=', True)]))> 1:
            raise ValidationError("Only one current season")

    @api.constrains('name')
    def _check_name(self):
        if len(self.search([('name','=', self.name)]))> 1:
            raise ValidationError("Field year must be unique")

    def _compute_members_qty(self):
        for rec in self:
            members_current_season = rec.env['res.partner'].search([]).filtered(lambda r: rec.id in r.season_ids.mapped('season_id').ids )
            rec.members_qty = len(members_current_season)

    def _compute_to_collect(self):
        for rec in self:
            registration_ids = rec.env['baseball.registration'].search([
                ('season_id','=',rec.id),
                ('member_id','!=',False),
                ])
            registration_ids = registration_ids.filtered(lambda r: r.fee_to_pay > r.fee_paid)
            rec.amount_left_to_collect = sum(registration_ids.mapped(lambda r: r.fee_to_pay - r.fee_paid))

    def set_as_current(self):
        self.ensure_one()
        old_season = self.search([('is_current', '=', True)])
        old_season.is_current = False
        self.is_current = True
        self.env['res.company'].search([]).write({'current_season_id': self.id})

    @api.model
    def get_current_season(self):
        return self.search([('is_current','=',True)])

    @api.model
    def make_or_create_current_season(self):
        if self.get_current_season():
            return
        current_id = self.search([], order="name DESC", limit=1)
        if current_id:
            current_id.is_current = True
        else:
            current_id = self.create({
                'name': str(datetime.today().year),
                'is_current': True,
                })


class Fee(models.Model):
    _name = 'baseball.fee'

    fee = fields.Float(string="Fee")
    season_id = fields.Many2one("baseball.season", string="Season")
    category_id = fields.Many2one("baseball.categories", string="Category")

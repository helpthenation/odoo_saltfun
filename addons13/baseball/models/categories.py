# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import ValidationError
from datetime import datetime


class Categories(models.Model):
    _name = 'baseball.categories'
    _order = 'sequence'

    name = fields.Char(string="Name", required=True)

    players_ids = fields.Many2many(
        'res.partner', string="Players", compute='_players_in_teams')
    description = fields.Html()
    teams_ids = fields.Many2many('baseball.teams', string="Teams")
    cotisation = fields.Float(string="Fee", compute='_compute_fee', inverse='_set_fee')
    start_date = fields.Integer(string="Beginning (year)")
    end_date = fields.Integer(string="End (year)")
    active = fields.Boolean(default=True)
    game_ids = fields.Many2many(
        'baseball.game', string="Games", compute="_compute_games")
    sequence = fields.Integer(string='Sequence')
    published = fields.Boolean('Published', default=True)

    @api.depends('teams_ids')
    def _players_in_teams(self):
        for rec in self:
            rec.players_ids = rec.teams_ids.players_ids

    def _set_fee(self):
        for rec in self:
            cotisation_id = self.env['baseball.fee'].search([('category_id','=',self.id),('season_id', '=', self.env['res.users'].browse(self._uid).company_id.current_season_id.id)])
            if cotisation_id:
                cotisation_id.fee =  rec.cotisation
            else:
                self.env['baseball.fee'].create({
                    'fee': rec.cotisation,
                    'season_id': self.env['res.users'].browse(self._uid).company_id.current_season_id.id,
                    'category_id': rec.id,
                    })

    def _compute_fee(self):
        for rec in self:
            cotisation_id = self.env['baseball.fee'].search([('category_id','=',rec.id),('season_id', '=', self.env['baseball.season'].get_current_season().id)])
            if cotisation_id:
                rec.cotisation = cotisation_id.fee
            else:
                rec.cotisation = 0

    def _compute_games(self):
        for rec in self:
            rec.game_ids = rec.teams_ids.game_ids.sorted(key=lambda r: r.start_time)

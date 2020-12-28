# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools, _
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import dateutil
import math
import pytz


class Teams(models.Model):
    _name = 'baseball.teams'
    _order = 'sequence'
    
    name = fields.Char(string="Name", required=True)
    name_from_federation = fields.Many2many('baseball.teams.dbname', string="Name on federation website", required=True)

    players_ids = fields.Many2many(
        'res.partner', string="Players", compute='_players_in_team')
    coaches_ids = fields.Many2many(
        'res.partner', string="Coaches", relation="team_coaches")
    responsible_ids = fields.Many2many(
        'res.partner', string="Manager", relation="team_responsibles")
    image = fields.Binary('Image')
    photo = fields.Binary('Photo')
    game_ids = fields.Many2many(
        'baseball.game', string="Games", compute="_compute_games")
    category_ids = fields.Many2many('baseball.categories', string="Categories")

    division_ids = fields.Many2many(
        'baseball.divisions', string="Divisions")
    is_official_umpires = fields.Boolean(
        default=False, string="Official Umpires")
    is_official_scorers = fields.Boolean(
        default=False, string="Official Scorers")
    is_opponent = fields.Boolean(default=False, string='Opponent')
    active = fields.Boolean(default=True)
    multiple_teams = fields.Boolean(default=False)
    subteams_ids = fields.Many2one('baseball.teams', string="Multiple teams")
    db_name = fields.Char(string="Database name")
    description = fields.Html()
    venue = fields.Many2one('baseball.venue', string="Venue")
    logo_id = fields.Many2one('baseball.logo', string="Logo")
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer(string='Color')
    practices_ids = fields.Many2many(
        'baseball.teams.practice', string="Weekly Practices", relation="team_practices_rel")
    practice_event_ids = fields.One2many(
        'baseball.teams.practice.event',
        'team_id',
        string='Practices',)
    published = fields.Boolean('Published', default=True)
    send_game_invitation = fields.Boolean(
        default=True, string="Send game invitation")

    @api.depends('division_ids', 'name')
    def name_get(self):
        result = []
        for team in self:
            if team.division_ids:
                division = team.division_ids.filtered(lambda r: not r.parent_related_division_ids)
                division = division and division[0]
                result.append(
                    (team.id, '%s (%s)' % (team.name, division.name)))
            else:
                result.append(
                    (team.id, '%s' % (team.name)))
  
        return result


    def _players_in_team(self):
        for rec in self:
            rec.players_ids = rec.env['res.partner'].search([('team_ids','in',rec.id)]).filtered(lambda r: r.is_active_current_season and r.is_player)

    def _compute_games(self):
        for rec in self:
            rec.game_ids = rec.env['baseball.game'].search(['|', ('home_team','=',rec.id),('away_team','=',rec.id), ('period', '=', 'current')]).sorted(key=lambda r: r.start_time)

class Divisions(models.Model):
    _name = 'baseball.divisions'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    description = fields.Html()
    team_ids = fields.Many2many('baseball.teams', string="Teams")
    average_duration = fields.Float(string="Average length")
    standings_ids = fields.Many2many('baseball.standings', string="Teams", compute="_compute_order_standing")
    parent_related_division_ids = fields.Many2many(
        comodel_name='baseball.divisions',
        column1="parent",
        column2="child", 
        relation="related_divisions", 
        string="Parent divisions")
    child_related_division_ids = fields.Many2many(
        comodel_name='baseball.divisions',
        column1="child",
        column2="parent", 
        relation="related_divisions", 
        string="Child divisions")

    def _compute_order_standing(self):
        for rec in self:
            standings = rec.env['baseball.standings']
            for team in rec.team_ids:
                standings += rec.env['baseball.standings'].create({'team_id':team.id, 'division_id':rec.id,})
            rec.standings_ids=  standings.sorted(key=lambda r: r.result_average, reverse=True)

class Standings(models.TransientModel):
    _name = 'baseball.standings'

    team_id = fields.Many2one('baseball.teams', string="Team")
    division_id = fields.Many2one('baseball.divisions', string="Division")
    is_opponent = fields.Boolean(string='Opponent', related="team_id.is_opponent")

    result_games = fields.Float(string="G", compute="_compute_standing", digits=(4,0))
    result_wins = fields.Float(string="W", compute="_compute_standing", digits=(4,0))
    result_losses = fields.Float(string="L", compute="_compute_standing", digits=(4,0))
    result_ties = fields.Float(string="T", compute="_compute_standing", digits=(4,0))
    result_not_played = fields.Float(string="NP", compute="_compute_standing", digits=(4,0))
    result_forfeits = fields.Float(string="FF", compute="_compute_standing", digits=(4,0))
    result_average = fields.Float(string="AVG", compute="_compute_standing", digits=(4,3))


    def _compute_standing(self):
        for rec in self:
            if rec.division_id.parent_related_division_ids:
                game_ids = rec.team_id.game_ids.filtered(lambda r: (r.score_home or r.score_away) and (r.division.id == rec.division_id.id or r.division.id in rec.division_id.parent_related_division_ids.ids))
            else:
                game_ids = rec.team_id.game_ids.filtered(lambda r: (r.score_home or r.score_away) and r.division.id == rec.division_id.id)
            game_played = game_ids.filtered(lambda r: r.score_home.isdigit() and  r.score_away.isdigit())
            game_forfeited = game_ids.filtered(lambda r:  'ff' in r.score_home.lower() or 'ff' in r.score_away.lower())

            rec.result_not_played = len(game_ids.filtered(lambda r: r.score_home == 'NP' and r.score_away == 'NP'))
            rec.result_games = len(game_ids) - rec.result_not_played
            rec.result_wins = len(game_played.filtered(lambda r: ( (int(r.score_home) > int(r.score_away)) and r.home_team==rec.team_id ) or ( (int(r.score_home) < int(r.score_away)) and r.away_team==rec.team_id)) ) + len(game_ids.filtered(lambda r:  ('ff' in r.score_home.lower() and r.away_team==rec.team_id) or ('ff' in r.score_away.lower() and r.home_team==rec.team_id)) )
            rec.result_losses = len(game_played.filtered(lambda r: ( (int(r.score_home) < int(r.score_away)) and r.home_team==rec.team_id) or ((int(r.score_home) > int(r.score_away)) and r.away_team==rec.team_id)) )
            rec.result_ties = len(game_played.filtered(lambda r: int(r.score_home) == int(r.score_away)) )
            rec.result_forfeits = len(game_ids.filtered(lambda r:  ('ff' in r.score_home.lower() and r.home_team==rec.team_id) or ('ff' in r.score_away.lower() and r.away_team==rec.team_id)) )

            rec.result_average = rec.result_wins/rec.result_games if rec.result_games else 0

class Teams_dbname(models.Model):
    _name = 'baseball.teams.dbname'
    
    name = fields.Char(string="Name", required=True)

class Logos(models.Model):
    _name = 'baseball.logo'

    name = fields.Char(string="Name", required=True)
    image = fields.Binary('Image')

class Practices(models.Model):
    _name = 'baseball.teams.practice'
    _order = "dayofweek, hour_from"

    dayofweek = fields.Selection([
        ('0','Monday'),
        ('1','Tuesday'),
        ('2','Wednesday'),
        ('3','Thursday'),
        ('4','Friday'),
        ('5','Saturday'),
        ('6','Sunday'),
        ], 'Day of Week', required=True)
    hour_from = fields.Float("Start")
    hour_to = fields.Float("End")
    team_ids = fields.Many2many(
        'baseball.teams', string="Teams", relation="team_practices_rel", domain="[('is_opponent','=',False)]")
    season = fields.Selection([('summer','Summer'),('winter','Winter')], string='Period', default='summer')
    venue_id = fields.Many2one('baseball.venue', string="Venue")
    practice_event_ids = fields.One2many(
        'baseball.teams.practice.event', 'practice_id', string="Practices")
    season_id = fields.Many2one('baseball.season', string='Season', default=lambda self: self.env['baseball.season'].sudo().get_current_season())
    period = fields.Selection([
        ('past', "Past seasons"),
        ('current', "Current seasn"),
    ], compute='_get_current', search='_search_period')

    @api.depends('season_id')
    def _get_current(self):
        for rec in self:
            if rec.season_id == rec.env['baseball.season'].sudo().get_current_season():
                rec.period = 'current'
            else:
                rec.period = 'past'

    def _search_period(self, operator, value):
        season_id = self.env['baseball.season'].sudo().get_current_season()
        if value == 'current' and operator == '=':
            games = self.search([('season_id','=', season_id.id)])
        else:
            games = self.search([('season_id','!=', season_id.id)])
        return [('id', 'in', games.ids)]

    def unlink(self):
        for rec in self:
            if rec.mapped('practice_event_ids.drill_ids') or rec.mapped('practice_event_ids.present_players_ids'):
                raise UserError(_('You cannot delete practice event with already saved drills or players presences counted.'))
        return super(Practices, self).unlink()

class Practices_serie(models.Model):
    _name = 'baseball.teams.practice.serie'

    practice_event_ids = fields.One2many(
        'baseball.teams.practice.event', 'serie_id', string="Practices")


class Practices_event(models.Model):
    _name = 'baseball.teams.practice.event'
    _order = "start_time, team_id"
    _rec_name = "start_time"

    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")
    team_id = fields.Many2one('baseball.teams', string="Team", domain="[('is_opponent','=',False)]")
    venue_id = fields.Many2one('baseball.venue', string="Venue")
    serie_id = fields.Many2one('baseball.teams.practice.serie', string="Serie", ondelete="cascade")
    practice_id = fields.Many2one('baseball.teams.practice', string="Practice", ondelete="cascade")
    season_id = fields.Many2one('baseball.season', string='Season', related='practice_id.season_id', store=True)
    drill_ids = fields.One2many('baseball.practice.drill', 'practice_id', string='Drills')
    period = fields.Selection([
        ('past', "Past seasons"),
        ('current', "Current seasn"),
    ], compute='_get_current', search='_search_period')
    present_players_ids = fields.Many2many(
        'res.partner', string="Attendees", relation="practice_attend")
    absent_players_ids = fields.Many2many(
        'res.partner', string="Absentees", relation="practice_absent")
    duration = fields.Float(string="Duration", compute="_get_duration", store=True)
    section_ids = fields.One2many(
        'baseball.practice.section', 'practice_id', string="Sections")


    @api.depends('start_time', 'team_id.name', 'venue_id.name')
    def name_get(self):
        result = []
        for rec in self:
            date = fields.Date.to_string(fields.Datetime.from_string(rec.start_time))
            result.append(
                (rec.id, '%s (%s @ %s)' % (date, rec.team_id.name, rec.venue_id.name)))
        return result

    @api.depends('season_id')
    def _get_current(self):
        for rec in self:
            if rec.season_id == rec.env['baseball.season'].sudo().get_current_season():
                rec.period = 'current'
            else:
                rec.period = 'past'

    def _search_period(self, operator, value):
        season_id = self.env['baseball.season'].sudo().get_current_season()
        if value == 'current' and operator == '=':
            games = self.search([('season_id','=', season_id.id)])
        else:
            games = self.search([('season_id','!=', season_id.id)])
        return [('id', 'in', games.ids)]

    @api.depends('drill_ids.duration')
    def _get_duration(self):
        for rec in self:
            rec.duration = sum(rec.mapped('drill_ids.duration'))

    def save_as_template(self):
        section_mapping = {}
        for section_id in self.section_ids:
            section_mapping[section_id.id] = self.env['baseball.practice.section.template'].create({
                'name': section_id.name,
                'sequence': section_id.sequence,
                }).id
        return {
            'name': _('Template'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'baseball.teams.practice.template',
            'type': 'ir.actions.act_window',
            'context': {
                'default_team_id':  self.team_id.id,
                'default_drill_ids': [
                    (0, 0, {
                        'section_id': section_mapping.get(line.section_id.id),
                        'drill_id': line.drill_id.id,
                        'duration': line.duration,
                        'repetitions': line.repetitions,
                        }) for line in self.drill_ids],
                },
        }

    def unlink(self):
        for rec in self:
            if rec.drill_ids or rec.present_players_ids:
                raise UserError(_('You cannot delete practice event with already saved drills or players presences counted.'))
        return super(Practices_event, self).unlink()


class Practice_load_template(models.TransientModel):
    _name = 'baseball.teams.practice.template.wizard'

    template_id = fields.Many2one('baseball.teams.practice.template', string="Template")
    practice_id = fields.Many2one('baseball.teams.practice.event', string="Practice")

    def load_template(self):
        for rec in self:
            section_mapping = {}
            for section_id in rec.template_id.section_ids:
                sequences = rec.practice_id.section_ids.mapped('sequence')
                sequence = sequences and max(sequences) or 0
                section_mapping[section_id.id] = self.env['baseball.practice.section'].create({
                    'name': section_id.name,
                    'sequence': section_id.sequence + sequence,
                    }).id
            rec.practice_id.write({
                'drill_ids': [
                    (0, 0, {
                        'section_id': section_mapping.get(line.section_id.id),
                        'drill_id': line.drill_id.id,
                        'duration': line.duration,
                        'repetitions': line.repetitions,
                        }) for line in rec.template_id.drill_ids],
                 })

class Practices_template(models.Model):
    _name = 'baseball.teams.practice.template'
    _inherit = 'baseball.teams.practice.event'

    name = fields.Char(string='Description', required=True)
    drill_ids = fields.One2many('baseball.practice.drill.template', 'practice_id', string='Drills')
    period = fields.Selection(compute=None, search=None)
    section_ids = fields.One2many(
        'baseball.practice.section.template', 'practice_id', string="Sections")

    @api.depends('name', 'duration', 'team_id.name')
    def name_get(self):
        result = []
        for rec in self:
            date = fields.Date.to_string(fields.Datetime.from_string(rec.start_time))
            duration = '{0:02.0f}h{1:02.0f}'.format(*divmod(rec.duration * 60, 60))
            if rec.team_id:
                result.append(
                    (rec.id, '%s - %s (%s)' % (rec.name, duration, rec.team_id.name)))
            else:
                result.append(
                    (rec.id, '%s - %s' % (rec.name, duration)))
        return result


class Practice_wizard(models.TransientModel):
    _name = 'baseball.teams.practice.wizard'


    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    practice_id = fields.Many2one('baseball.teams.practice', string="Practice", required=True)

    def generate_practice(self):
        for rec in self:
            dates = dateutil.rrule.rrule(
                dateutil.rrule.MONTHLY,
                byweekday=int(rec.practice_id.dayofweek), 
                byhour=int(math.floor(rec.practice_id.hour_from)), 
                byminute=int(math.floor((rec.practice_id.hour_from%1)*60)), 
                dtstart=fields.Date.from_string(rec.start_date), 
                until=fields.Date.from_string(rec.end_date))[:]
            dates = [pytz.timezone(rec._context.get('tz')).localize(x, is_dst=None).astimezone(pytz.utc) for x in dates]

            for team in rec.practice_id.team_ids:
                serie  = rec.env['baseball.teams.practice.serie'].create({})
                rec.practice_id.write({
                    'practice_event_ids': [(0,0,{
                        'start_time': fields.Datetime.to_string(date),
                        'end_time': fields.Datetime.to_string(date + dateutil.relativedelta.relativedelta(hours=(rec.practice_id.hour_to - rec.practice_id.hour_from),) ),
                        'team_id': team.id,
                        'venue_id': rec.practice_id.venue_id.id,
                        'serie_id': serie.id,
                    }) for date in dates],
                })






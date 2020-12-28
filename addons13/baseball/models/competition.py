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


class Venues(models.Model):
    _name = 'baseball.venue'

    name = fields.Char(string="Name")
    name_from_federation = fields.One2many('baseball.venue.name', 'venue_id', string="Name on federation website", required=True)
    officials_needed = fields.Boolean(string="Officials needed")
    always_show_on_website = fields.Boolean(string="Always show on website", default=False)
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    zip_code = fields.Char(string="Zip")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")

class Venues_name(models.Model):
    _name = 'baseball.venue.name'

    name = fields.Char(string="Name")
    venue_id = fields.Many2one('baseball.venue', string="Venue")

_sql_constraints = [
                     ('name_unique',
                      'unique(name)',
                      'Name of the venue name has to be unique!')
]

class Game(models.Model):
    _name = 'baseball.game'
    _order = "start_time"
    _inherit = ['mail.thread']

    @api.model
    def _default_game_type(self):
        return self.env.context.get('game_type', 'competition')


    name = fields.Char(string="Name")
    game_number = fields.Char(required=True, string="Game number")
    division = fields.Many2one('baseball.divisions', string="Division")
    start_time = fields.Datetime(string="Start Time")
    start_date = fields.Char(string="Start Date", compute="_compute_end_time")
    start_hour = fields.Char(string="Start Hour", compute="_compute_end_time")
    end_time = fields.Datetime(string="End Time", compute="_compute_end_time")
    end_time_tournament = fields.Datetime(string="End Time")
    end_date_tournament = fields.Char(string="Start Date", compute="_compute_end_time_tournament")
    end_hour_tournament = fields.Char(string="Start Hour", compute="_compute_end_time_tournament")
    home_team = fields.Many2one('baseball.teams', string="Home Team")
    away_team = fields.Many2one('baseball.teams', string="Away Team")
    score_home = fields.Char(string="Score Home")
    score_away = fields.Char(string="Score Away")
    scorer_ids = fields.Many2many('res.partner', string="Scorers", relation="game_scorer_rel", domain=['|', ('active', '=', True),  ('active', '=', False)])
    umpire_ids = fields.Many2many('res.partner', string="Umpires", relation="game_umpire_rel", domain=['|', ('active', '=', True), ('active', '=', False)])
    present_players_ids = fields.Many2many(
        'res.partner', string="Attendees", relation="game_attend")
    absent_players_ids = fields.Many2many(
        'res.partner', string="Absentees", relation="game_absent")
    invitation_ids = fields.One2many(
        'baseball.game.invitation', 'game_id', string="Invitations")
    game_type = fields.Selection([
        ('competition', "Competition game"),
        ('friendly', "Friendly game"),
        ('tournament', "Tournament"),
    ], default=_default_game_type)
    venue = fields.Many2one('baseball.venue', string="Venue")
    is_opponent = fields.Boolean(string="Opponent", compute="_get_is_opponent", store=True)
    result = fields.Selection([
        ('home', "Home"),
        ('away', "Away"),
        ('tie', "Tie"),
        ('np', "Not played"),
    ], string="Result", compute="_compute_result")
    season_id = fields.Many2one('baseball.season', string='Season', default=lambda self: self.env['baseball.season'].sudo().get_current_season())
    period = fields.Selection([
        ('past', "Past seasons"),
        ('current', "Current seasn"),
    ], compute='_get_current', search='_search_period')
    officals_reminded = fields.Boolean()

    _sql_constraints = [
        ('game_number',
         'UNIQUE(game_number,season_id)',
         "The game number must be unique"),
    ]

    @api.depends('home_team.is_opponent', 'away_team.is_opponent')
    def _get_is_opponent(self):
        for rec in self:
            rec.is_opponent = rec.home_team.is_opponent and rec.away_team.is_opponent

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

    @api.depends('score_away', 'score_home')
    def _compute_result(self):
        for rec in self:
            if rec.score_home:
                if  rec.score_home.isdigit() and rec.score_away.isdigit():
                    if int(rec.score_home) > int(rec.score_away):
                        rec.result = 'home'
                    elif int(rec.score_home) < int(rec.score_away):
                        rec.result = 'away'
                    elif int(rec.score_home) == int(rec.score_away):
                        rec.result = 'tie'
                    else:
                        rec.result = 'np'
                else:
                    if 'ff' in rec.score_home.lower():
                        rec.result = 'away'
                    elif 'ff' in rec.score_away.lower():
                        rec.result = 'home'
                    else:
                        rec.result = 'np'
            else:
                rec.result = 'np'

    def _update_offcials(self):
        if self.env.context.get('set_officals'):
            return
        self = self.with_context(set_officals=True)
        for rec in self:
            vals = {}
            if not rec.umpire_ids and (rec.home_team.is_official_umpires or
                    rec.away_team.is_official_umpires) and rec.game_type == 'competition':
                vals['umpire_ids'] = [(6, 0, self.env.ref('baseball.partner_frbbs_official').ids)]
            if not rec.scorer_ids and (rec.home_team.is_official_scorers or
                    rec.away_team.is_official_scorers) and rec.game_type == 'competition':
                vals['scorer_ids'] = [(6, 0, self.env.ref('baseball.partner_frbbs_official').ids)]
            if vals:
                rec.write(vals)

    @api.depends('start_time', 'division.average_duration')
    def _compute_end_time(self):
        for rec in self:
            if not rec.division.average_duration:
                duration = timedelta(hours=1)
            else:
                duration = timedelta(hours=rec.division.average_duration)
            if rec.start_time:
                start = fields.Datetime.from_string(rec.start_time)
                rec.end_time = start + duration

                rec.start_date = start.strftime("%d/%m/%Y")
                rec.start_hour = start.strftime("%H:%M")

    @api.depends('end_time_tournament')
    def _compute_end_time_tournament(self):
        if self.end_time_tournament:
            end = fields.Datetime.from_string(self.end_time_tournament)
            self.end_date_tournament = end.strftime("%d/%m/%Y")
            self.end_hour_tournament = end.strftime("%H:%M")

    @api.model
    def create(self, values):
        res =  super(Game, self).create(values)
        res._update_offcials()
        return res

    def write(self, vals):
        result = super(Game, self).write(vals)
        self._update_offcials()
        return result

    @api.model
    def _get_upcoming_games(self, limit=None):
        today = datetime.strftime(datetime.today(),DEFAULT_SERVER_DATE_FORMAT)
        return self.search([
            ('start_time','>=',today),
            '|', '|',
                ('home_team.is_opponent','=',False),
                ('away_team.is_opponent', '=', False,),
                ('venue.always_show_on_website', '=', True,),
                ], limit=limit)

    @api.depends('game_number', 'home_team', 'away_team')
    def name_get(self):
        result = []
        for game in self:
            result.append(
                (game.id, '[%s] %s @ %s' % (game.game_number, game.away_team.name, game.home_team.name)))
        return result

    def invite_team(self):
        for rec in self:
            team = (rec.home_team + rec.away_team).filtered(lambda r: not r.is_opponent)
            if not team.send_game_invitation:
                return
            player_ids = team.players_ids.filtered(lambda r: r not in rec.invitation_ids.mapped('partner_id') and r not in rec.absent_players_ids and r not in rec.present_players_ids)
            for player_id in player_ids:
                invite_id = rec.env['baseball.game.invitation'].create({
                        'partner_id': player_id.id,
                        'game_id': rec.id
                    })
                invite_id._send_mail_to_attendees()

    @api.model
    def invite_upcoming(self, days=7):
        now = fields.Datetime.to_string(datetime.now())
        later = fields.Datetime.to_string(datetime.now()+timedelta(days=days))
        games = self.env['baseball.game'].search([('start_time','>',now),('start_time','<',later)])
        games = games.filtered(lambda r: not r.is_opponent)
        games.invite_team()


    @api.model
    def action_get_games_database(self):
        local = pytz.timezone ("Europe/Brussels")

        def get_or_create_team(team_name, division):
            tag_name = self.env['baseball.teams.dbname'].search([('name','=',team_name)], limit=1)
            if not tag_name:
                tag_name = self.env['baseball.teams.dbname'].create({'name': team_name})

            team = self.env['baseball.teams'].search(
                [('division_ids', 'in', division.id)]).filtered(lambda r: tag_name in r.name_from_federation)[:1]
            if not team:
                alternative_team = self.env['baseball.teams'].search([]).filtered(lambda r: tag_name in r.name_from_federation)
                alternative_team = alternative_team.filtered(lambda r: division in r.division_ids.mapped('parent_related_division_ids') | r.division_ids.mapped('parent_related_division_ids').mapped('child_related_division_ids') | r.division_ids.mapped('child_related_division_ids') )
                if alternative_team:
                    alternative_team.write({'division_ids': [(4, division.id)]})
                    team = alternative_team
            if not team:
                team = self.env['baseball.teams'].create({'name_from_federation': [(4,tag_name.id)], 'name': team_name, 'division_ids': [(4, division.id)], 'is_opponent': True})
            return team

        def get_or_create_venue(name):
            if not name:
                return False
            tag_name = self.env['baseball.venue.name'].search([('name','=',name)])
            if not tag_name:
                tag_name = self.env['baseball.venue.name'].create({'name': name})
            tag_name = tag_name[0]

            venue = self.env['baseball.venue'].search([]).filtered(lambda r: tag_name in r.name_from_federation)
            if not venue:
                venue = self.env['baseball.venue'].create({'name_from_federation': [(4,tag_name.id)], 'name': name})
            return venue

        xml_frbbs_calendar = self.env['ir.config_parameter'].get_param('xml_frbbs_calendar')
        if not xml_frbbs_calendar:
            return
        # "http://www.frbbs.be/xmlGames.php?token=ed54@dAff5d!f6gDH%28T54sdF6-fJ5:9hvF!b"
        file = urllib.request.urlopen(xml_frbbs_calendar)
        data = file.read()
        file.close()

        if not data:
            return
        data = xmltodict.parse(data)

        # games = []
        for k, v in list(data.items()):
            for game in v['GameInfo']:

                ga = {}

                ga['game_number'] = game['game'].encode('utf-8')
                ga['division'] = game['division'].encode('utf-8')
                ga['date'] = game['date'].encode('utf-8')
                if ga['date'] == '0000-00-00':
                    continue
                ga['time'] = game['time'].encode('utf-8')
                ga['venue'] = game['field'].encode('utf-8')
                ga['home'] = game['home'].encode('utf-8')
                ga['away'] = game['away'].encode('utf-8')
                ga['score'] = game['score'].encode('utf-8')

                current_game = self.env['baseball.game'].search(
                    [
                        ('game_number', '=', ga['game_number']),
                        ('season_id', '=', self.env['baseball.season'].get_current_season().id),
                    ])
                division = self.env['baseball.divisions'].search(
                    [('code', '=', ga['division'])])
                if not division:
                    division = self.env['baseball.divisions'].create(
                        {'name': ga['division'], 'code': ga['division']})

                home = get_or_create_team(ga['home'], division)
                away = get_or_create_team(ga['away'], division)

                venue = get_or_create_venue(ga['venue'])

                values = {
                    'game_number': ga['game_number'],
                    'division': division.id,
                    'start_time': (game['date'] + ' ' + game['time']).encode('utf-8'),
                    'home_team': home.id,
                    'away_team': away.id,
                    'venue': venue.id,
                    'game_type': 'competition',
                }
                if ga['score'] != 'null' and ga['score'] != 'NP' and '-' in ga['score']:
                    values.update(
                        {'score_home':  (ga['score'].split('-')[0])}),
                    values.update(
                        {'score_away':  (ga['score'].split('-')[1])}),

                local_dt = local.localize(fields.Datetime.from_string(values.get('start_time')), is_dst=None)
                values.update({'start_time': fields.Datetime.to_string(local_dt.astimezone(pytz.utc))})
                if current_game:
                    current_game.write(values)
                else:
                    current_game.create(values)
                # print ga['game_number']
        for logo_id in self.env['baseball.logo'].search([]):
            teams_without_logo = self.env['baseball.teams'].search([('logo_id','=',False),('name_from_federation','ilike',logo_id.name)])
            teams_without_logo.write({'logo_id': logo_id.id})

    @api.model
    def remind_officials(self, days=3):
        now = fields.Datetime.to_string(datetime.now())
        later = fields.Datetime.to_string(datetime.now() + timedelta(days=days))
        games = self.env['baseball.game'].search([('start_time', '>', now), ('start_time', '<', later), ('officals_reminded', '=', False)])
        games = games.filtered(lambda r: not r.is_opponent)
        template_id = self.env.ref('baseball.mail_template_game_official_reminder')
        for game in games:
            if not ((game.umpire_ids | game.scorer_ids) - self.env.ref('baseball.partner_frbbs_official')):
                continue
            template_id.send_mail(game.id)
            game.officals_reminded = True


class Invitation(models.Model):
    _name = 'baseball.game.invitation'

    partner_id = fields.Many2one('res.partner', string="Player", required=True)
    game_id = fields.Many2one(
        'baseball.game', string="Game")
    state = fields.Selection([
        ('accepted', "Accepted"),
        ('declined', "Declined"),
    ], string="Answer")
    token = fields.Char('Token', readonly=True)
    is_sent = fields.Boolean('Is sent')


    @api.model
    def create(self, values):
        values['token'] = uuid.uuid4().hex
        return super(Invitation, self).create(values)

    def write(self, vals):
        result = super(Invitation, self).write(vals)
        if vals.get('state') and result:
            for record in self:
                if record.state == 'accepted':
                    record.game_id.present_players_ids |= record.partner_id
                    record.game_id.absent_players_ids -= record.partner_id
                if record.state == 'declined':
                    record.game_id.present_players_ids -= record.partner_id
                    record.game_id.absent_players_ids |= record.partner_id
        return result

    def _send_mail_to_attendees(self, template_xmlid='baseball.mail_template_game_invitation'):
        for rec in self:
            template_id = rec.env.ref(template_xmlid)
            mail_id = template_id.send_mail(rec.id)
            rec.is_sent = True
            return mail_id

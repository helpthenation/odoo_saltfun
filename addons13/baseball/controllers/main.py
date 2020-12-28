# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo import models, fields, api, exceptions, tools
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from datetime import datetime
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
from odoo.tools.translate import _

class baseball_auth_signup(AuthSignupHome):


    @http.route()
    def web_login(self, *args, **kw):
        response = super(baseball_auth_signup, self).web_login(*args, **kw)

        user_id = request.env['res.users'].sudo().search([('id','=',request.uid)])
        if user_id:
            user_id.current_partner_id = user_id.partner_id

        return response

    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            if request.env['res.partner'].sudo().search([('name','ilike',kw.get('name'))]) and not request.env['res.users'].sudo().search([('login','=',kw.get('login'))]):
                qcontext["error"] = _("A member with this name is already registered. Contact the admin or try resetting your password.")
                qcontext.update(self.signup_values())
                return request.render('auth_signup.signup', qcontext)
        res = super(baseball_auth_signup, self).web_auth_signup(*args, **kw)

        res.qcontext.update(self.signup_values())
        if 'error' not in res.qcontext and request.httprequest.method == 'POST':
            kw.update({
                'teams': [int(x) for x in request.httprequest.form.getlist('teams')],
                'categories': [int(x) for x in request.httprequest.form.getlist('categories')]
                })

            user_id = request.env['res.users'].sudo().search([('id','=',request.uid)])
            partner_id = user_id.partner_id
            self.update_partner(partner_id, **kw)
            partner_id.recalculat_current_category()
            user_id.current_partner_id = partner_id

        return res

    @http.route('/web/add_child_partner', type='http', auth='user', website=True)
    def web_auth_add_child_partner(self, *args, **kw):

        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            kw.update({
                'teams': [int(x) for x in request.httprequest.form.getlist('teams')],
                'categories': [int(x) for x in request.httprequest.form.getlist('categories')]
                })

            user_id = request.env['res.users'].sudo().search([('id','=',request.uid)])
            new_partner_id = self.add_child_partner(**kw)
            new_partner_id.recalculat_current_category()
            user_id.current_partner_id =  new_partner_id
            return request.redirect("/profile")

        qcontext.update(self.signup_values(no_values=True))
        qcontext.update({'add_partner_enabled': True})

        return request.render('auth_signup.add_child', qcontext)


    @http.route('/web/update_profile', type='http', auth='user', website=True)
    def web_auth_update_profile(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            kw.update({
                'teams': [int(x) for x in request.httprequest.form.getlist('teams')],
                'categories': [int(x) for x in request.httprequest.form.getlist('categories')]
                })
            user_id = request.env['res.users'].sudo().search([('id','=',request.uid)])
            partner_id = user_id.current_partner_id
            self.update_partner(partner_id, **kw)
            partner_id.recalculat_current_category()
            return request.redirect("/profile")

        qcontext.update(self.signup_values())

        return request.render('auth_signup.update_profile', qcontext)


    def signup_values(self, data=None, no_values=False):

        env, uid, registry = request.env, request.uid, request.registry
        countries = env['res.country'].sudo().search([])
        partner_id = env['res.users'].sudo().browse(uid).current_partner_id
        categories = env['baseball.categories'].sudo().search([])
        teams = env['baseball.teams'].sudo().search([('is_opponent','=',False)])
        signup = {}

        # Default search by user country
        if not signup.get('country_id'):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                country_ids = registry.get('res.country').search([('code', '=', country_code)])
                if country_ids:
                    signup['country_id'] = country_ids[0]

        signup['email'] = partner_id.email
        signup['gender'] = partner_id.gender
        signup['name'] = partner_id.name if uid != env.ref('base.public_user').id else False
        signup['phone'] = partner_id.phone
        signup['mobile'] = partner_id.mobile
        signup['birthdate'] = partner_id.birthdate
        signup['street']  = partner_id.street
        signup['street2']  = partner_id.street2
        signup['city'] = partner_id.city
        signup['zip'] = partner_id.zip
        signup['country_id'] = partner_id.country_id
        signup['is_player'] = partner_id.is_player
        signup['baseball_category_ids'] = partner_id.baseball_category_ids.ids
        signup['team_ids'] = partner_id.team_ids.ids
        signup['ads_authorize'] = partner_id.ads_authorize if uid != env.ref('base.public_user').id else 'on'

        if no_values:
            signup = {'email' : partner_id.email}

        values = {
            'countries': countries,
            'categories': categories,
            'teams': teams,
            'signup': signup,
            'is_active_current_season': partner_id.is_active_current_season,
        }


        return values

    def update_partner(self, partner_id, **kw):
        current_season = request.env['baseball.season'].sudo().get_current_season()
        values = {
            'name' :kw.get('name'),
            'gender' :kw.get('gender'),
            'phone' :kw.get('phone'),
            'mobile' :kw.get('mobile'),
            'birthdate' :kw.get('birthdate'),
            'street' :kw.get('street'),
            'street2' :kw.get('street2'),
            'city' :kw.get('city'),
            'zip' :kw.get('zip'),
            'country_id' :kw.get('country_id'),
            'is_player' :kw.get('is_player') =='player',
            'team_ids' : [(6,0,kw.get('teams'))] if kw.get('teams') else False,
            'ads_authorize': kw.get('ads_authorize') == 'on',
            }
        photo = kw.get('photo')
        if photo and photo.filename and photo.content_type.split('/')[0] == 'image':
            values['image'] = photo.read().encode('base64')

        partner_id.write(values)
        partner_id.recalculat_current_category()

        registration_document = kw.get('registration_document')
        if registration_document and registration_document.filename:
            extension = registration_document.filename.split('.')[-1]
            registration_id = partner_id.season_ids.filtered(lambda r: r.season_id == current_season)
            new_name = '%s_%s.%s' % (partner_id.name.lower().replace(' ', '_'), current_season.name, extension)
            attachment_value = {
                'name': new_name,
                'res_model': 'res.partner',
                'res_id': partner_id.id,
                'datas': registration_document.read().encode('base64'),
                'datas_fname': new_name,
                }
            if registration_id:
                registration_id.is_certificate = True
                attachment_value['res_id'] = registration_id.id
                attachment_value['res_model'] = 'baseball.registration'
            attachment = request.env['ir.attachment'].sudo().create(attachment_value)

    def add_child_partner(self, **kw):
        current_season = request.env['baseball.season'].sudo().get_current_season()
        user_id = request.env['res.users'].sudo().search([('id','=',request.uid)])
        values = {
            'email' : user_id.partner_id.email,
            'parent_user_id' : user_id.partner_id.id,
            'name' :kw.get('name'),
            'gender' :kw.get('gender'),
            'phone' :kw.get('phone'),
            'mobile' :kw.get('mobile'),
            'birthdate' :kw.get('birthdate'),
            'street' :kw.get('street'),
            'street2' :kw.get('street2'),
            'city' :kw.get('city'),
            'zip' :kw.get('zip'),
            'country_id' :kw.get('country_id'),
            'is_player' :kw.get('is_player') =='player',
            'team_ids' : [(6,0,kw.get('teams'))] if kw.get('teams') else False,
            'ads_authorize': kw.get('ads_authorize') == 'on',
            }

        photo = kw.get('photo')
        if photo and photo.filename and photo.content_type.split('/')[0] == 'image':
            values['image'] = photo.read().encode('base64')

        new_partner_id = request.env['res.partner'].sudo().create(values)
        new_partner_id.recalculat_current_category()

        registration_document = kw.get('registration_document')
        registration_id = new_partner_id.season_ids.filtered(lambda r: r.season_id == current_season)

        if registration_document and registration_document.filename and registration_id:
            extension = registration_document.filename.split('.')[-1]
            new_name = '%s_%s.%s' % (new_partner_id.name.lower().replace(' ', '_'), current_season.name, extension)
            attachment_value = {
                'name': new_name,
                'res_model': 'baseball.registration',
                'res_id': registration_id.id,
                'datas': registration_document.read().encode('base64'),
                'datas_fname': new_name,
                }
            attachment = request.env['ir.attachment'].sudo().create(attachment_value)
            registration_id.is_certificate = True

        return new_partner_id

class baseball_club(http.Controller):

    @http.route(['/page/teams/<int:team_id>'], type='http', auth="public", website=True)
    def team(self, team_id, **post):
        env, uid = request.env, request.uid
        team = env['baseball.teams'].sudo().browse(team_id)
        user = env['res.users'].sudo().browse(uid) if uid != env.ref('base.public_user').id else False
        values = {
            'team' : team,
            'user': user,
        }

        return request.render('baseball.team_page', values)

    @http.route(['/page/teams/<int:team_id>/calendar/practice.ics'], type='http', auth="public", website=True)
    def team_practice_calendar(self, team_id, **post):
        env, uid = request.env, request.uid
        team = env['baseball.teams'].sudo().browse(team_id)

        calendar = Calendar()
        calendar.add('prodid', '-//My practices//mxm.dk//')
        calendar.add('version', '2.0')
        calendar.add('method', 'PUBLISH')
        calendar.add('class', 'PUBLIC')
        company_id = env['res.company'].sudo().search([]) and env['res.company'].sudo().search([])[0]
        if company_id:
            organizer = vCalAddress('MAILTO:%s' % (company_id.partner_id.email))
            organizer.params['cn'] = vText(company_id.partner_id.name)
            organizer.params['role'] = vText('Baseball club')
        else:
            organizer = vCalAddress('MAILTO:')

        practice_ids = env['baseball.teams.practice.event'].sudo().search([
            ('team_id','=',team.id),
            ])

        for practice_id in practice_ids:
            practice = Event()
            practice['organizer'] = organizer
            practice.add('summary', 'Practice - %s' % (team_id.name))
            if practice_id.venue_id:
                location = '%s: %s %s, %s %s' % (practice_id.venue_id.name, practice_id.venue_id.street or '', practice_id.venue_id.street2 or '', practice_id.venue_id.zip_code or '', practice_id.venue_id.city or '')
                practice['location'] = vText(location)
            practice.add('dtstart', fields.Datetime.from_string(practice_id.start_time).replace(tzinfo=pytz.utc) )
            practice.add('dtend', fields.Datetime.from_string(practice_id.end_time).replace(tzinfo=pytz.utc))
            calendar.add_component(practice)

        return request.make_response(calendar.to_ical(), headers=[('Content-Type', 'text/calendar')])

    @http.route(['/page/teams/<int:team_id>/calendar/game.ics'], type='http', auth="public", website=True)
    def team_game_calendar(self, team_id, **post):
        env, uid = request.env, request.uid
        team = env['baseball.teams'].sudo().browse(team_id)


        calendar = Calendar()
        calendar.add('prodid', '-//My games//mxm.dk//')
        calendar.add('version', '2.0')
        calendar.add('method', 'PUBLISH')
        calendar.add('class', 'PUBLIC')
        company_id = env['res.company'].sudo().search([]) and env['res.company'].sudo().search([])[0]
        if company_id:
            organizer = vCalAddress('MAILTO:%s' % (company_id.partner_id.email))
            organizer.params['cn'] = vText(company_id.partner_id.name)
            organizer.params['role'] = vText('Baseball club')
        else:
            organizer = vCalAddress('MAILTO:')

        for game_id in team.game_ids:
            game = Event()
            game['organizer'] = organizer
            if game_id.game_type == 'tournament':
                game.add('summary', 'Tournament@ %s' % (game_id.venue.name or ''))
                if game_id.venue:
                    location = '%s: %s %s, %s %s' % (game_id.venue.name, game_id.venue.street or '', game_id.venue.street2 or '', game_id.venue.zip_code or '', game_id.venue.city or '')
                    game['location'] = vText(location)
                game.add('dtstart', fields.Datetime.from_string(game_id.start_time).replace(tzinfo=pytz.utc) )
                game.add('dtend', fields.Datetime.from_string(game_id.end_time_tournament).replace(tzinfo=pytz.utc))
            else:
                game.add('summary', '%s: vs %s (%s)' % (game_id.game_number, game_id.home_team.name if game_id.home_team != team else game_id.away_team.name, game_id.division.code))
                if game_id.venue:
                    location = '%s: %s %s, %s %s' % (game_id.venue.name, game_id.venue.street or '', game_id.venue.street2 or '', game_id.venue.zip_code or '', game_id.venue.city or '')
                    game['location'] = vText(location)
                game.add('dtstart', fields.Datetime.from_string(game_id.start_time).replace(tzinfo=pytz.utc) )
                game.add('dtend', fields.Datetime.from_string(game_id.end_time).replace(tzinfo=pytz.utc))
            calendar.add_component(game)

        return request.make_response(calendar.to_ical(), headers=[('Content-Type', 'text/calendar')])

    @http.route(['/baseball/calendar/<int:venue_id>/all.ics'], type='http', auth="public", website=True)
    def team_practice_calendar(self, venue_id, **post):
        env, uid = request.env, request.uid
        venue_id = env['baseball.venue'].sudo().browse(venue_id)

        calendar = Calendar()
        calendar.add('prodid', '-//My practices//mxm.dk//')
        calendar.add('version', '2.0')
        calendar.add('method', 'PUBLISH')
        calendar.add('class', 'PUBLIC')
        company_id = env['res.company'].sudo().search([]) and env['res.company'].sudo().search([])[0]
        if company_id:
            organizer = vCalAddress('MAILTO:%s' % (company_id.partner_id.email))
            organizer.params['cn'] = vText(company_id.partner_id.name)
            organizer.params['role'] = vText('Baseball club')
        else:
            organizer = vCalAddress('MAILTO:')

        practice_ids = env['baseball.teams.practice.event'].sudo().search([
            ('venue_id', '=', venue_id.id),
        ])

        for practice_id in practice_ids:
            practice = Event()
            practice['organizer'] = organizer
            practice.add('summary', 'Baseball Practice - %s' % (practice_id.team_id.name))
            if practice_id.venue_id:
                location = '%s: %s %s, %s %s' % (practice_id.venue_id.name, practice_id.venue_id.street or '', practice_id.venue_id.street2
                                                 or '', practice_id.venue_id.zip_code or '', practice_id.venue_id.city or '')
                practice['location'] = vText(location)
            practice.add('dtstart', fields.Datetime.from_string(practice_id.start_time).replace(tzinfo=pytz.utc))
            practice.add('dtend', fields.Datetime.from_string(practice_id.end_time).replace(tzinfo=pytz.utc))
            calendar.add_component(practice)

        game_ids = env['baseball.game'].sudo().search([
            ('venue', '=', venue_id.id),
        ])

        for game_id in game_ids:
            game = Event()
            game['organizer'] = organizer
            if game_id.game_type == 'tournament':
                game.add('summary', 'Baseball Tournament - %s' % (game_id.home_team.name or ''))
                if game_id.venue:
                    location = '%s: %s %s, %s %s' % (game_id.venue.name, game_id.venue.street or '', game_id.venue.street2 or '',
                                                     game_id.venue.zip_code or '', game_id.venue.city or '')
                    game['location'] = vText(location)
                game.add('dtstart', fields.Datetime.from_string(game_id.start_time).replace(tzinfo=pytz.utc))
                game.add('dtend', fields.Datetime.from_string(game_id.end_time_tournament).replace(tzinfo=pytz.utc))
            else:
                game.add(
                    'summary', 'Baseball Game: %s vs %s (%s)' % (game_id.home_team.name, game_id.away_team.name, game_id.division.code))
                if game_id.venue:
                    location = '%s: %s %s, %s %s' % (game_id.venue.name, game_id.venue.street or '', game_id.venue.street2 or '',
                                                     game_id.venue.zip_code or '', game_id.venue.city or '')
                    game['location'] = vText(location)
                game.add('dtstart', fields.Datetime.from_string(game_id.start_time).replace(tzinfo=pytz.utc))
                game.add('dtend', fields.Datetime.from_string(game_id.end_time).replace(tzinfo=pytz.utc))
            calendar.add_component(game)

        event_ids = env['baseball.event'].sudo().search([
            ('venue_id', '=', venue_id.id),
        ])

        for event_id in event_ids:
            event = Event()
            event['organizer'] = organizer
            event.add('summary', '%s' % event_id.name or '')
            event.add('description', '%s' % event_id.description or '')
            if event_id.venue_id:
                location = '%s: %s %s, %s %s' % (event_id.venue_id.name, event_id.venue_id.street or '', event_id.venue_id.street2 or '',
                                                        event_id.venue_id.zip_code or '', event_id.venue_id.city or '')
                event['location'] = vText(location)
            event.add('dtstart', fields.Datetime.from_string(event_id.start_time).replace(tzinfo=pytz.utc))
            event.add('dtend', fields.Datetime.from_string(event_id.end_time).replace(tzinfo=pytz.utc))
            calendar.add_component(event)

        return request.make_response(calendar.to_ical(), headers=[('Content-Type', 'text/calendar')])

    @http.route(['/player'], type='json', auth="public", methods=['POST'], website=True)
    def modal_player(self, player_id, **kw):
        context, env = request.context, request.env

        website_context = kw.get('kwargs', {}).get('context', {})
        context = dict(context or {}, **website_context)

        player = env['res.partner'].sudo().browse(int(player_id))
        teams = env['baseball.teams'].sudo().search([('is_opponent','=',False)])
        is_coach =  player in teams.mapped('coaches_ids')
        is_manager= player in teams.mapped('responsible_ids')

        request.website = request.website.with_context(context)
        return request.website._render("baseball.modal_player", {
                'player': player,
                'player_image': player.image_medium,
                'is_coach': is_coach,
                'is_manager': is_manager,
            })


    @http.route(['/game'], type='json', auth="public", methods=['POST'], website=True)
    def modal_game(self, game_id, **kw):
        context, env, uid= request.context, request.env, request.uid
        website_context = kw.get('kwargs', {}).get('context', {})
        context = dict(context or {}, **website_context)

        game = env['baseball.game'].sudo().browse(int(game_id))
        request.website = request.website.with_context(context)

        user = env['res.users'].sudo().browse(uid) if uid != env.ref('base.public_user').id else False

        return request.website._render("baseball.modal_game", {
                'game': game,
                'user': user,
            })


    @http.route(['/game/attend'], type='json', auth="public", methods=['POST'], website=True)
    def game_attend(self, game_id, **kw):
        env, uid = request.env, request.uid

        if uid == env.ref('base.public_user').id:
            return
        user_id = env['res.users'].sudo().browse(uid)
        game_id = env['baseball.game'].sudo().browse(int(game_id))

        game_id.present_players_ids |= user_id.current_partner_id
        game_id.absent_players_ids -= user_id.current_partner_id

        value = {'attending': True}
        template_id = env.ref('baseball.mail_template_game_invitation_answer')
        game_id.with_context(member_name=user_id.current_partner_id.name, presence=True, game_name=game_id.display_name).message_post_with_template(template_id.id)
        return value


    @http.route(['/game/absent'], type='json', auth="public", methods=['POST'], website=True)
    def game_absent(self, game_id, **kw):
        env, uid = request.env, request.uid

        if uid == env.ref('base.public_user').id:
            return
        user_id = env['res.users'].sudo().browse(uid)
        game_id = env['baseball.game'].sudo().browse(int(game_id))

        game_id.present_players_ids -= user_id.current_partner_id
        game_id.absent_players_ids |= user_id.current_partner_id

        value = {'attending': False}
        template_id = env.ref('baseball.mail_template_game_invitation_answer')
        game_id.with_context(member_name=user_id.current_partner_id.name, presence=False, game_name=game_id.display_name).message_post_with_template(template_id.id)
        return value

    @http.route('/game/invitation/accept', type='http', auth='public', website=True)
    def game_invite_accept(self, token, invite_id, **kwargs):
        env, uid = request.env, request.uid

        invitation_id = env['baseball.game.invitation'].sudo().search([('token','=',token), ('id','=',invite_id)])
        if invitation_id:
            invitation_id.state = 'accepted'
        game_team = invitation_id.game_id.home_team | invitation_id.game_id.away_team
        team = invitation_id.partner_id.team_ids & game_team
        values = {
            'answer': True,
            'team' : team,
            'game' : invitation_id.game_id,
            'partner': invitation_id.partner_id,
        }
        template_id = env.ref('baseball.mail_template_game_invitation_answer')
        invitation_id.game_id.with_context(member_name=invitation_id.partner_id.name, presence=True, game_name=invitation_id.game_id.display_name).message_post_with_template(template_id.id)
        return request.render('baseball.invitation_response', values)


    @http.route('/game/invitation/decline', type='http', auth='public', website=True)
    def game_invite_decline(self, token, invite_id, **kwargs):
        env, uid = request.env, request.uid

        invitation_id = env['baseball.game.invitation'].sudo().search([('token','=',token), ('id','=',invite_id)])
        if invitation_id:
            invitation_id.state = 'declined'
        game_team = invitation_id.game_id.home_team | invitation_id.game_id.away_team
        team = invitation_id.partner_id.team_ids & game_team
        values = {
            'answer': False,
            'team' : team,
            'game' : invitation_id.game_id,
            'partner': invitation_id.partner_id,
        }
        template_id = env.ref('baseball.mail_template_game_invitation_answer')
        invitation_id.game_id.with_context(member_name=invitation_id.partner_id.name, presence=False, game_name=invitation_id.game_id.display_name).message_post_with_template(template_id.id)
        return request.render('baseball.invitation_response', values)


    @http.route(['/game/score'], type='json', auth="public", methods=['POST'], website=True)
    def game_score(self, game_id, **kw):
        env, uid = request.env, request.uid

        user_id = env['res.users'].sudo().browse(uid)
        game_id = env['baseball.game'].sudo().browse(int(game_id))
        game_id.scorer_ids |= user_id.current_partner_id
        value = {
            'scoring': True,
            'scorer': user_id.current_partner_id.name,
            }
        return value


    @http.route(['/game/umpire'], type='json', auth="public", methods=['POST'], website=True)
    def game_umpire(self, game_id, **kw):
        env, uid = request.env, request.uid

        user_id = env['res.users'].sudo().browse(uid)
        game_id = env['baseball.game'].sudo().browse(int(game_id))

        game_id.umpire_ids |= user_id.partner_id

        value = {
            'umpiring': True,
            'umpire': user_id.current_partner_id.name,
        }
        return value

    @http.route(['/page/upcoming_games'], type='http', auth="public", website=True)
    def upcoming_games(self, **kw):
        env, uid = request.env, request.uid
        games = env['baseball.game'].sudo()._get_upcoming_games()
        user = env['res.users'].sudo().browse(uid) if uid != env.ref('base.public_user').id else False
        values = {
            'games' : games,
            'user': user,
        }

        return request.render('baseball.upcoming_schedule', values)

    @http.route(['/profile'], type='http', auth="user", website=True)
    def get_profile(self, **kw):
        env, uid = request.env, request.uid
        if uid != env.ref('base.public_user').id:
            user = env['res.users'].sudo().browse(uid)
            if kw.get('current_partner'):
                user.current_partner_id = int(kw.get('current_partner'))
            values = {
                'user': user,
            }

            return request.render('baseball.profile', values)
        else:
            return request.redirect("/web/login?redirect=/profile")

    @http.route(['/sponsors'], type='http', auth="public", website=True)
    def sponsors(self, **kw):
        env, uid = request.env, request.uid
        values = {
            'dossier': env.ref('baseball.sponsoring_record').sudo().dossier_id,
            'sponsors' : env['baseball.sponsor'].sudo().get_active_sponsors(),
        }

        return request.render('baseball.sponsors', values)

    @http.route(['/sponsors/<model("baseball.sponsor"):sponsor_id>'], type='http', auth="public", website=True)
    def sponsor(self, sponsor_id, **kw):
        values = {
            'sponsor' : sponsor_id.sudo(),
        }

        return request.render('baseball.sponsor', values)


    @http.route(['/practice/details/<int:practice_id>'], type='http', auth="public", website=True)
    def practice_details(self, practice_id, **post):
        env, uid = request.env, request.uid
        practice = env['baseball.teams.practice.event'].sudo().browse(practice_id)
        values = {
            'practice' : practice,
        }

        return request.render('baseball.practice_details', values)

    @http.route(['/page/teams/<int:team_id>/practice'], type='http', auth="public", website=True)
    def practice_team(self, team_id, **post):
        env, uid = request.env, request.uid
        team = env['baseball.teams'].sudo().browse(team_id)
        today = fields.Date.today()
        values = {
            'practices' : team.practice_event_ids.filtered(lambda r: today <= fields.Date.to_string(fields.Datetime.from_string(r.start_time))),
            'team' : team,
        }

        return request.render('baseball.team_practice', values)



    @http.route([
        '/coach/drill',
        '/coach/drill/<model("baseball.drill"):drill>',
        '/coach/drill/page/<int:page>',
        '/coach/drill/category/<model("baseball.categories"):category>',
        '/coach/drill/category/<model("baseball.categories"):category>/page/<int:page>',
        '/coach/drill/skill/<model("baseball.skill"):skill>',
        '/coach/drill/skill/<model("baseball.skill"):skill>/page/<int:page>',
        '/coach/drill/category/<model("baseball.categories"):category>/skill/<model("baseball.skill"):skill>',
        '/coach/drill/category/<model("baseball.categories"):category>/skill/<model("baseball.skill"):skill>/page/<int:page>',
    ], type='http', auth="public", website=True)
    def all_drills(self, drill=None, category=None, skill=None, page=1, **opt):
        _drills_per_page = 20

        env, cr, uid, context = request.env, request.cr, request.uid, request.context

        # build the domain for drills to display
        domain = []
        if category:
            domain += [('category_ids', 'in', category.id)]
        if skill:
            domain += [('skill_ids', 'in', skill.id)]

        drill_ids = env['baseball.drill'].search(domain)

        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=len(drill_ids),
            page=page,
            step=_drills_per_page,
        )
        pager_begin = (page - 1) * _drills_per_page
        pager_end = page * _drills_per_page
        drill_ids = drill_ids[pager_begin:pager_end]

        domain = [('published','=',True)]
        category_ids = env['baseball.categories'].sudo().search(domain)

        domain = [('published','=',True)]
        if category:
            domain += [('drill_ids.category_ids', 'in', category.id)]
        if drill:
            domain += [('drill_ids', 'in', drill.id)]
        skill_ids = env['baseball.skill'].sudo().search(domain)

        values = {
            'drill': drill or env['baseball.drill'],
            'drills': drill_ids or env['baseball.drill'],
            'category_ids': category_ids or env['baseball.categories'],
            'skill_ids': skill_ids or env['baseball.skill'],
            'category': category or env['baseball.categories'],
            'skill': skill or env['baseball.skill'],
            'pager': pager,
        }
        return request.render("baseball.all_drills", values)


class WebsiteBlog(WebsiteBlog):

    @http.route([
        """/blog/<model('blog.blog'):blog>/post/"""
        """<model('blog.post', '[("blog_id","=", "blog[0]")]'):blog_post>"""],
        type='http', auth="public", website=True)
    def blog_post(self, blog, blog_post,
                  tag_id=None, page=1, enable_editor=None, **post):
        response = super(WebsiteBlog, self).blog_post(
            blog, blog_post, tag_id=None, page=1, enable_editor=None, **post)
        response.qcontext['lang'] = request.context['lang']
        response.qcontext['base_url'] = request.httprequest.url
        return response

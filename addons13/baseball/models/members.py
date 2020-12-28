# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import ValidationError, Warning
from datetime import datetime
import werkzeug


class Members(models.Model):
    _inherit = 'res.partner'
    _order = 'lastname,name'
    
    firstname = fields.Char('First name',)
    lastname = fields.Char('Last name',)
    name = fields.Char(
        compute="_compute_name",
        inverse="_inverse_name_after_cleaning_whitespace",
        required=False,
        store=True)
    baseball_category_ids = fields.Many2many(
        'baseball.categories', string="Categories", compute='_players_in_categories', store=True)
    team_ids = fields.Many2many(
        'baseball.teams', string="Teams", relation="team_players")
    club_role_ids = fields.Many2many('baseball.roles', string="Roles")
    main_club_role_id = fields.Many2one('baseball.roles', string="Main Role", compute='_compute_main_role', store=True)
    is_in_order = fields.Boolean(readonly=True, string="Is in order", compute='_is_in_order', store=True)
    is_registered = fields.Boolean(readonly=True, string="Licenced", compute='_is_in_order', store=True)
    is_photo = fields.Boolean(
        default=False, string="Photo", compute='_check_photo', store=True)
    licence_number = fields.Char(string="Licence")
    jerseys_ids = fields.One2many(
        'baseball.jerseysitem', 'member_id', string="Jerseys")
    season_ids = fields.One2many(
        'baseball.registration', 'member_id', string="Seasons", track_visibility='always')
    season_id = fields.Many2one('baseball.season', related='season_ids.season_id', string='Season')
    present_games_ids = fields.Many2many(
        'baseball.game', string="Attended Games", relation="game_attend")
    absent_games_ids = fields.Many2many(
        'baseball.game', string="Missed Games", relation="game_absent")
    positions_ids = fields.Many2many('baseball.positions', string="Positions")
    positions_ids_names = fields.Char(
        string='Positions',
        compute='_compute_positions_names',
        store=True
    )
    personal_comments = fields.Html()
    private_comments = fields.Html()
    is_active_current_season = fields.Boolean('Active current season', default=False, compute='_is_active_this_season', store=True)
    is_certificate = fields.Boolean('Certificate', default=False, compute='_is_in_order', store=True)
    is_player = fields.Boolean('Player', default=True)
    game_ids = fields.Many2many(
        'baseball.game', string="Games", compute="_compute_games", store=True)
    gender = fields.Selection([('male', 'Male'),('female', 'Female')], string="Gender")
    field_street = fields.Char('Field Street')
    field_city = fields.Char('Field City')
    field_zip = fields.Char('Field Zip')
    field_country_id = fields.Many2one('res.country', 'Field Country')
    nationality_id = fields.Many2one('res.country', 'Nationality')
    debt = fields.Monetary(string="Debt", compute='_compute_debt', store=True)
    parent_user_id = fields.Many2one('res.partner', 'Parent member')
    child_partner_ids = fields.One2many('res.partner', 'parent_user_id', string="Child members")
    is_user = fields.Boolean('User', compute="_is_user", store=True)
    fee_to_pay = fields.Monetary(string="Season Fee", compute='_compute_fee', store=True)
    fee_paid = fields.Monetary(string="Season Paid", compute='_compute_fee', store=True)
    email2 = fields.Char(string="Email 2")
    mobile2 = fields.Char(string="Mobile 2")
    practice_event_ids = fields.Many2many(
        'baseball.teams.practice.event', string="Practices", compute='_get_practices', store=True)
    birthdate = fields.Date('Birthdate')
    count_jerseys = fields.Integer(string="Count jerseys", compute='_compute_count_jerseys', store=True)
    ads_authorize = fields.Boolean('Authorize sponsor', default=False)
    tab_ids = fields.One2many('baseball.tab', 'member_id', string="Tabs")
    payment_ids = fields.One2many('account.payment', 'partner_id', string="Payments")
    tab_debt = fields.Float(srring='Current Tab', compute='_get_tab_total', store=True)


    @api.model
    def create(self, vals):
        """Add inverted names at creation if unavailable."""
        context = dict(self.env.context)
        name = vals.get("name", context.get("default_name"))

        if name is not None:
            # Calculate the splitted fields
            inverted = self._get_inverse_name(
                self._get_whitespace_cleaned_name(name),
                vals.get("is_company",
                         self.default_get(["is_company"])["is_company"]))

            for key, value in inverted.items():
                if not vals.get(key) or context.get("copy"):
                    vals[key] = value

            # Remove the combined fields
            if "name" in vals:
                del vals["name"]
            if "default_name" in context:
                del context["default_name"]

        result = super(Members, self.with_context(context)).create(vals)
        result._add_role_followers()
        return result

    def copy(self, default=None):
        """Ensure partners are copied right.
        Odoo adds ``(copy)`` to the end of :attr:`~.name`, but that would get
        ignored in :meth:`~.create` because it also copies explicitly firstname
        and lastname fields.
        """
        return super(Members, self.with_context(copy=True)).copy(default)

    @api.model
    def default_get(self, fields_list):
        """Invert name when getting default values."""
        result = super(Members, self).default_get(fields_list)

        inverted = self._get_inverse_name(
            self._get_whitespace_cleaned_name(result.get("name", "")),
            result.get("is_company", False))

        for field in list(inverted.keys()):
            if field in fields_list:
                result[field] = inverted.get(field)

        return result

    def _add_role_followers(self):
        channel = self.env.ref('baseball.channel_registration', raise_if_not_found=False)
        if not channel:
            return
        self.message_subscribe(channel_ids=channel.ids)

    @api.model
    def _get_computed_name(self, lastname, firstname):
        return " ".join((p for p in (firstname , lastname) if p))

    @api.depends("jerseys_ids")
    def _compute_count_jerseys(self):
        for rec in self:
            rec.count_jerseys = len(rec.jerseys_ids)

    @api.depends("firstname", "lastname")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for rec in self:
            rec.name = rec._get_computed_name(rec.lastname, rec.firstname)

    def _inverse_name_after_cleaning_whitespace(self):
        # Remove unneeded whitespace
        for rec in self:
            clean = rec._get_whitespace_cleaned_name(rec.name)

            # Clean name avoiding infinite recursion
            if rec.name != clean:
                rec.name = clean

            # Save name in the real fields
            else:
                rec._inverse_name()

    @api.model
    def _get_whitespace_cleaned_name(self, name):
        return " ".join(name.split(None)) if name else name

    @api.model
    def _get_inverse_name(self, name, is_company=False):
        """Compute the inverted name.
        - If the partner is a company, save it in the lastname.
        - Otherwise, make a guess.
        This method can be easily overriden by other submodules.
        You can also override this method to change the order of name's
        attributes
        When this method is called, :attr:`~.name` already has unified and
        trimmed whitespace.
        """
        # Company name goes to the lastname
        if is_company or not name:
            parts = [name or False, False]
        # Guess name splitting
        else:
            parts = name.strip().split(" ", 1)
            while len(parts) < 2:
                parts.append(False)
        return {"lastname": parts[1], "firstname": parts[0]}

    def _inverse_name(self):
        """Try to revert the effect of :meth:`._compute_name`."""
        for rec in self:
            parts = rec._get_inverse_name(rec.name, rec.is_company)
            rec.lastname, rec.firstname = parts["lastname"], parts["firstname"]


    @api.onchange("firstname", "lastname")
    def _onchange_subnames(self):
        """Avoid recursion when the user changes one of these fields.
        This forces to skip the :attr:`~.name` inversion when the user is
        setting it in a not-inverted way.
        """
        # Modify self's context without creating a new Environment.
        # See https://github.com/odoo/odoo/issues/7472#issuecomment-119503916.
        for rec in self:
            rec.env.context = rec.with_context(skip_onchange=True).env.context

    @api.onchange("name")
    def _onchange_name(self):
        """Ensure :attr:`~.name` is inverted in the UI."""
        for rec in self:
            if rec.env.context.get("skip_onchange"):
                # Do not skip next onchange
                rec.env.context = (
                    rec.with_context(skip_onchange=False).env.context)
            else:
                rec._inverse_name_after_cleaning_whitespace()

    @api.model
    def _install_partner_firstname(self):
        """Save names correctly in the database.
        Before installing the module, field ``name`` contains all full names.
        When installing it, this method parses those names and saves them
        correctly into the database. This can be called later too if needed.
        """
        # Find records with empty firstname and lastname
        records = self.search([("firstname", "=", False),
                               ("lastname", "=", False)])

        # Force calculations there
        records._inverse_name()

    @api.depends('team_ids', 'company_id.current_season_id')
    def _players_in_categories(self):
        for rec in self:
            for team_id in rec.team_ids:
                rec.baseball_category_ids |= rec.env['baseball.categories'].search(
                    [('teams_ids', 'in', team_id.id)])
            current_register = rec.season_ids.filtered(lambda r: r.season_id == rec.company_id.current_season_id)
            rec.baseball_category_ids |= current_register.mapped('category_id')

    @api.depends('positions_ids')
    def _compute_positions_names(self):
        for rec in self:
            rec.positions_ids_names = ', '.join(rec.positions_ids.mapped('name'))

    @api.depends('image_1920')
    def _check_photo(self):
        for rec in self:
            if rec.image_1920:
                rec.is_photo = True
            else:
                rec.is_photo = False

    @api.depends('season_ids.season_id.is_current', 'company_id.current_season_id')
    def _is_active_this_season(self):
        for rec in self:
            if rec.company_id.current_season_id and rec.company_id.current_season_id.id in rec.season_ids.mapped('season_id').ids :
                rec.is_active_current_season = True
            else:
                rec.is_active_current_season = False
    
    @api.depends('is_photo','season_ids.is_certificate', 'season_ids.is_registered', 'season_ids.fee_to_pay', 'season_ids.fee_paid', 'company_id.current_season_id')
    def _is_in_order(self):
        for rec in self:
            if rec.company_id.current_season_id.id in rec.season_ids.mapped('season_id').ids :
                current_register = rec.season_ids.filtered(lambda r: r.season_id == rec.company_id.current_season_id)
                rec.is_certificate = any(current_register.mapped('is_certificate'))
                rec.is_registered =  all(current_register.mapped('is_registered'))
                rec.is_in_order = all([rec.is_photo,rec.is_certificate, all(current_register.mapped(lambda r: round(r.fee_to_pay - r.fee_paid,2) <= 0.01))])
            else:
                rec.is_certificate = False
                rec.is_registered =  False
                rec.is_in_order = False

    @api.depends('team_ids.practice_event_ids.start_time')
    def _get_practices(self):
        for rec in self:
            rec.practice_event_ids = rec.team_ids.mapped('practice_event_ids').sorted(key=lambda r: r.start_time)

    def _compute_games(self):
        for rec in self:
            rec.game_ids = rec.team_ids.mapped('game_ids').sorted(key=lambda r: r.start_time)

    @api.depends('club_role_ids')
    def _compute_main_role(self):
        for rec in self:
            rec.main_club_role_id = rec.club_role_ids[:1]

    @api.depends('season_ids.fee_to_pay','season_ids.fee_paid', 'tab_debt')
    def _compute_debt(self):
        for rec in self:
            rec.debt = round(sum(rec.season_ids.mapped(lambda r: r.fee_to_pay - r.fee_paid)) + rec.tab_debt,2)

    def recalculat_current_category(self):
        current_season = self.company_id.current_season_id
        current_registration_ids = self.season_ids.filtered(lambda r: r.season_id == current_season)

        categories = self.baseball_category_ids.sorted(lambda r: r.cotisation, reverse=True)
        if categories:
            category = categories[0]
            if current_registration_ids:
                for current_registration_id in current_registration_ids:
                    if current_registration_id and current_registration_id.category_id != category:
                        current_registration_id.category_id = category
            else:
                old_registration = self.season_ids
                new_registration = self.env['baseball.registration'].new({
                    'member_id': self.id,
                    'season_id': current_season.id,
                    'category_id': category.id
                    })
                if self.season_ids != old_registration | new_registration:
                    self.season_ids = old_registration | new_registration

    def google_map_img(self, zoom=8, width=298, height=298, field=False):
        if field:
            params = {
                'center': '%s, %s %s, %s' % (self.field_street or '', self.field_city or '', self.field_zip or '', self.field_country_id and self.field_country_id.name_get()[0][1] or ''),
                'size': "%sx%s" % (height, width),
                'zoom': zoom,
                'sensor': 'false',
            }
        else:
            params = {
                'center': '%s, %s %s, %s' % (self.street or '', self.city or '', self.zip or '', self.country_id and self.country_id.name_get()[0][1] or ''),
                'size': "%sx%s" % (height, width),
                'zoom': zoom,
                'sensor': 'false',
            }
        print(urlplus('//maps.googleapis.com/maps/api/staticmap' , params))
        return urlplus('//maps.googleapis.com/maps/api/staticmap' , params)

    def google_map_link(self, zoom=10, field=False):
        if field:
            params = {
                'q': '%s, %s %s, %s' % (self.field_street or '', self.field_city  or '', self.field_zip or '', self.field_country_id and self.field_country_id.name_get()[0][1] or ''),
                'z': zoom,
            }
        else:
            params = {
                'q': '%s, %s %s, %s' % (self.street or '', self.city  or '', self.zip or '', self.country_id and self.country_id.name_get()[0][1] or ''),
                'z': zoom,
            }
        print(urlplus('https://maps.google.com/maps' , params))
        return urlplus('https://maps.google.com/maps' , params)

    @api.depends('user_ids')
    def _is_user(self):
        for rec in self:
            rec.is_user = True if rec.user_ids else False


    @api.depends('season_ids.fee_paid', 'season_ids.fee_to_pay', 'season_ids.season_id.is_current')
    def _compute_fee(self):
        for rec in self:
            current_registration = rec.season_ids.filtered(lambda r: r.season_id.is_current)
            rec.fee_paid = sum(current_registration.mapped('fee_paid'))
            rec.fee_to_pay = sum(current_registration.mapped('fee_to_pay'))

    @api.depends('tab_ids.to_pay', 'tab_ids.paid')
    def _get_tab_total(self):
        for rec in self:
            rec.tab_debt = sum(rec.tab_ids.mapped('to_pay')) - sum(rec.tab_ids.mapped('paid')) 

    def create_user(self):
        for rec in self:
            existing_user = rec.env['res.users'].search([('login','=',rec.email)])
            if existing_user and not rec.user_ids:
                raise Warning('Cannot create user. A user with the same email address already exists! Either link the member to a parent member or change the email address.')
            if rec.email and not rec.user_ids:
                rec.env['res.users'].create({
                    'partner_id': rec.id,
                    'login': rec.email,
                    'groups_id': [(6,0, rec.env.ref('base.group_portal').ids)],
                    'active': True,
                    })

    _sql_constraints = [(
        'check_name',
        "CHECK( 1=1 )",
        'Contacts require a name.'
    )]

class Positions(models.Model):
    _name = 'baseball.positions'
    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    description = fields.Html()

def urlplus(url, params):
    return werkzeug.Href(url)(params or None)

class res_company(models.Model):
    _inherit = "res.company"

    def google_map_img(self, zoom=8, width=298, height=298, field=False):
        return self.sudo().partner_id and self.sudo().partner_id.google_map_img(zoom, width, height, field=field) or None
    def google_map_link(self, zoom=8, field=False):
        return self.sudo().partner_id and self.sudo().partner_id.google_map_link(zoom, field=field) or None







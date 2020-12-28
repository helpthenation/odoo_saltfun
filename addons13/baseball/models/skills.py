# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class PracticeDrill(models.Model):
    _name = 'baseball.practice.drill'
    _order = 'section_sequence,sequence'

    sequence = fields.Integer('Sequence')
    section_sequence = fields.Integer('Section Sequence', related='section_id.sequence', store=True)
    practice_id = fields.Many2one('baseball.teams.practice.event', string='Practice')
    section_id = fields.Many2one('baseball.practice.section', string='Section', domain="['|', ('practice_id','=',parent.id), '&',('practice_copy_id','=',parent.id), ('practice_copy_id', '!=', False)]")
    team_id = fields.Many2one('baseball.teams', string='Team', related='practice_id.team_id', readonly=True)
    category_ids = fields.Many2many('baseball.categories', string='Categories', related='team_id.category_ids', readonly=True)
    drill_id = fields.Many2one('baseball.drill', string='Exercice', domain="[('team_ids','in',parent.team_id)]")
    skill_ids = fields.Many2many('baseball.skill', string='Skills', related='drill_id.skill_ids', readonly=True)

    time = fields.Float(string="Time")
    duration = fields.Float(string="Duration")
    repetitions = fields.Integer(string="Repetitions")
    material_ids = fields.Many2many('baseball.practice.material', string="Material", related='drill_id.material_ids', readonly=True)

class PracticeDrillTemplate(models.Model):
    _name = 'baseball.practice.drill.template'
    _inherit = 'baseball.practice.drill'

    practice_id = fields.Many2one('baseball.teams.practice.template', string='Practice template')
    section_id = fields.Many2one('baseball.practice.section.template', string='Section', domain="['|', ('practice_id','=',parent.id), '&',('practice_copy_id','=',parent.id), ('practice_copy_id', '!=', False)]")

class PracticeSection(models.Model):
    _name = 'baseball.practice.section'
    _order = 'sequence'

    name = fields.Char(string="Name")
    sequence = fields.Integer('Sequence')
    duration = fields.Float(string="Duration", compute='_get_duration')
    line_ids = fields.One2many(
        'baseball.practice.drill',
        'section_id',
        string='Practice line',)
    practice_id = fields.Many2one(
        'baseball.teams.practice.event',
        'Practice',
         related="line_ids.practice_id",
         store=True,
         readonly=True,
         ondelete='cascade',
         index=True
    )
    practice_copy_id = fields.Many2one( 
        'baseball.teams.practice.event',
        'Practice copy',
    )

    def _get_duration(self):
        for rec in self:
            rec.duration = sum(rec.line_ids.mapped('duration'))

class PracticeSectionTemplate(models.Model):
    _name = 'baseball.practice.section.template'
    _inherit = 'baseball.practice.section'

    line_ids = fields.One2many(
        'baseball.practice.drill.template',
        'section_id',
        string='Practice line',)
    practice_id = fields.Many2one(
        'baseball.teams.practice.template',
        'Practice template',
         related="line_ids.practice_id",
         store=True,
         readonly=True,
         ondelete='cascade',
         index=True
    )
    practice_copy_id = fields.Many2one( 
        'baseball.teams.practice.template',
        'Practice template copy',
    )



class Skill(models.Model):
    _name = 'baseball.skill'

    name = fields.Char(string="Name")
    published = fields.Boolean('Published', default=True)
    minimal_category_id = fields.Many2one('baseball.categories', string="Minimal category")
    category_ids = fields.Many2many('baseball.categories', string="Concerned categories")
    team_ids = fields.Many2many('baseball.teams', string="Concerned teams", compute='_get_teams', store=True)
    drill_ids = fields.Many2many('baseball.drill', string="Drills")

    @api.depends('category_ids.teams_ids')
    def _get_teams(self):
        for rec in self:
            rec.team_ids = rec.mapped('category_ids.teams_ids')


class Drill(models.Model):
    _name = 'baseball.drill'


    def _default_content(self):
        return '''  <div class="container">
                        <section class="mt16 mb16">
                            <p class="o_default_snippet_text">''' + "Commencez à écrire ici ..." + '''</p>
                        </section>
                    </div> '''

    name = fields.Char(string="Name")
    website_published = fields.Boolean('Published', default=True)
    range_number = fields.Char(string="Number of players", compute='_get_range_number_player')
    minimal_number = fields.Integer(string="Minimal number of players")
    maximal_number = fields.Integer(string="Maximal number of players")

    range_time = fields.Char(string="Duration", compute='_get_range_duration')
    minimal_duration = fields.Float(string="Minimal duration")
    maximal_duration = fields.Float(string="Maximal duration")

    description = fields.Html(string="Description", default=_default_content)
    material_ids = fields.Many2many('baseball.practice.material', string="Material")

    minimal_category_id = fields.Many2one('baseball.categories', string="Minimal category")
    category_ids = fields.Many2many('baseball.categories', string="Concerned categories")
    team_ids = fields.Many2many('baseball.teams', string="Concerned teams", related='category_ids.teams_ids', readonly=True)
    skill_ids = fields.Many2many('baseball.skill', string="Skills")

    @api.depends('minimal_number', 'maximal_number')
    def _get_range_number_player(self):
        for rec in self:
            rec.range_number = '%s-%s' % (rec.minimal_number, rec.maximal_number)

    @api.depends('minimal_duration', 'maximal_number')
    def _get_range_duration(self):
        for rec in self:
            rec.range_time = '%s-%s' % (rec.minimal_duration, rec.maximal_duration)

    @api.model
    def create_new(self):
        return self.create({
            'name': 'Nouveau Drill',
            'website_published': False,
            }).id



class Material(models.Model):
    _name = 'baseball.practice.material'

    name = fields.Char(string="Name")
    description = fields.Html(string="Description")
    


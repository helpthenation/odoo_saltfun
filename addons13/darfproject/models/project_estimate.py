from odoo import models, fields, api


class ProjectEstimate(models.Model):
    
    _name = "project.estimate"
    
    name = fields.Char(string="Name of project")
    #estimation of project
    project_scoring = fields.One2many('project.scoring','estimating_project_id',string="Estimation for project")
    

class ProjectScoring(models.Model):
    
    _name = 'project.scoring'
    
    scoring_name = fields.Many2one('scoring.item.setting',string="Name")
    estimating_project_id = fields.Many2one('project.estimate')
    weight = fields.Integer(string="Weight",related="scoring_name.weight")
    value = fields.Integer(string="Balls")    
    result_estimation = fields.Float(string="Estimation",compute="_result_estimation")
    

    def _result_estimation(self):
        if self.weight and self.value and self.scoring_name.parent_item:
            self.result_estimation = self.weight/100*self.value
        if self.scoring_name.parent_item is False and self.weight and self.value:
            get_all_childs = self.env['scoring.item.setting'].search([('parent_item','=',self.id)])
            scoring_of_main = 0
            for item_of_child in get_all_childs:
                scoring_of_main = scoring_of_main + (item_of_child.weight/100 * item_of_child.value)
            self.result_estimation = scoring_of_main
    
    
#setting for scoring here we can create item witch we can use for project estimation     

class ScoringItemSetting(models.Model):
    
    _name = 'scoring.item.setting'
    
    name = fields.Char(string='Name of criteria')
    weight = fields.Integer(string="Weight")
    state = fields.Selection([('main','Integration'),
                              ('child','Child')],string='State (main or child)')
    number = fields.Integer(string="Number")
    parent_item = fields.Many2one('scoring.item.setting',string='Parent Item')

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_visited = fields.Boolean(string='Is Visited', default=False)
    module_name = fields.Char()
    version = fields.Char()
    category = fields.Char()

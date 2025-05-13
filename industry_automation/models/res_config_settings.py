from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    industry_automation_project_id = fields.Many2one(
        'project.project',
        string="Default Project for Dump Tasks",
        config_parameter='industry_automation.project_id'
    )

    industry_automation_output_path = fields.Char(
        string="Output Path for Saved Files",
        config_parameter='industry_automation.output_path'
    )
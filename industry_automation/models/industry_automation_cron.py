from odoo import models, api
from ..utils import file_utils


class IndustryAutomationCron(models.Model):
    _name = "industry.automation.cron"
    _description = 'Industry Automation Cron Jobs'

    @api.model
    def process_new_tasks(self):
        project_id = self.env['ir.config_parameter'].sudo().get_param('industry_automation.project_id')
        if not project_id:
            return
        
        new_stage = self.env['project.task.type'].search([
            ('name', '=', 'New')
        ])
        
        tasks = self.env['project.task'].search([
            ('project_id', '=', int(project_id)),
            ('stage_id', '=', new_stage.id),
            ('is_visited', '=', False)
        ])
        for task in tasks:
            attachments = task.attachment_ids
            for attachment in attachments:
                if attachment.name.lower().endswith('.zip'):
                    file_utils.export_module_zip(attachment)
                    task.sudo().write({'is_visited': True})


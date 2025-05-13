from odoo import models, api
from ..utils import file_utils


class IndustryAutomationCron(models.Model):
    _name = "industry.automation.cron"
    _description = 'Industry Automation Cron Jobs'

    @api.model
    def process_new_tasks(self):
        project_id = self.env['ir.config_parameter'].sudo().get_param('industry_automation.project_id')
        output_path = self.env['ir.config_parameter'].sudo().get_param('industry_automation.output_path')

        if not project_id:
            return
        if not output_path:
            return
        
        spec_stage = self.env['project.task.type'].sudo().search([
                ('name', '=', 'Spec'),
                ('project_ids', 'in', int(project_id))
            ], limit=1)
        
        tasks = self.env['project.task'].sudo().search([
            ('project_id', '=', int(project_id)),
            ('stage_id', '=', spec_stage.id),
            ('state', '=', '01_in_progress')
        ])
        breakpoint()
        for task in tasks:
            attachments = task.attachment_ids
            for attachment in attachments:
                if attachment.name.lower().endswith('.zip'):
                    
                    module_name =task.module_name
                    version =task.version
                    category =task.category
                    file_utils.export_module_zip(attachment, output_path, module_name, version, category)
                    task.sudo().write({'state': '03_approved'})

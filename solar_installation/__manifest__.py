{
    'name': 'Solar Installation',
    'version': '1.0',
    'category': 'Services',
    'description': """
This configuration is designed for companies specializing in solar equipment and installation services.
They cater to both residential and commercial customers, accommodating capacities ranging from 1 kW to 100 kW, 
ensuring the efficient installation of solar panels and associated equipment.
""",
    'depends': [
        'account_followup', 
        'appointment_crm', 
        'crm_enterprise', 
        'helpdesk_fsm',
        'helpdesk_stock',
        'helpdesk_account',
        'helpdesk_repair',
        'industry_fsm_sale_report', 
        'industry_fsm_stock', 
        'mrp_account', 
        'product_expiry', 
        'project_sms', 
        'repair', 
        'sale_crm', 
        'sale_planning', 
        'sale_purchase', 
        'stock_landed_costs', 
        'website_appointment', 
        'website_crm', 
        'website_helpdesk_knowledge', 
        'website_livechat',
    ],
    'data': [
        'data/helpdesk_config.xml',
        'data/ir_attachment_pre.xml',
        'data/ir_model.xml',
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_model_access.xml',
        'data/ir_rule.xml',
        'data/project_task_type.xml',
        'data/product_category.xml',
        'data/worksheet_template.xml',
        'data/account_analytic_plan.xml',
        'data/account_analytic_account.xml',
        'data/project_project.xml',
        'data/product_template.xml',
        'data/product_product.xml',
        'data/sale_order_template.xml',
        'data/sale_order_template_line.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/ir_attachment_post.xml',
        'data/mrp_bom.xml',
        'data/mrp_bom_line.xml',
        'data/chatbot_script.xml',
        'data/chatbot_script_answer.xml',
        'data/chatbot_script_step.xml',
        'data/im_livechat_channel.xml',
        'data/im_livechat_channel_rule.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/crm_tag.xml',
        'demo/crm_stage.xml',
        'demo/crm_lead.xml',
        'demo/crm_team.xml',
        'demo/product_supplierinfo.xml',
        'demo/stock_lot.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_post.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_post.xml',
        'demo/project_task.xml',
        'demo/website_ir_attachment.xml',
        'demo/website.xml',
        'demo/website_view.xml',
        'demo/website_page.xml',
        'demo/website_menu.xml',
        'demo/website_theme_apply.xml',
        'demo/helpdesk_ticket.xml',
        'demo/stock_picking_return.xml',
        'demo/ir_attachment_post.xml',
    ],
    'license': 'OPL-1',
    'images': ['images/main.png'],
}

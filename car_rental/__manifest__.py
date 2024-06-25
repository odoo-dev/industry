{
    'name': 'Car Rental',
    'version': '1.0',
    'category': 'Services',
    'description': """
This module is for car rental companies, for short or long-distance travel renting or tailored services based on the customer's specific requirements.
""",
    'depends': [
        'account_followup',
        'base_automation',
        'crm',
        'knowledge',
        'purchase_stock',
        'sale_purchase',
        'sale_renting_crm',
        'sale_stock_renting',
        'sale_timesheet',
        'timesheet_grid',
        'payment_demo',
        'web_studio',
        'website_crm',
        'website_sale_stock',
    ],
    'data': [
        'data/base_automation.xml',
        'data/ir_model_fields.xml',
        'data/ir_actions_server.xml',
        'data/ir_ui_view.xml',
        'data/ir_attachment_pre.xml',
        'data/product_category.xml',
        'data/project_project.xml',
        'data/product_product.xml',
        'data/res_config_settings.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/payment_provider_demo.xml',
        'data/ir_attachment_post.xml',
        'data/mail_message.xml',
    ],
    'demo': [
        'demo/account_analytic_plan.xml',
        'demo/account_analytic_account.xml',
        'demo/project_project.xml',
        'demo/website.xml',
        'demo/res_partner.xml',
        'demo/crm_team.xml',
        'demo/crm_lead.xml',
        'demo/product_pricing.xml',
        'demo/product_supplierinfo.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_confirm.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_post.xml',
        'demo/purchase_order_line_post.xml',
        'demo/website_ir_attachment.xml',
        'demo/payment_provider_demo.xml',
        'demo/website_view.xml',
        'demo/website_theme_apply.xml',
    ],
    'license': 'OPL-1',
    'images': ['images/main.png'],
}

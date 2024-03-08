{
    'name': 'Car Rental',
    'version': '1.0',
    'category': 'Services',
    'description': """
This module pre-configures Odoo to manage your fleet. Easily purchase a new car or rent one for short or long-distance travel. Provide also tailored car rental services based on the customer's specific requirements.
""",
    'depends': [
        "account_followup",
        "base_automation",
        "crm_enterprise",
        "fleet",
        "knowledge",
        "purchase_stock",
        "sale_purchase",
        "sale_renting_crm",
        "sale_stock_renting",
        "sale_timesheet",
        "timesheet_grid",
        "website_crm",
        "website_sale_stock",
    ],
    'data': [
        'data/base_automation.xml',
        'data/ir_model_fields.xml',
        'data/ir_actions_server.xml',
        'data/ir_ui_view.xml',
        'data/fleet_vehicle_state.xml',
        'data/fleet_vehicle.xml',
        'data/ir_attachment_pre.xml',
        'data/project_task_type.xml',
        'data/product_category.xml',
        'data/account_analytic_plan.xml',
        'data/account_analytic_account.xml',
        'data/project_project.xml',
        'data/uom_uom.xml',
        'data/product_template.xml',
        'data/product_product.xml',
        'data/res_config_settings.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/ir_attachment_post.xml',
    ],
    'demo': [
        'demo/website.xml',
        'demo/res_partner.xml',
        'demo/crm_team.xml',
        'demo/crm_lead.xml',
        'demo/product_supplierinfo.xml',
        'demo/project_task.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_confirm.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_post.xml',
        'demo/purchase_order_line_post.xml',
        'demo/website_ir_attachment.xml',
        'demo/website_view.xml',
        'demo/website_theme_apply.xml',
    ],
    'license': 'OPL-1',
    'images': ['images/main.png'],
    'maintenance_loc': 18,
}

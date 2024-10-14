{
    'name': 'Real Estate',
    'version': '1.0',
    'category': 'Services',
    'description': """
Manage your long term or mid long term rental properties
Manage your properties, create and manage rental contracts, and streamline your entire rental process. Efficient property management.
""",
    'depends': [
        'base_automation',
        'crm_enterprise',
        'crm_iap_enrich',
        'crm_iap_mine',
        'knowledge',
        'project_sale_subscription',
        'sale_crm',
        'website_crm',
        'website_studio',
        'theme_treehouse',
    ],
    'data': [
        'data/account_analytic_plan.xml',
        'data/ir_model.xml',
        'data/ir_model_fields.xml',
        'data/ir_model_2.xml',
        'data/crm_stages.xml',
        'data/res_config_setting.xml',
        'data/ir_attachment_pre.xml',
        'data/product_product.xml',
        'data/sale_order_template.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/ir_attachment_post.xml',
        'data/ir_model_access.xml',
        'data/ir_rule.xml',
        'data/base_automation.xml',
        'data/ir_actions_server.xml',
        'data/website_controller_page.xml',
        'data/ir_ui_views.xml',
        'data/ir_actions_act_window.xml',
        'data/menu_item.xml',
        'data/ir_filters.xml',
        'data/x_meters.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/account_tags.xml',
        'demo/account_analytic_account.xml',
        'demo/ir_attachment.xml',
        'demo/website.xml',
        'demo/res_partner.xml',
        'demo/crm_tag.xml',
        'demo/crm_lead.xml',
        'demo/crm_lead_action.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_confirm.xml',
        'demo/account_move.xml',
        'demo/account_move_line.xml',
        'demo/website_attachment.xml',
        'demo/website_view.xml',
        'demo/website_page.xml',
        'demo/website_menu.xml',
        'demo/website_theme_apply.xml',
    ],
    'license': 'OPL-1',
    'assets': {
        'web.assets_backend': [
            'industry_real_estate/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "data/website_controller_page.xml",
        "static/src/js/my_tour.js",
        "demo/website_view.xml",
    ],
    'images': ['images/main.png'],
}

{
    'name': 'Corporate Gifts',
    'version': '1.0',
    'category': 'Supply Chain',
    'description': """
This module is for marketing companies selling and producing customized corporate gifts, like mugs and t-shirts.
""",
    'depends': [
        'base_automation',
        'crm_enterprise',
        'crm_iap_enrich',
        'crm_iap_mine',
        'documents_hr',
        'documents_product',
        'documents_project_sale',
        'documents_spreadsheet',
        'knowledge',
        'project_enterprise',
        'purchase_product_matrix',
        'purchase_stock',
        'sale_crm',
        'sale_planning',
        'sale_product_matrix',
        'sale_purchase',
        'web_studio',
        'website_crm',
        'website_sale_stock',
        'theme_enark',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/ir_attachment_pre.xml',
        'data/mail_template.xml',
        'data/product_public_category.xml',
        'data/project_task_type.xml',
        'data/documents_folder.xml',
        'data/project_project.xml',
        'data/base_automation.xml',
        'data/ir_actions_server.xml',
        'data/planning_role.xml',
        'data/product_template.xml',
        'data/product_attribute.xml',
        'data/product_attribute_value.xml',
        'data/product_template_attribute_line.xml',
        'data/product_template_attribute_value.xml',
        'data/product_product.xml',
        'data/product_image.xml',
        'data/sale_order_template.xml',
        'data/sale_order_template_line.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/ir_attachment_post.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/website.xml',
        'demo/res_partner.xml',
        'demo/hr_employee.xml',
        'demo/crm_tag.xml',
        'demo/crm_lead.xml',
        'demo/product_template.xml',
        'demo/product_supplierinfo.xml',
        'demo/website_ir_attachment.xml',
        'demo/website_view.xml',
        'demo/website_page.xml',
        'demo/website_menu.xml',
        'demo/website_theme_apply.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_confirm.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_confirm.xml',
        'demo/planning_slot_template.xml',
        'demo/planning_slot.xml',
        'demo/ir_attachment_post.xml',
        'demo/payment_provider_demo_post.xml',
    ],
    'license': 'OPL-1',
    'assets': {
        'web.assets_backend': [
            'corporate_gifts/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
        "demo/website_view.xml",
    ],
    'images': ['images/main.png'],
}

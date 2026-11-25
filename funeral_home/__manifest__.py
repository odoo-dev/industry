{
    'name': 'Funeral Home',
    'category': 'Services',
    'depends': [
        'base_automation',
        'base_industry_data',
        'contacts',
        'sale_management',
        'web_studio',
    ],
    'data': [
        # same in every country.
        'data/ir_module_module_dependency.xml',
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/product_template.xml',
        'data/ir_actions_server.xml',
        'data/base_automation.xml',
        # active only for companies whose country is Belgium.
        'data/l10n/be/ir_ui_view.xml',
        'data/l10n/be/ir_actions_report.xml',
        'data/l10n/be/ir_actions_server.xml',
        'data/country_content_sync.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
    ],
    'demo': [
        'demo/res_company.xml',
        'demo/res_partner.xml',
        'demo/sale_order.xml',
    ],
    'license': 'OEEL-1',
    'author': 'Odoo S.A.',
    'cloc_exclude': [
        'data/country_content_sync.xml',
        'data/knowledge_article.xml',
        'data/l10n/be/ir_ui_view.xml',
    ],
    'application': True,
    'images': ['images/main.png'],
    'url': 'https://www.odoo.com/trial?industry&selected_app=funeral_home',
    'website': 'https://www.odoo.com/all-industries',
}

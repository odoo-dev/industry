{
    'name': 'Booking Channex',
    'author': 'Odoo S.A.',
    'category': 'Hospitality',
    'depends': [
        'booking_engine',
    ],
    'data': [
        'data/ir_model.xml',
        'data/ir_access.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_model_fields.xml',
        'data/ir_actions_server.xml',
        'data/res_config_settings.xml',
        'data/ir_default.xml',
        'data/base_automation.xml',
        'data/ir_cron.xml',
        'data/x_channex_group.xml',
        'data/ir_ui_view.xml',
        'data/ir_ui_menu.xml',
    ],
    'demo': [
        'demo/res_company.xml',
    ],
    'license': 'OEEL-1',
    'cloc_exclude': [
        'data/knowledge_article.xml',
    ],
}

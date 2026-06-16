{
    'name': 'Hotel Industry Website',
    'description': 'Custom website module for Hotel industry',
    'version': '19.0.1.0.0',
    'author': 'Odoo S.A.',
    'license': 'OEEL-1',
    'depends': [
        'website',
        'website_sale',
        'website_sale_renting',
        'product',
        'delivery',
    ],
    'data': [
        'data/website.xml',
        'data/server_actions.xml',
        'data/assets.xml',
        'data/images.xml',
        'data/menu.xml',
        'data/pages/contactus.xml',
        'data/pages/home.xml',
        'views/website_templates.xml',
    ],
    'cloc_exclude': [
        'views/website_templates.xml',
        'views/website_sale_templates.xml',
    ],
}

{
    'name': 'Vineyard Website',
    'description': 'Custom website module exported from Odoo Website Builder',
    'version': '19.0.1.0.0',
    'author': 'Odoo',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_sale',
        'website_sale_comparison',
        'website_sale_wishlist',
    ],
    'data': [
        'data/images.xml',
        'data/presets.xml',
        'data/website.xml',
        'data/pages/home.xml',
        'data/pages/contactus.xml',
        'data/menu.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'website_vineyard/static/src/scss/primary_variables.scss',
        ],
    },
    'color-palettes-name': 'vineyard',
}

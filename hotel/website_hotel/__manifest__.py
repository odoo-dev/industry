{
    'name': 'Custom Website Hotel',
    'description': 'Custom website module exported from Odoo Website Builder',
    'version': '19.0.1.0.0',
    'author': 'PSBE Designers',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_sale',
    ],
    'data': [
        'data/images.xml',
        'data/presets.xml',
        'data/website.xml',
        'data/pages/contactus.xml',
        'data/pages/home.xml',
        'data/menu.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'website_hotel/static/src/scss/primary_variables.scss',
        ],
    },
    'color-palettes-name': 'hotel',
}

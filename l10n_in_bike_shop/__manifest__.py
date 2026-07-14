{
    "name": "Indian Localization for Bike Shop",
    "version": "1.0",
    "depends": ['l10n_in', 'bike_shop'],
    "author": "Odoo S.A.",
    "category": "Localization",
    "description": """
        Bridge module to adapt Bike Shop industry module
        for Indian localization (GST, taxes, accounts).
    """,
    "data": [
        'data/pos_confirm.xml',
        'data/res_company.xml',
    ],
    'auto_install': ['l10n_in', 'bike_shop'],
}

# -*- coding: utf-8 -*-
"""Post-init hook: presets, theme vars, pages, menus (identique import ZIP)."""

def post_init_hook(env):
    env["website_hotel.post_import"].run_post_import(
        "website_hotel",
        preset_keys_json='["website_sale.carousel_product_indicators_bottom", "website_sale.cta_wrapper_boxed", "website_sale.floating_bar", "website_sale.sidebar_dropzone_at_bottom", "website_sale.sidebar_dropzone_at_top", "website.header_call_to_action_large", "website.header_call_to_action_sidebar", "website.header_call_to_action_stretched", "website.template_footer_minimalist"]',
        theme_vars_json='{"footer-template": "minimalist"}',
    )

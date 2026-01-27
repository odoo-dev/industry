# -*- coding: utf-8 -*-
"""Post-import: base views, fragile, presets, theme vars, pages, menus."""
import json
import logging
from collections import defaultdict

from odoo import api, models

_logger = logging.getLogger(__name__)

DEFAULT_VIEW_KEYS = ("website.homepage", "website.contactus")
FRAGILE_VIEW_KEYS_TO_DEACTIVATE = ("website.footer_copyright_company_name",)


class PostImport(models.AbstractModel):
    _name = "website_hotel.post_import"
    _description = "Post-import"

    @api.model
    def run_post_import(self, mod_name, preset_keys_json="[]", theme_vars_json="{}"):
        preset_keys = json.loads(preset_keys_json) if isinstance(preset_keys_json, str) else (preset_keys_json or [])
        theme_vars = json.loads(theme_vars_json) if isinstance(theme_vars_json, str) else (theme_vars_json or {})
        View = self.env["ir.ui.view"].with_context(active_test=False)

        # 1. Disable default homepage/contactus views
        for xmlid in DEFAULT_VIEW_KEYS:
            try:
                v = self.env.ref(xmlid, raise_if_not_found=False)
                if v and v.exists():
                    v.write({"active": False})
            except Exception:
                pass

        # 2. Deactivate fragile footer views
        for key in FRAGILE_VIEW_KEYS_TO_DEACTIVATE:
            try:
                views = View.search([("key", "=", key), ("active", "=", True)])
                if views:
                    views.write({"active": False})
            except Exception:
                pass

        # 3. Activate presets + set theme vars
        Website = self.env["website"]
        Assets = self.env["website.assets"]
        for website in Website.search([]):
            header_val = None
            footer_val = None
            for key in preset_keys:
                v = View.search(
                    [("key", "=", key), ("website_id", "in", [False, website.id])],
                    limit=1,
                )
                if v:
                    try:
                        v.with_context(website_id=website.id).write({"active": True})
                    except Exception as e:
                        _logger.warning("Activate %s: %s", key, e)
                if key.startswith("website.template_header_") and key != "website.template_header_default":
                    header_val = key.replace("website.template_header_", "", 1)
                if key.startswith("website.template_footer_") and key != "website.template_footer_default":
                    footer_val = key.replace("website.template_footer_", "", 1)
            vars_apply = dict(theme_vars)
            if header_val:
                vars_apply["header-template"] = header_val
            if footer_val:
                vars_apply["footer-template"] = footer_val
            if vars_apply:
                try:
                    Assets.with_context(website_id=website.id).make_scss_customization(
                        "/website/static/src/scss/options/user_values.scss",
                        {k: repr(v) for k, v in vars_apply.items()},
                    )
                except Exception as e:
                    _logger.warning("Theme vars: %s", e)
            # Disable defaults when custom preset active
            if any(k.startswith("website.template_header_") and k != "website.template_header_default" for k in preset_keys):
                def_h = View.search([("key", "=", "website.template_header_default"), ("website_id", "in", [False, website.id])], limit=1)
                if def_h:
                    try:
                        def_h.write({"active": False})
                    except Exception:
                        pass
            if any(k.startswith("website.template_footer_") for k in preset_keys):
                def_f = View.search([("key", "=", "website.footer_custom"), ("website_id", "in", [False, website.id])], limit=1)
                if def_f:
                    try:
                        def_f.write({"active": False})
                    except Exception:
                        pass

        # 4. Remove default pages
        Imd = self.env["ir.model.data"]
        for mod, name in [("website", "homepage_page"), ("website", "contactus_page")]:
            rec = Imd.search([("module", "=", mod), ("name", "=", name), ("model", "=", "website.page")], limit=1)
            if rec and rec.res_id:
                page = self.env["website.page"].browse(rec.res_id)
                if page.exists():
                    try:
                        page.unlink()
                    except Exception:
                        pass

        # 5. Dedupe menus
        Menu = self.env["website.menu"]
        our_ids = set(Imd.search([("module", "=", mod_name), ("model", "=", "website.menu")]).mapped("res_id"))
        for website in Website.search([]):
            menus = Menu.search([("website_id", "=", website.id), ("parent_id", "!=", False)])
            by_url = defaultdict(list)
            for m in menus:
                url = (m.url or "#").strip()
                canonical = "/contactus" if url in ("/contactus", "/contact-us") else url
                by_url[canonical].append(m)
            for url, group in by_url.items():
                if len(group) <= 1:
                    continue
                keep = next((x for x in group if x.id in our_ids), group[0])
                to_remove = [m for m in group if m != keep]
                for m in to_remove:
                    try:
                        m.unlink()
                    except Exception:
                        pass
        self.env.registry.clear_cache()
        _logger.info("run_post_import done: %s", mod_name)

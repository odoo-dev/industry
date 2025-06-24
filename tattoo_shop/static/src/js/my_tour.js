/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
var core = require('web.core');
var _lt = core._lt;

registry.category("web_tour.tours").add("tattoo_shop_knowledge_tour", {
    url: "/odoo",
    
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="knowledge.knowledge_menu_root"]',
            content: _lt("Get on track and explore our recommendations for your Odoo usage here!"),
            run: "click",
        },
    ],
});

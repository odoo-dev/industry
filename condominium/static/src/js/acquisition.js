import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("Condominium_Acquisition", {
    url: "/odoo",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='sale\\.sale_menu_root']",
        "content": "Open the Sales app to create the quotation",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "content": "Create a new quotation",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='partner_id'] .o-autocomplete--input",
        "content": "Create and edit the condominium",
        "run": "edit New condo"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(2) > a",
        "run": "click"
    },
    {
        "trigger": ".o_radio_item:nth-child(2) > .o_form_label",
        "content": "Set the condominium as company",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='email'] .o_input",
        "content": "Set the email address of the responisible",
        "run": "edit john@sgsmg.com"
    },
    {
        "trigger": ".o_form_buttons_edit > .o_form_button_save",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='sale_order_template_id'] .o-autocomplete--input",
        "content": "Select the right quotation template",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_quotation_send']",
        "content": "Send the quotation",
        "run": "click"
    },
    {
        "trigger": ".o_mail_send[name='action_send_mail']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_confirm']",
        "content": "If the quote is accepted, confirm it",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='\\35 51']",
        "content": "Invoice the condominium",
        "run": "click"
    },
    {
        "trigger": ".o_technical_modal button[name='create_invoices']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_post']",
        "content": "Check the invoice and post it",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='partner_id'] > .o_form_uri",
        "content": "Open the customer to create the condominium setup",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='\\36 90']",
        "content": "Convert it as condominium",
        "run": "click"
    },
    {
        "trigger": ".o_switch_company_menu > .o-dropdown",
        "content": "The condominium is created as a new company where you will be able to manage it",
        "run": "click"
    }
]
})

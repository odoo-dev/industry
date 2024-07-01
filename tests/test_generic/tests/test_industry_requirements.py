# Part of Odoo. See LICENSE file for full copyright and licensing details.

import sys
import os
from odoo.tests.common import tagged
from odoo.tools import cloc, file_open
from .industry_case import IndustryCase, get_industry_path
import json
import textwrap


@tagged('post_install', '-at_install')
class TestEnv(IndustryCase):

    def test_payment_demo(self):
        if self.env['ir.module.module']._get('payment_demo').state != 'installed':
            return
        demo_provider = self.env.ref('payment.payment_provider_demo')
        sys_args = sys.argv
        index_database = sys_args.index('-d')
        if sys_args[index_database + 1].endswith('imported_no_demo'):
            self.assertEqual(
                demo_provider.state, 'disabled', "Payment provider demo should be disabled in data"
            )
            self.assertFalse(
                demo_provider.is_published, "Payment provider demo should be unpublished in data"
            )
        elif sys_args[index_database + 1].endswith('imported_with_demo'):
            self.assertEqual(
                demo_provider.state,
                'test',
                "Payment provider demo should be enabled (test) in demo",
            )
            self.assertTrue(
                demo_provider.is_published, "Payment provider demo should be published in demo"
            )

    def test_dependencies(self):
        installed_apps = (
            self.env["ir.module.module"]
            .search([("state", "=", "installed"), ("application", "=", True)])
            .mapped('name')
        )

        base_path = get_industry_path()
        template_path = f"{base_path}tests/test_generic/tests/templater.json"

        try:
            with file_open(template_path, mode='r') as file:
                templates = json.load(file)
        except Exception as e:
            print(f"Error loading templater.json: {e}")
            return

        knowledge_article_path = (
            f"{base_path}/{self.installed_modules[0]}/data/knowledge_article.xml"
        )
        favorite_article_path = (
            f"{base_path}/{self.installed_modules[0]}/data/knowledge_article_favorite.xml"
        )

        try:
            if os.path.exists(knowledge_article_path):
                with file_open(knowledge_article_path, 'r') as file:
                    knowledge_content = file.read()
            else:
                print(f"Warning: knowledge_article.xml not found")
                return

            if os.path.exists(favorite_article_path):
                with file_open(favorite_article_path, 'r') as file:
                    favorite_content = file.read()
            else:
                print(f"Warning: knowledge_favorite_article.xml not found")
                return
        except Exception as e:
            print(f"Error opening files: {e}")
            return

        for app_name in installed_apps:
            try:
                if f'id="article_{app_name}"' not in knowledge_content:
                    body_content = templates.get(app_name, "")
                    new_article = f"""
                    <record id="article_{app_name}" model="knowledge.article">
                        <field name="name">{app_name}</field>
                        <field name="category">workspace</field>
                        <field name="is_article_visible_by_everyone" eval="True"/>
                        <field name="body">{body_content}</field>
                    </record>
                    """
                    knowledge_content = knowledge_content.replace(
                        '</odoo>', f'{textwrap.dedent(new_article)}</odoo>'
                    )

                if f'id="knowledge_favorite_{app_name}"' not in favorite_content:
                    favorite_record = f"""
                    <record id="knowledge_favorite_{app_name}" model="knowledge.article.favorite">
                        <field name="article_id" ref="article_{app_name}"/>
                        <field name="user_id" ref="base.user_admin"/>
                    </record>
                    """
                    favorite_content = favorite_content.replace(
                        '</odoo>', f'{textwrap.dedent(favorite_record)}</odoo>'
                    )

            except Exception as e:
                print(f"Error processing module '{app_name}': {e}")

        try:
            with open(knowledge_article_path, 'w', encoding='utf-8') as file:
                file.write(knowledge_content)
            with open(favorite_article_path, 'w', encoding='utf-8') as file:
                file.write(favorite_content)
        except Exception as e:
            print(f"Error writing files: {e}")

    def test_knowledge_article_notification(self):
        for module in self.installed_modules:
            ref = self.env.ref(module + '.notification_knowledge', raise_if_not_found=False)
            self.assertTrue(
                ref, "You forgot to define a `mail.message` with `id=notification_knowledge`."
            )
            notif = self.env['mail.message'].browse(ref.id)
            self.assertIn(
                '<a href="/knowledge/article/',
                notif.body,
                "The notification should contain a link to the knowledge article.",
            )
            knowledge = self.env['ir.model.data'].search(
                [('model', '=', 'knowledge.article'), ('module', '=', module)], limit=1
            )
            self.assertTrue(knowledge, "Missing knowledge article for the industry module.")
            knowledge_article = self.env.ref(knowledge.complete_name)
            self.assertNotEqual(
                knowledge_article.favorite_count,
                0,
                "The knowledge article should be in the favorite category",
            )
            self.assertIn(
                'href="/knowledge/article/%s' % knowledge_article.id,
                notif.body,
                "The notification link should target the module-related knowledge article.",
            )

    def test_cloc_exclude_view(self):
        if not sys.argv[sys.argv.index('-d') + 1].endswith('imported_no_demo'):
            return
        c = cloc.Cloc()
        c.count_database(self.env.cr.dbname)
        c.report(True)  # show details of cloc in the logs
        for module in self.installed_modules:
            for cloc_entry in c.modules.get(module, {}):
                message = "The view '%s' is counted in the maintenance lines. " % cloc_entry
                message += "Please add a '__cloc_exclude__' entry in 'ir_model_data'."
                self.assertEqual(len(cloc_entry.split(':')), 2, message)

    def test_sale_ok_and_is_published_in_db(self):
        models = ["product.template", "product.product"]
        for model in models:
            if "is_published" in self.env[model]._fields:
                records = self.env[model].search(
                    [("is_published", "=", True), ("sale_ok", "=", False)]
                )

                self.assertFalse(
                    records,
                    "Found records with 'is_published=True' and 'sale_ok=False' in the database. Records: %s"
                    % ", ".join(
                        ["%s (ID: %s)" % (record.display_name, record.id) for record in records],
                    ),
                )

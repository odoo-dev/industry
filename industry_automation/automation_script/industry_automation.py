#!/usr/bin/env python3
"""
./industry_automation.py   --module_name="veterinary"  --db_version="saas~18.1"   --category="design"   --dump_path="/home/odoo/Documents/DUMB DB/veterinary-industry.dump.zip"   --destination_path="/home/odoo/Pictures/custom_modules"  --master_password="wnqj-csb3-w822"
"""

import zipfile
import os
import tempfile
import requests
import logging
import socket
import shutil
import argparse
import sys

from pathlib import Path
import re
from ast import literal_eval
from lxml import etree

# Setup logger
# Create a Logger instance directly
_logger = logging.Logger("logging")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
_logger.addHandler(handler)

 # Map DB version to fixed port
VERSION_PORT_MAP = {
    'saas~18.1': 10001,
    'saas~18.2': 10002,
}
BASE_URL = "http://localhost:"
LOGIN = "admin"
PASSWORD = "admin" 

# ====================================================
#              Export logic             
# ====================================================

class ProcessDb:
    def __init__(self, module_name, db_version, category, dump_path, destination_path, master_password):
        self.module_name = module_name
        self.db_version = db_version
        self.category = category
        self.dump_path = dump_path
        self.destination_path = destination_path
        self.master_password = master_password

    def process_dump_task(self):
        try:
            # Setup destination path
            self.destination_path = os.path.join(self.destination_path, self.module_name)

            # 2. Get the DB version (first two parts of semantic versioning, e.g., 16.0)
            port = self.get_port_for_version()

            # Check if the appropriate Odoo server is running on the correct port
            if not self.is_port_open("localhost" , port):
                _logger.error(f"No server is running on port {port} for DB version {self.db_version}.")
                raise Exception(f"No server is running on port {port} for DB version {self.db_version}.")
            _logger.info(f"Server found on port {port} for DB version {self.db_version}.")

            # 3. Restore the DB using the dump file on the found port
            restore_db_name = f"{self.module_name}_db"
            success = self.restore_db(port, restore_db_name)
            if not success:
                _logger.error(f"Database '{restore_db_name}' Failed to restore  on port {port}.")
                raise Exception(f"Database '{restore_db_name}' Failed to restore  on port {port}.")
            _logger.info(f"Database '{restore_db_name}' restored successfully on port {port}.")

            # 5. Prepare a temporary base directory for exporting and modifying files
            base_temp_dir = os.path.join(tempfile.gettempdir(), self.module_name)
            os.makedirs(base_temp_dir, exist_ok=True)

            # 6. Export the Studio customizations into a zip file
            studio_zip_path = f"{base_temp_dir}/studio_customization.zip"
            self.export_studio_customizations(port, restore_db_name, studio_zip_path)

            # 7. Extract the studio zip for cleaning up
            with zipfile.ZipFile(studio_zip_path, "r") as zip_ref:
                zip_ref.extractall(self.destination_path)

            # 8. Run the external cleanup script to refactor the module
            studio_extract_path = f"{self.destination_path}/studio_customization"

            try:
                cleanModuleObj = CleanModule(self.module_name, self.category, restore_db_name, studio_extract_path, port, self.destination_path)
                cleanModuleObj.clean()
                _logger.info("Module Clean Up successful")
            except Exception as e:
                raise Exception("Error while Running CleanUp Script", str(e))
            
            # delete temp directory
            self.delete_temp_dir(base_temp_dir)

            # drop restore DB
            self.drop_db(restore_db_name, port)

            
        except Exception as e:
           raise Exception(str(e))
  
    def get_port_for_version(self):
        # Look up the port number mapped to the given DB version
        port = VERSION_PORT_MAP.get(self.db_version)

        # Raise an error if no port is found for the version
        if not port:
            _logger.error(f"No port mapped for DB version {self.db_version}")
            raise Exception(f"No port mapped for DB version {self.db_version}")
        return port
    
    def is_port_open(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if a TCP port is open on the given host."""
        
        # Create a TCP socket using IPv4
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Set the timeout for the connection attempt
            sock.settimeout(timeout)
            try:
                # Attempt to connect to the specified host and port
                sock.connect((host, port))
                return True
            except (socket.timeout, ConnectionRefusedError):
                # Return False if the connection times out or is refused
                return False

    def restore_db(self, port, db_name):
        """
        Restores the database from the given ZIP file to the Odoo server running on the specified port.

        Args:
            port (int): The port number of the Odoo server where the DB should be restored.
            db_name (str): The name to assign to the restored database.
            temp_zip_file_path (str): Path to the ZIP file containing the DB dump.

        Returns:
            bool: True if the database is restored and credentials are reset, False otherwise.
        """
        try:
            # Open the ZIP file containing the database dump
            with open(self.dump_path, 'rb') as backup_file:
                # Send POST request to Odoo's database restore endpoint
                response = requests.post(
                    f'{BASE_URL}{port}/web/database/restore',
                    data={
                        'master_pwd': self.master_password,  # Master admin password
                        'name': db_name,                # Target DB name
                        'copy': True                    # Indicate it's a copy
                    },
                    files={
                        'backup_file': ('industry_module.zip', backup_file, 'application/zip')
                    }
                )

            # Check if the restore was successful (HTTP 200 OK or 302 Found)
            if response.status_code in (200, 302):
                # Reset login credentials for user ID 2
                os.system(f"psql {db_name} -c \"UPDATE res_users SET login='{LOGIN}', password='{PASSWORD}' WHERE id=2;\"")
                return True
            else:
                return False

        except Exception:
            raise Exception("Database Can't be Restore")

    def drop_db(self, db_name, port):
        response = requests.post(
            f'{BASE_URL}{port}/web/database/drop',
            data={
                'master_pwd': self.master_password,  # Master admin password
                'name': db_name,
            },
        )
        response.raise_for_status()

    def export_studio_customizations(self, port, db_name, studio_zip_path):
        try:
            session = requests.Session()
            # Step 1: Authenticate via /web/session/authenticate (sets session cookie)
            auth_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "db": db_name,
                    "login": LOGIN,
                    "password": PASSWORD,
                },
                "id": 1
            }
            response = session.post(f"{BASE_URL}{port}/web/session/authenticate", json=auth_payload)
            response.raise_for_status()

            # Parse login result
            result = response.json().get("result")
            if not result or not result.get("uid"):
                _logger.error("Authentication Failed")
                raise Exception("Login failed.")
            uid = result["uid"]
            _logger.info("Authentication Successful")

            # Step 2: Ensure web_studio is installed
            modules = self.check_web_studio_installed(port, db_name, uid)
            if modules:
                state = modules[0]['state']
                model_id = modules[0]['id']
                if state == "uninstalled":
                    self.install_web_studio(port, db_name, uid, model_id)
            else:
                _logger.error("web_studio module not found in registry.")
                raise Exception("web_studio module not found in registry.")

            # Step 3: Call action_preset on studio.export.model
            preset_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        db_name,
                        uid,
                        PASSWORD,
                        "studio.export.model",
                        "action_preset",
                        [{}],
                    ]
                },
                "id": 2
            }
            preset_resp = session.post(f"{BASE_URL}{port}/jsonrpc", json=preset_payload)
            preset_resp.raise_for_status()

            # Step 4: Create export wizard via RPC
            wizard_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                                db_name,
                                uid,
                                PASSWORD,
                                "studio.export.wizard",
                                "create",
                                [{
                                    "include_additional_data": True,
                                    "include_demo_data": True
                                }]
                            ]
                },
                "id": 3
            }

            wizard_resp = session.post(f"{BASE_URL}{port}/jsonrpc", json=wizard_payload)
            
            wizard_resp.raise_for_status()
            
            if not wizard_resp.json()["result"]:
                _logger.error("Export Wizard Failed to Create")
                raise Exception("wizard id not found")
            wizard_id = wizard_resp.json()["result"]

            # Step 5: Call the export route (no token needed, session is authenticated)
            export_url = f"{BASE_URL}{port}/web_studio/export?active_id={wizard_id}&token=dummytoken"
            export_resp = session.get(export_url, stream=True)
            

            if export_resp.status_code == 200 and export_resp.headers['Content-Type'] == 'application/zip':
                with open(studio_zip_path, "wb") as f:
                    f.write(export_resp.content)
            else:
                _logger.error(f" Export failed: {export_resp.status_code} - {export_resp.text}")
                raise Exception(f" Export failed: {export_resp.status_code} - {export_resp.text}")
            
        except Exception as e:
            _logger.error("studio_customization Failed to Export")
            raise Exception(str(e))
    
    def delete_temp_dir(self, dir_path):
        """
        Deletes a temporary directory and all its contents.
        
        :param dir_path: Full path to the directory.
        """
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)

    def check_web_studio_installed(self, port, db_name, uid):
        # Prepare the JSON-RPC payload to search for the 'web_studio' module
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db_name, uid, PASSWORD,
                    "ir.module.module", "search_read",
                    [[["name", "=", "web_studio"]]],
                    {"fields": ["state"], "limit": 1}
                ]
            },
            "id": 2
        }

        # Send the request to the server and parse the JSON response
        response = requests.post(f"{BASE_URL}{port}/jsonrpc", json=payload).json()
        
        # Return the list of matched module(s) with their state
        if response["result"]:
            return response["result"]
        
    def install_web_studio(self, port, db_name, uid, module_id):
        # Prepare JSON-RPC payload to install the module using button_immediate_install
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db_name, uid, PASSWORD,
                    "ir.module.module", "button_immediate_install",
                    [module_id]
                ]
            },
            "id": 4
        }

        # Send request to install the module
        install_response = requests.post(f"{BASE_URL}{port}/jsonrpc", json=payload).json()

        # Log error if installation failed
        if not install_response["result"]:
            _logger.error("Module Studio can't install")
        return install_response["result"]


# ====================================================
#              CleanUp logic             
# ====================================================


class CleanModule:
    def __init__(self, ind_name, ind_category, db_name, module_path, port, destination_base_path):
        self.ind_name = ind_name
        self.ind_category = ind_category
        self.db_name = db_name
        self.module_path = module_path
        self.port = port
        self.destination_base_path = destination_base_path
        self.automated = {
            'author': 'Odoo S.A.',
            'category': '',
            'images': ['images/main.png'],
            'license': 'OPL-1',
            'version': '1.0',
        }
        self.mandatory_files = {
            "/static/src/js/my_tour.js": """import {{ _t }} from "@web/core/l10n/translation";
import {{ registry }} from "@web/core/registry";

registry.category("web_tour.tours").add("{ind_name}_knowledge_tour", {{
    url: "/odoo",
    steps: () => [
        {{
            trigger: '.o_app[data-menu-xmlid="knowledge.knowledge_menu_root"]',
            content: _t("Get on track and explore our recommendations for your Odoo usage here!"),
            run: "click",
        }},
    ],
}});
""",
            "/data/mail_message.xml": """<?xml version='1.0' encoding='UTF-8'?>
<odoo noupdate="1">
    <record model="mail.message" id="notification_knowledge">
        <field name="model">discuss.channel</field>
        <field name="res_id" ref="mail.channel_all_employees"/>
        <field name="message_type">email</field>
        <field name="author_id" ref="base.partner_root"/>
        <field name="subtype_id" ref="mail.mt_comment"/>
        <field name="subject">🚀 Get started with Odoo {Ind_name} Shop</field>
        <field name="body" model="knowledge.article" eval="
            '&lt;span>&#x1F44B; Hi! Follow this &lt;a href=\\''
             + obj().env.ref('{ind_name}.welcome_article').article_url 
             + '\\'>onboarding guide&lt;/a>. You can find it anytime in the Knowledge app.&lt;/span>'"/>
    </record>
</odoo>
""",
            "/data/knowledge_article_favorite.xml": """<?xml version='1.0' encoding='UTF-8'?>
<odoo noupdate="1">
    <record id="knowledge_favorite" model="knowledge.article.favorite">
        <field name="article_id" ref="welcome_article"/>
        <field name="user_id" ref="base.user_admin"/>
    </record>
</odoo>
""",
            "/data/knowledge_tour.xml": """<?xml version="1.0" encoding="UTF-8"?>
<odoo noupdate="1">
    <record id="knowledge_tour" model="web_tour.tour">
        <field name="name">{ind_name}_knowledge_tour</field>
        <field name="sequence">2</field>
        <field name="rainbow_man_message">Welcome! Happy exploring.</field>
    </record>
</odoo>
""",
}

    def clean(self):
        # Format the industry name and category by replacing underscores/hyphens with spaces and capitalizing
        Ind_name = re.sub(r'[_-]', ' ', self.ind_name).title()
        Ind_category = re.sub(r'[_-]', ' ', self.ind_category).title()
        self.automated['category'] = Ind_category

        # Construct the destination path for the cleaned module
        destination_module_path = self.destination_base_path + '/' + self.ind_name
        directory = self.module_path

        # Fetch field metadata of fields
        fields_info_dict = {}

        scss_content_list = []
        manifest_demo_file_list = []

        # Traverse the module directory recursively
        for root, dirs, files in os.walk(directory):
            current_dir = root.split(directory)[1] + '/'
            
            # Recreate directory structure at the destination
            for d in dirs:
                os.makedirs(destination_module_path + current_dir + d, exist_ok=True)
            for file_name in files:
                ext = file_name.rsplit('.')[1] if '.' in file_name else ''

                # Process XML files
                if ext == 'xml':
                    content = Path(root + '/' + file_name).read_text(encoding="utf-8")
                    
                    # Apply module-specific modifications to XML content
                    content = self.edit_xml_content(content)

                    # Remove predefined unwanted fields from the XML
                    unwanted_fields = ['color', 'inherited_permission', 'access_token', 'document_token', 'peppol_verification_state', 'uuid']
                    content = self.remove_unwanted_fields(content, unwanted_fields)

                    # Remove sequence field and add auto_sequence = "1" in <odoo>
                    content = self.process_sequence_field(content)

                    xml_root = etree.fromstring(content.encode("utf-8"))
                    
                    # Collect reference names from the XML records
                    ref_name_list = list(set([
                        field.get('ref')
                        for record in xml_root.xpath("//record")
                        for field in record
                        if field.get('ref') and '.' not in field.get('ref')
                    ]))

                    # Store metadata of demo files without records for later use
                    if current_dir.endswith('/demo/') and not xml_root.xpath("//record"):
                        manifest_demo_file_dict = {
                            'file_name': file_name,
                            'ref_name': ref_name_list
                        }
                        manifest_demo_file_list.append(manifest_demo_file_dict)

                    for record in xml_root.xpath("//record"):
                        
                        # Store metadata of demo files with records for later use
                        self.unorder_manifest_demo_files(manifest_demo_file_list, current_dir, file_name, ref_name_list, record)
                        
                        model_name = record.get('model')
                        if not model_name:
                            continue
                        
                        # Remove fields based on model-specific rules
                        content = self.remove_model_based_fields(model_name, content)

                        # Clean computed fields without inverse methods
                        content = self.remove_computed_fields(fields_info_dict, model_name, record, content)
                    
                    # Special case handling for certain XML files
                    if file_name == 'ir_default.xml':
                        content = re.sub(r"<odoo>", '<odoo noupdate="1">', content)

                    if file_name == "knowledge_article.xml":
                        content = re.sub('<odoo noupdate="1">', '<odoo>', content)
                    
                    # Write the processed XML content to the destination
                    Path(destination_module_path + current_dir + file_name).write_text(content, encoding='utf-8')

                # Handle manifest file separately
                elif ext in ['py', 'txt']:
                    if file_name != '__manifest__.py':
                        continue
                    manifest = literal_eval(Path(root + '/' + file_name).read_text(encoding="utf-8"))
                    with open(destination_module_path + '/__manifest__.py', 'w', encoding="utf-8") as f:
                        f.write('{\n')
                        for k, v in manifest.items():
                            if k == 'name':
                                f.write(f"    '{k}': '{Ind_name}',\n")
                            elif k == 'description':
                                continue
                            elif k not in self.automated:
                                if isinstance(v, list):
                                    f.write(f"    '{k}': [\n")
                                    for item in v:

                                        # Skip unwanted dependencies
                                        unwanted_depends = [
                                            'base_module',
                                            '__import__',
                                            'account_invoice_extract',
                                            'account_online_synchronization',
                                            'account_peppol',
                                            'auth_totp_mail',
                                            'base_install_request',
                                            'crm_iap_enrich',
                                            'crm_iap_mine',
                                            'partner_autocomplete',
                                            'pos_epson_printer',
                                            'sale_async_emails',
                                            'snailmail_account',
                                            'web_grid',
                                            'web_studio',
                                            'social_push_notifications',
                                            'appointment_sms',
                                            'website_knowledge',
                                            'base_vat',
                                            'product_barcodelookup',
                                            'snailmail_account_followup',
                                            'base_geolocalize',
                                            'gamification',
                                            'l10n_be_pos_sale',
                                            'pos_sms',
                                            'pos_settle_due',
                                            'website_partner',
                                            'website_project',
                                            'project_sms',
                                            ]
                                        if k == 'depends' and (item in unwanted_depends or item.startswith('theme_')):
                                            continue
                                        f.write(f"        '{item}',\n")
                                    if k == 'data':
                                        f.write("        'data/mail_message.xml',\n")
                                        f.write("        'data/knowledge_article_favorite.xml',\n")
                                        f.write("        'data/knowledge_tour.xml',\n")
                                    f.write("    ],\n")
                                else:
                                    f.write(f"    '{k}': '{v}',\n")
                            else:
                                f.write(f"    '{k}': '{self.automated[k]}',\n")
                        f.write('}\n')

                # Copy other files without an extension or as specific assets
                elif not ext or (current_dir.endswith('/ir_attachment/') and ext != "scss"):
                    shutil.copy(root + '/' + file_name, destination_module_path + current_dir + file_name)

                # Extract relevant SCSS customization data
                elif current_dir.endswith('/ir_attachment/') and ext == "scss":
                    self.get_relevant_scss_data(scss_content_list, root, file_name)

        # Generate SCSS function from collected theme data
        self.write_scss_function(destination_module_path, scss_content_list)

        # Remove fields explicitly marked with ondelete=False
        self.remove_ondelete_false_field(destination_module_path)

        # Clean up specific non-user created records
        remove_file_names = ['ir_attachment_pre.xml', 'knowledge_cover.xml', 'mail_template.xml']
        for remove_file_name in remove_file_names:
            self.remove_record_not_created_by_user(destination_module_path, remove_file_name)

        # Clean up default pricelists from data files
        self.remove_default_pricelist(destination_module_path)

        # Organize records in a standard format
        self.remove_unused_ir_attachment_post(destination_module_path)
        self.order_ir_attachment_post(destination_module_path)

        # Retain only welcome article in the knowledge article
        self.clean_knowledge_article(destination_module_path)

        # Add demo payment provider if relevant module is present
        self.add_demo_payment_provider(destination_module_path, manifest_demo_file_list)
        
        # Add immediate install function for the theme module in demo XML files
        self.add_theme_immediate_install_function(destination_module_path)

        self.clean_sale_order_line_record(destination_module_path)
        # Update demo file order in manifest
        self.arrange_demo_files(destination_module_path,  manifest_demo_file_list)

        # Write mandatory files such as templates or init scripts
        for file, content in self.mandatory_files.items():
            directory, _ = os.path.split(file)
            os.makedirs(destination_module_path + directory, exist_ok=True)
            Path(destination_module_path + file).write_text(content.format(ind_name=self.ind_name, Ind_name=Ind_name), encoding='UTF-8')
    
    def get_etree_content(self, file_path):
        try:
            # Read the xml file and parse the XML string into an ElementTree object
            content = file_path.read_text(encoding='utf-8')
            etree_content = etree.fromstring(content.encode("utf-8"))
            return etree_content
        except Exception as e:
            raise Exception(f"Error while getting etree content of file ({file_path}): {e}")

    def write_etree_content(self, file_path, etree_content):
        try:
            # Convert the ElementTree content to a pretty-printed XML string
            content = etree.tostring(
                        etree_content,
                        pretty_print = True,
                        encoding="UTF-8",
                        xml_declaration = True
                    ).decode("utf-8")
            file_path.write_text(content, encoding="utf-8")

        except Exception as e:
            raise Exception(f"Error while writing etree content to file ({file_path}): {e}")

    def session_authentication(self):
        session = requests.Session()
        # Authenticates the user via Odoo's /web/session/authenticate endpoint and returns a session with an active login and the user ID.
        auth_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.db_name,
                "login": LOGIN,
                "password": PASSWORD,
            },
            "id": 1
        }
        response = session.post(f"{BASE_URL}{self.port}/web/session/authenticate", json=auth_payload)
        response.raise_for_status()
        result = response.json().get("result")
        if not result or not result.get("uid"):
            raise Exception("Login failed in script.")
        return session, result['uid']

    def get_fields_info(self, model_name):
        session, uid = self.session_authentication()

        # Retrieves metadata (model, name, store, readonly, depends) for all fields from the Odoo model using JSON-RPC.
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    self.db_name,
                    uid,
                    PASSWORD,
                    model_name,  # the model whose fields you're querying
                    "fields_get",
                    [],  # optional list of fields (empty means all)
                    {
                        "attributes": ["model", "name", "store", "readonly", "depends"]
                    }
                ]
            },
            "id": 1
        }
        
        resp = session.post(f"{BASE_URL}{self.port}/jsonrpc", json=payload)
        resp.raise_for_status()

        if not resp.json()["result"]:
            raise Exception("Error in getting model and field name")

        return resp.json()["result"]
    
    def edit_xml_content(self, content):
        # Replace references to the "studio_customization" module with the new industry module name
        env_ref = re.compile("(env\.ref\('studio_customization\.)(.*)'")
        content = env_ref.sub(lambda m: f"env.ref('{self.ind_name}.{m.group(2)}'", content)
        
        # Normalize custom field names by replacing "x_studio_" with "x_"
        x_studio = re.compile("x_studio_")
        content = x_studio.sub('x_', content)
        
        # Remove studio-specific context attribute
        context_studio = re.compile(" context=\"{'studio': True}\"")
        content = context_studio.sub('', content)
        
        # Remove the "studio_customization." prefix from field values or references
        studio_mod = re.compile("studio_customization\.")
        content = studio_mod.sub('', content)
        
        # Replace directory references from "studio_customization/" to the new module directory
        studio_link = re.compile("studio_customization/")
        content = studio_link.sub(self.ind_name + '/', content)
        
        # Remove forcecreate="1" attribute from <record> tags where the id starts with "base_module."
        pattern_base_module_forcecreate = re.compile(r'(<record\s+[^>]*id="base_module\.[^"]*"[^>]*?")\s+forcecreate="1"')
        content = pattern_base_module_forcecreate.sub(r"\1", content)
        
        # Remove "base_module." prefix from record IDs or references
        pattern_base_module = re.compile(r"base_module.")
        content = pattern_base_module.sub("", content)
        
        # Normalize user references by replacing "res_users_*" with "base.user_admin"
        pattern_res_users = re.compile("res_users_\w+")
        content = pattern_res_users.sub("base.user_admin", content)
        
        # Add the industry module prefix to ir_ui_view references in Python-style expressions
        pattern_ir_ui_view = re.compile(r"obj\(\)\.env\.ref\(\'ir_ui_view_")
        content = pattern_ir_ui_view.sub(f"obj().env.ref('{self.ind_name}.ir_ui_view_", content)
        
        # Replace default homepage key with a namespaced one under the new module
        pattern_ir_ui_view_key = re.compile(r'(<field name="key">)website.homepage(</field>)')
        content = pattern_ir_ui_view_key.sub(rf'\1{self.ind_name}.homepage\2', content)
        
        # Update subdomain links to match the industry subdomain (replace underscores with hyphens)
        pattern_href_url = re.compile(r'https://(?!www\.)([^/]+)\.odoo\.com')
        content = pattern_href_url.sub(f'https://{self.ind_name.replace("_", "-")}.odoo.com', content)
        
        # Remove full URLs in <field name="url"> when a hardcoded domain is present
        pattern_url = re.compile(r'(<field name="url">)https://[^/]+(.*?</field>)')
        content = pattern_url.sub(r'\1\2', content)
        
        # Remove any field referencing UOM (unit of measure) records to avoid data coupling
        pattern_product_uom_unit = re.compile(r'\s*<field[^>]*ref="uom.[^"]*"[^>]*\s*/>')
        content = pattern_product_uom_unit.sub('', content)
        
        # Replace any version segment in a '/documentation/{version}/' URL with '/documentation/latest/'
        pattern_documention_version_link= re.compile(r'(/documentation/)[^/]+')
        content = pattern_documention_version_link.sub(r'\1latest', content)
        
        return content

    def remove_unwanted_fields(self, content, unwanted_fields):
        """
        Removes XML field elements (both standard and self-closing) based on a list of unwanted field names.

        Args:
            content (str): The XML content as a string.
            unwanted_fields (list): A list of field names to remove from the XML.

        Returns:
            str: The cleaned XML content with unwanted fields removed.
        """
        for unwanted_field in unwanted_fields:
            pattern_regular = rf'\s*<field name="{unwanted_field}">.*?</field>'
            pattern_self_closing = rf'\s*<field name="{unwanted_field}"[^>]*\s*/>'

            content = re.sub(pattern_regular, "", content, flags=re.DOTALL)
            content = re.sub(pattern_self_closing, "", content)

        return content
    
    def process_sequence_field(self, content):
        """
            Process XML content to detect numeric 'sequence' fields and conditionally modify the root tag.

            Parses the given XML content to check for any <field name="sequence"> elements
            with numeric text values. If found, it adds the attribute `auto_sequence="1"` to
            the root <odoo> element. Also removes all 'sequence' fields from the content using
            `remove_unwanted_fields`.

            Args:
                content (str): XML content as a UTF-8 encoded string.

            Returns:
                str: Modified XML content with 'sequence' fields removed and possibly
                    updated root <odoo> tag with `auto_sequence="1"`.
        """
        etree_content = etree.fromstring(content.encode('utf-8'))
        found_numeric_sequence = False
        for record in etree_content.xpath("//record"):
            for field in record.xpath(".//field[@name='sequence']"):
                # Check if the field has a numeric value (not eval="False")
                if field.text and field.text.strip().isdigit():
                    found_numeric_sequence = True
            content = self.remove_unwanted_fields(content, ['sequence'])

        # Add auto_sequence="1" if any numeric sequence was found
        if found_numeric_sequence:
            content = re.sub(r'<odoo', '<odoo auto_sequence="1"', content)

        return content
    
    def unorder_manifest_demo_files(self, manifest_demo_file_list, current_dir, file_name, ref_name_list, record):
        """
        Inserts a demo file entry into the manifest_demo_file_list in an ordered manner.

        Logic:
        - If the record's ID appears in any ref_name of an existing entry, insert before that entry.
        - If ref_name_list is empty, insert the entry at the beginning of the list.
        - Otherwise, append the entry at the end.

        Args:
            manifest_demo_file_list (list): The current list of demo file metadata dictionaries.
            current_dir (str): The current directory being processed (used to check if in '/demo/').
            file_name (str): The name of the XML file being processed.
            ref_name_list (list): A list of references extracted from the file.
            record (etree.Element): The current <record> element from the XML.
        """

        # Only process files within the 'demo' directory
        if current_dir.endswith('/demo/'):
            # Prepare a dictionary for the current demo file and its references
            manifest_demo_file_dict = {
                'file_name': file_name,
                'ref_name': ref_name_list
            }

            # Get the ID of the current record
            file_record_id = record.get('id')
            if manifest_demo_file_dict['ref_name']:
                inserted = False

                # Try to insert before any existing file that references this record ID
                for idx, existing in enumerate(manifest_demo_file_list):
                    if file_record_id in existing['ref_name']:
                        manifest_demo_file_list.insert(idx, manifest_demo_file_dict)
                        inserted = True
                        break
                
                # If not inserted in loop, append to the end
                if not inserted:
                    manifest_demo_file_list.append(manifest_demo_file_dict)
            
            # If no references, insert at the beginning
            else:
                manifest_demo_file_list.insert(0, manifest_demo_file_dict)
        return

    def remove_model_based_fields(self, model_name, content):
        """
        Removes specific XML fields from the content based on the model name.

        Args:
            model_name (str): The technical name of the model (e.g., 'sale.order').
            content (str): The XML content as a string.

        Returns:
            str: The XML content with model-specific unwanted fields removed.
        """

        # Define a dictionary mapping models to their corresponding unwanted field names
        model_field_map = {
            'calendar.event': ['start', 'stop'],
            'crm.lead': ['email_from', 'company_id', 'country_id', 'city', 'street', 'partner_name', 'contact_name', 'zip', 'reveal_id', 'medium_id', 'date_closed', 'email_state', 'date_open', 'email_domain_criterion', 'won_status', 'street2', 'phone', 'state_id'],
            'event.event': ['kanban_state_label'],
            'hr.department': ['complete_name', 'master_department_id'],
            'pos.config': ['last_data_change'],
            'pos.order': ['date_order', 'state', 'last_order_preparation_change', 'pos_reference', 'ticket_code', 'email', 'company_id'],
            'pos.order.line': ['full_product_name', 'qty_delivered', 'price_unit', 'total_cost'],
            'pos.payment.method': ['is_cash_count'],
            'pos.session': ['name', 'start_at', 'stop_at', 'state'],
            'product.pricelist.item': ['date_start', 'date_end'],
            'product.template': ['base_unit_count'],
            'purchase.order': ['date_order', 'date_approve', 'state', 'date_planned'],
            'purchase.order.line': ['date_planned', 'name'],
            'res.partner': ['supplier_rank', 'partner_gid'],
            'sale.order': ['date_order', 'prepayment_percent', 'delivery_status', 'amount_unpaid', 'warehouse_id', 'origin'],
            'sale.order.line': ['technical_price_unit', 'warehouse_id'],
            'sale.order.template': ['prepayment_percent'],
            'sign.item': ['transaction_id'],
        }

        # Retrieve the list of unwanted fields for the given model
        unwanted_fields = model_field_map.get(model_name, [])
        
        # Remove those fields using the previously defined helper
        content = self.remove_unwanted_fields(content, unwanted_fields)

        return content

    def remove_computed_fields(self, fields_info_dict, model_name, record, content):
        # Retrieve and cache the fields information for the current model if not already done; otherwise, use the cached info
        if model_name not in fields_info_dict:
            field_info = self.get_fields_info(model_name)
            fields_info_dict[model_name] = field_info
        else:
            field_info = fields_info_dict[model_name]

        # Extract all field names defined in the given XML <record> tag
        fields_set_in_record = {
            field.get('name') for field in record.xpath('.//field')
        }

        # Iterate through each field name in the record
        for field_name in fields_set_in_record:
            field_obj = None

            field_obj = field_info.get(field_name)

            # Remove the field from the XML content if it's computed (not stored) and readonly
            if field_obj and (field_obj["depends"] and field_obj["readonly"] and not field_obj['store']):
                # Match standard field tags (e.g., <field name="foo">bar</field>)
                pattern_standard = re.compile(
                    rf'\s*<field name="{field_name}">.*?</field>',
                    re.DOTALL
                    )

                # Match self-closing field tags (e.g., <field name="foo" />)
                pattern_self_closing = re.compile(
                        rf'\s*<field name="{field_name}"[^>]*\s*/>'
                    )

                # Remove matched fields from the content
                content = pattern_standard.sub('', content)
                content = pattern_self_closing.sub('', content)

        return content

    def get_relevant_scss_data(self, scss_content_list, root, file_name):
        """
        Parses the given SCSS file to extract relevant customization data.

        This function reads the content of a specified SCSS file and searches for 
        a customization block defined by the 'o-map-omit((...))' pattern. If found, 
        it extracts the inner content and appends a dictionary containing the content 
        and a corresponding URL to the provided list.

        Parameters:
            scss_content_list (list): A list to which the extracted SCSS data dictionaries will be appended.
            root (str): The root directory path where the SCSS file is located.
            file_name (str): The name of the SCSS file to be processed.

        Returns:
            None
        """
        scss_content_dict = {}
        scss_content = Path(root + '/' + file_name).read_text(encoding="utf-8")
        
        # Extract SCSS variable customization block
        scss_pattern = re.compile(r'o-map-omit\(\(\s*(.*?)\s*\)\)', re.DOTALL)
        scss_match = scss_pattern.search(scss_content)

        if scss_match:
            inner_scss_content = scss_match.group(1)  # Extract inner contents
            scss_content_dict['inner_scss_content'] = inner_scss_content
            if 'color' in file_name:
                scss_content_dict['url'] = "/website/static/src/scss/options/colors/" + file_name
            else:
                scss_content_dict['url'] = "/website/static/src/scss/options/" + file_name

            scss_content_list.append(scss_content_dict)
        
        return

    def write_scss_function(self, destination_module_path, scss_content_list):
        """
            Generates and writes SCSS customization functions into the website_theme_apply.xml file.

            For each SCSS customization, this function generates a <function> block, embedding the SCSS 
            content and target URL. It appends these blocks to the existing XML file or creates
            a new one if it does not exist.

            Args:
                destination_module_path (str): Path to the module directory.
                scss_content_list (list): A list of dictionaries with keys 'url' and 'inner_scss_content'.
        """
        if scss_content_list:
            target_path = Path(destination_module_path + '/demo/' + 'website_theme_apply.xml')
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Build new <function> entries for each SCSS customization
            new_function = ""
            for item in scss_content_list:
                new_function += f"""
        <function model="web_editor.assets" name="make_scss_customization">
            <value eval="{item['url']}" />
            <value eval="{{'
                    {item['inner_scss_content']}'
                }}" />
        </function>
        """
            
            # Base structure if file does not exist
            base_xml = f"""<?xml version='1.0' encoding='UTF-8'?>
    <odoo>{new_function}
    </odoo>
    """
            
            # Update existing file or create new one
            if target_path.exists():
                content = target_path.read_text(encoding='utf-8')
                if "</odoo>" in content:
                    updated_content = content.replace("</odoo>", f"{new_function}\n</odoo>")
                else:
                    updated_content = content + "\n" + new_function + "\n</odoo>"
            else:
                updated_content = base_xml
            try:
                target_path.write_text(updated_content, encoding='utf-8')
            except Exception as e:
                raise Exception(f"Unable to write website_theme_apply.xml file: {e}")

        return

    def remove_ondelete_false_field(self, destination_module_path):
        """
        From ir_model_fields.xml, remove <field name="on_delete" eval="False"/> 
        if field type (ttype) is NOT 'many2one' or 'one2many'.
        Also wrap the 'compute' field text in CDATA.
        """    
        path_ir_model_fields = Path(destination_module_path + '/data/' + 'ir_model_fields.xml')
        if path_ir_model_fields.exists():
            root_ir_model_field = self.get_etree_content(path_ir_model_fields)
            records = root_ir_model_field.xpath("//record")
            for record in records:
                field_type_elem = record.xpath(".//field[@name='ttype']")
                if not field_type_elem:
                    continue
                field_type = field_type_elem[0].text.strip()
            
                # Remove on_delete fields if ttype is not many2one or one2many and on_delete eval is False
                if field_type not in ['many2one', 'one2many']:
                    for field in record.xpath(".//field[@name='on_delete']"):
                        if field.get('eval') == 'False':
                            record.remove(field)
                
                # Wrap compute field text in CDATA if exists
                for field in record.xpath(".//field[@name='compute']"):
                    original_text = field.text
                    if original_text:
                        field.text = etree.CDATA(original_text)

            self.write_etree_content(path_ir_model_fields, root_ir_model_field)

        return

    def remove_record_not_created_by_user(self, destination_module_path, file_name):
        """
        Remove XML records from the given file if their ID contains a dot ('.'),
        which indicates they are not user-created records.

        Args:
            destination_module_path (str or Path): The base path to the module directory.
            file_name (str): The XML data file name to process.

        Returns:
            None
        """
        path_file = Path(destination_module_path + '/data/' + file_name)
        if path_file.exists():
            root_file = self.get_etree_content(path_file)
            records = root_file.xpath("//record")
            for record in records:
                record_id = record.get('id')
                if '.' in record_id:
                    root_file.remove(record)
            self.write_etree_content(path_file, root_file)
        return

    def remove_default_pricelist(self, destination_module_path):
        """
        Remove records from product_pricelist.xml where the 'name' field is 'Default' or 'default'.

        Args:
            destination_module_path (str or Path): The path to the module directory.

        Returns:
            None
        """
        path_product_pricelist = Path(destination_module_path + '/data/' + 'product_pricelist.xml')
        if path_product_pricelist.exists():
            root_product_pricelist = self.get_etree_content(path_product_pricelist)
            records = root_product_pricelist.xpath("//record")
            for record in records:
                name_key = record.xpath(".//field[@name='name']")
                if name_key and (name_key[0].text == 'Default' or name_key[0].text == 'default'):
                    root_product_pricelist.remove(record)

            self.write_etree_content(path_product_pricelist, root_product_pricelist)

        return

    def remove_unused_ir_attachment_post(self, destination_module_path):
        """
        Remove unused <record> elements from 'ir_attachment_post.xml' whose 'key' or 'name' fields
        are not referenced in 'ir_ui_view.xml'. Also deletes corresponding files from disk.

        Args:
            destination_module_path (str): Module directory path.
        """

        path_ir_attachment_post = Path(destination_module_path + '/demo/' + 'ir_attachment_post.xml')
        path_ir_ui_view = Path(destination_module_path + '/demo/' + 'ir_ui_view.xml')
        
        # Only proceed if both files exist
        if path_ir_attachment_post.exists() and path_ir_ui_view.exists():
            root_ir_attachment_post = self.get_etree_content(path_ir_attachment_post)
            content_ir_ui_view = path_ir_ui_view.read_text(encoding="utf-8")
            records = root_ir_attachment_post.xpath("//record")
            unused_ir_attachment_post_ids = []
            unused_files = []
            for record in records:
                key_field = record.xpath(".//field[@name='key']")
                name_field = record.xpath(".//field[@name='name']")
                datas_field = record.xpath(".//field[@name='datas']")
                if key_field or name_field:
                    # check key or name in ir_ui_view.xml file if not found store in list
                    key = key_field[0].text if key_field else None
                    name = name_field[0].text if name_field else None
                    file_name = record.xpath(".//field[@name='datas']")[0].get('file') if datas_field else None
                    # file_name = record.xpath(".//field[@name='datas']")[0].get('file')
                    if (key and key not in content_ir_ui_view) or (name and name not in content_ir_ui_view):
                        unused_ir_attachment_post_ids.append(record)
                        if file_name:
                            unused_files.append(file_name)
                else:
                    unused_ir_attachment_post_ids.append(record)

            # Remove record from ir_attachment_post file
            for unused_ir_attachment_post_id in unused_ir_attachment_post_ids:
                root_ir_attachment_post.remove(unused_ir_attachment_post_id)
            
            # Delete unused files
            for unused_file in unused_files:
                file_path = Path(self.destination_base_path + unused_file)
                if file_path.exists():
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Warning: Failed to remove file {file_path}: {e}")

            self.write_etree_content(path_ir_attachment_post, root_ir_attachment_post)

        return

    def order_ir_attachment_post(self, destination_module_path):
        """
        Orders <record> elements in 'ir_attachment_post.xml' based on numeric suffix in their IDs.

        This function looks for records with IDs matching the pattern 'ir_attachment_<number>' 
        and sorts them in ascending order by the numeric part. The sorted records are then 
        re-inserted at the beginning of the XML tree, maintaining the order.

        Args:
            destination_module_path (str): The base path to the module directory.
        """

        path_ir_attachment_post = Path(destination_module_path + '/demo/' + 'ir_attachment_post.xml')
        if path_ir_attachment_post.exists():
            root_ir_attachment_post = self.get_etree_content(path_ir_attachment_post)
            all_records = root_ir_attachment_post.xpath("//record")
            records = list(filter(lambda x: re.fullmatch(r'ir_attachment_\d+', x.get('id', '')), all_records))
            sorted_records = sorted(records, key = lambda x: int(x.get('id').split("_")[-1]))

            for record in records:
                root_ir_attachment_post.remove(record)
            for record in reversed(sorted_records):
                root_ir_attachment_post.insert(0, record)

            self.write_etree_content(path_ir_attachment_post, root_ir_attachment_post)
        
        return

    def clean_knowledge_article(self, destination_module_path):
        """
            Keep only the record with ID ending with 'welcome_article' in knowledge_article.xml,
            remove all others. Also remove 'last_edition_uid' fields, add 'is_locked' if missing,
            wrap certain field texts in CDATA.
        """    
        path_knowledge_article = Path(destination_module_path + '/data/' + 'knowledge_article.xml')
        if path_knowledge_article.exists():
            root_knowledge_article = self.get_etree_content(path_knowledge_article)
            records = root_knowledge_article.xpath("//record")
            for record in records:

                # Remove all 'last_edition_uid' fields in the record
                for field in record.xpath('.//field[@name="last_edition_uid"]'):
                    record.remove(field)
                
                # Add 'is_locked' field with eval="True" if missing in this record
                if not record.xpath('.//field[@name="is_locked"]'):
                    new_field = etree.Element("field", name="is_locked", eval="True")
                    record.append(new_field)
                
                record_id = record.get('id', '')
                if record_id.endswith("welcome_article"):
                    record.set("id", "welcome_article")  # Rename the ID

                    # Wrap field text containing '<div' in CDATA sections
                    for field in record:
                        if field.text and '<div' in field.text:
                            field.text = etree.CDATA(field.text)
                else:
                    # Remove all other records
                    root_knowledge_article.remove(record)

            self.write_etree_content(path_knowledge_article, root_knowledge_article)
        return

    def check_website_sale_installed(self):
        # Prepare the JSON-RPC payload to search for the 'website_sale' module
        
        session, uid = self.session_authentication()
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    self.db_name, uid, PASSWORD,
                    "ir.module.module", "search_read",
                    [[["name", "=", "website_sale"]]],
                    {"fields": ["state"], "limit": 1}
                ]
            },
            "id": 2
        }

        # Send the request to the server and parse the JSON response
        response = session.post(f"{BASE_URL}{self.port}/jsonrpc", json=payload).json()
        
        # Return the list of matched module(s) with their state
        if response["result"]:
            return response["result"][0]['state'] == 'installed'

    def add_demo_payment_provider(self, destination_module_path, manifest_demo_file_list):
        """
        Adds a demo payment provider XML file and updates the manifest demo file list,
        only if the 'website_sale' module is installed in the target Odoo database.
        
        Args:
            destination_module_path (str): Path to the destination module folder.
            manifest_demo_file_list (list): List of dictionaries representing demo files in manifest.
        """
        file_name = 'payment_provider_demo.xml'

        # Check if website_sale module is installed in the Odoo instance
        if self.check_website_sale_installed():
            xml_content = """<?xml version='1.0' encoding='UTF-8'?>
    <odoo noupdate="1">
        <function name="button_immediate_install" model="ir.module.module" eval="[ref('base.module_payment_demo')]"/>
    </odoo>
            """
            
            # Prepare dictionary for manifest demo file entry
            manifest_demo_file_dict = {
                'file_name': file_name,
                'ref_name': []  # No references for this file
            }
            # Append new demo file to manifest list
            manifest_demo_file_list.append(manifest_demo_file_dict)

            # Ensure demo directory exists and write XML content to file
            demo_file_path = Path(destination_module_path) / 'demo' / file_name
            demo_file_path.parent.mkdir(parents=True, exist_ok=True)
            demo_file_path.write_text(xml_content, encoding='utf-8')

        return

    def add_require_depends(self, depends_list):
        """
        Add required dependencies to the existing depends list and return the updated list.

        Args:
            depends_list (list): Original list of module dependencies.

        Returns:
            list: Sorted list of unique dependencies including the newly added ones.
        """
        new_depends = ['knowledge']
        depends_list = sorted(set(depends_list + new_depends))
        return depends_list

    def arrange_demo_files(self, destination_module_path, manifest_demo_file_list):
        """
        Finalizes the demo file arrangement and updates the __manifest__.py accordingly.

        Steps:
        1. Renames ir_ui_view.xml to website_view.xml if it exists.
        2. Deduplicates demo file references and prefixes with 'demo/'.
        3. Removes specific unused data files if they contain no <record> tags.
        4. Ensures required dependencies are included.
        5. Rewrites the manifest file with the updated 'demo' section and additional metadata.

        Args:
            destination_module_path (str): Full path to the module directory.
            manifest_demo_file_list (list): List of demo file metadata dictionaries.
        """

        # Rename ir_ui_view.xml to website_view.xml for consistency
        try:
            old_file = Path(destination_module_path + "/demo/ir_ui_view.xml")
            new_file = Path(destination_module_path + "/demo/website_view.xml")
            os.rename(old_file, new_file)
        except Exception as e:
            raise Exception(f"Error while renaming file: {e}")
        
        # Remove duplicate demo files; keep only first occurrence
        new_manifest_demo_file_list = []
        for file_list in manifest_demo_file_list:
            if file_list['file_name'] == "ir_ui_view.xml":
                file_list['file_name'] = "website_view.xml"
            if file_list['file_name'] not in new_manifest_demo_file_list:
                new_manifest_demo_file_list.append(file_list['file_name'])

        # Prefix each file with 'demo/' for manifest compatibility
        unique_manifest_demo_file_list = [ 'demo/' + file_name for file_name in new_manifest_demo_file_list ]

        # Read and evaluate the manifest file
        manifest_path = Path(destination_module_path + '/__manifest__.py')
        try:
            manifest = literal_eval(manifest_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise Exception(f"Unable to read manifest file: {e}")
        
        # Clean up specific files in the data directory if they have no <record> elements
        check_files = ['ir_attachment_pre.xml', 'knowledge_cover.xml', 'mail_template.xml', 'product_pricelist.xml']
        for check_file in check_files:
            file_path = Path(destination_module_path + '/data/' + check_file)
            if file_path.exists():
                etree_content = self.get_etree_content(file_path)
                records = etree_content.xpath("//record")
                if len(records) == 0:
                    os.remove(file_path)
                    manifest['data'].remove('data/' + check_file)
        
        # Adding some required dependencies like knowledge
        manifest['depends'] = self.add_require_depends(manifest['depends'])

        # Update the demo file list in the manifest
        manifest['demo'] = unique_manifest_demo_file_list

        # Format the manifest dictionary as Python code
        lines = ["{"]
        for key, value in manifest.items():
            if isinstance(value, str):
                lines.append(f"    '{key}': '{value}',")
            elif isinstance(value, list):
                lines.append(f"    '{key}': [")
                for item in value:
                    lines.append(f"        '{item}',")
                lines.append("    ],")
            else:
                lines.append(f"    '{key}': {value},")
        
        # Append static entries (assets, cloc_exclude, images)
        lines.append((f"""    'assets': {{
                'web.assets_backend': [
                    '{self.ind_name}/static/src/js/my_tour.js',
                ],
            }},
        'cloc_exclude': [
            'data/knowledge_article.xml',
            'static/src/js/my_tour.js',
        ],
        'images': [
            'images/main.png',
        ],"""))

        lines.append("}")

        # Write the updated manifest back to disk
        formatted_manifest = "\n".join(lines)
        try:
            manifest_path.write_text(formatted_manifest, encoding="utf-8")
        except Exception as e:
            raise Exception(f"Unable to write manifest file: {e}")

        return

    def add_theme_immediate_install_function(self, destination_module_path):
        """
            Adds an immediate install function for the theme module in the website_theme_apply.xml file.

            This function reads the theme_id reference from the demo/website.xml file of the given module.
            It then generates a <function> XML element to trigger the immediate installation of the theme module.
            The generated function block is appended inside the <odoo> tag of demo/website_theme_apply.xml.
            If the target XML file does not exist, it creates a new one with the required structure.

            Args:
                destination_module_path (str): The module directory name containing the demo folder with website.xml.
        """
        website_path = Path(destination_module_path + '/demo/' + 'website.xml')
        if website_path.exists():
            etree_content = self.get_etree_content(website_path)
            theme_id = etree_content.xpath("//field[@name='theme_id']")[0].get('ref')
            if theme_id:
        
                # Build new <function> entries for each SCSS customization
                new_function = f"""<function name="button_immediate_install" model="ir.module.module" eval="[ref('{theme_id}', raise_if_not_found=False)]"/>"""
                
                # Base structure if file does not exist
                base_xml = f"""<?xml version='1.0' encoding='UTF-8'?>
    <odoo>{new_function}
    </odoo>
    """
                target_path = Path(destination_module_path + '/demo/' + 'website_theme_apply.xml')

                # Update existing file or create new one
                if target_path.exists():
                    content = target_path.read_text(encoding='utf-8')
                    updated_content = content.replace("<odoo>", f"<odoo>\n\t{new_function}\n")
                else:
                    updated_content = base_xml

                # Write back to file
                try:
                    target_path.write_text(updated_content, encoding='utf-8')
                except Exception as e:
                    raise Exception(f"Unable to write website_theme_apply.xml file: {e}")

    def clean_sale_order_line_record(self, destination_module_path):
        """
            Process the 'sale_order_line.xml' file to clean and modify <record> elements.

            For records with `display_type` equal to 'line_section', wrap the text content
            of all <field name='name'> elements in a CDATA section. For all other records,
            remove the <field name='name'> elements entirely.

            Args:
                destination_module_path (str): Directory name containing the 'demo/sale_order_line.xml' file.

            Returns:
                None: Modifies the XML file in place without returning a value.
        """
        target_path = Path(destination_module_path + '/demo/' + 'sale_order_line.xml')
        if target_path.exists():
            etree_content = self.get_etree_content(target_path)
            records = etree_content.xpath("//record")
            for record in records:
                display_type_elem = record.xpath(".//field[@name='display_type']")
                if display_type_elem and display_type_elem[0].text and display_type_elem[0].text.strip() == 'line_section':
                    for field in record.xpath(".//field[@name='name']"):
                        original_text = field.text
                        if original_text:
                            field.text = etree.CDATA(original_text)
                else:
                    for field in record.xpath(".//field[@name='name']"):
                        record.remove(field)
            
            self.write_etree_content(target_path, etree_content)

        return


# ====================================================
#              Main Function         
# ====================================================

def main():
    parser = argparse.ArgumentParser(description="Industry Automation Script")

    parser.add_argument('--module_name', required=True, help="Name of the module")
    parser.add_argument('--db_version', required=True, help="Database version")
    parser.add_argument('--category', required=True, help="Module category")
    parser.add_argument('--dump_path', required=True, help="Path to the dump zip file")
    parser.add_argument('--destination_path', default="/home/odoo/Downloads", help="Path to save the cleaned module")
    parser.add_argument('--master_password', required=True, help="Odoo master password")

    args = parser.parse_args()

    task = ProcessDb(
        module_name=args.module_name,
        db_version=args.db_version,
        category=args.category,
        dump_path=args.dump_path,
        destination_path=args.destination_path,
        master_password=args.master_password,
    )

    task.process_dump_task()

if __name__ == "__main__":
    main()

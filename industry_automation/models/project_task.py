from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import zipfile
import os
import tempfile
import requests
import logging
import socket
import shutil
from markupsafe import Markup

# Setup logger
_logger = logging.getLogger(__name__)

 # Map DB version to fixed port
VERSION_PORT_MAP = {
    'saas~18.1': 10001,
    'saas~18.2': 10002,
}
BASE_URL = "http://localhost:"
PROJECT_NAME = "RD Fun Industry"
PROJECT_STAGE_NAME = "Spec"
MASTER_PASSWORD = "hyif-nir4-qjf5"
LOGIN = "admin"
PASSWORD = "admin"

class ProjectTask(models.Model):
    _inherit = 'project.task'

    module_name = fields.Char(string="Module Name")
    version = fields.Char(string="Dump Database Version")
    category = fields.Selection(
        selection=[
            ('finance', 'Finance'),
            ('hr', 'Human Resources'),
            ('sales', 'Sales'),
            ('inventory', 'Inventory'),
            ('other', 'Other'),               
        ],
        string="Module Category"
    )

    @api.model
    def process_new_tasks(self):
        project = self.env['project.project'].sudo().search([('name', '=', PROJECT_NAME)], limit=1)
        if not project:
            raise UserError("Project 'RD Fun Industry' not found.")
        project_id = project.id
        
        spec_stage = self.env['project.task.type'].sudo().search([
                ('name', '=', PROJECT_STAGE_NAME),
                ('project_ids', 'in', int(project_id))
            ], limit=1)
        
        tasks = self.env['project.task'].sudo().search([
            ('project_id', '=', int(project_id)),
            ('stage_id', '=', spec_stage.id),
            ('state', '=', '01_in_progress')
        ])
        for task in tasks:
            attachments = task.attachment_ids
            for attachment in attachments:
                if attachment.name.lower().endswith('.zip') and '.dump' in attachment.name.lower():
                    try:
                        module_name =task.module_name
                        version =task.version
                        category =task.category

                        task.export_module_zip(attachment, module_name, version, category, task.id)
                        task.sudo().write({'state': '03_approved'})

                    except Exception as e:
                        # Post failure message to Chatter
                        message = Markup("%s<b>%s</b><br/><br/>%s.") % (
                            "❌ Failed to process ZIP file ",
                            attachment.name,
                            str(e),
                        )
                        task.sudo().message_post(
                            body=message
                        )

    def export_module_zip(self, attachment, module_name, version, category, task_id):
        try:
            industry_name = attachment.name.split('.')[0]

            # fetch dump.zip from attachment
            temp_zip_file_path = self.download_dump_from_attachment(attachment)
            if not temp_zip_file_path:
                raise Exception("Failed to write zip file to temporary location.")

            # find server which version same as DB version 
            db_version = '.'.join(version.split('.')[:2])
            port = self.get_port_for_version(db_version)

            if not self.is_port_open('localhost', port):
                _logger.error(f"No server is running on port {port} for DB version {db_version}.")
                raise Exception(f"No server is running on port {port} for DB version {db_version}.")
            _logger.info(f"Server found on port {port} for DB version {db_version}.")
            
            # restore Database at matched version server
            restore_db_name = f"{module_name}_db"
            success = self.restore_db(port, restore_db_name, temp_zip_file_path)
            if not success:
                _logger.error(f"Database '{restore_db_name}' Failed to restore  on port {port}.")
                raise Exception("Database restore failed.")
            _logger.info(f"Database '{restore_db_name}' restored successfully on port {port}.")

            # store all generated file under this directory
            base_temp_dir = os.path.join(tempfile.gettempdir(), industry_name)
            os.makedirs(base_temp_dir, exist_ok=True)

            # export module zip 
            studio_zip_path = f"{base_temp_dir}/studio_customization.zip"
            self.export_studio_customizations(port, restore_db_name, studio_zip_path)


            # extract module zip to extract_path
            with zipfile.ZipFile(studio_zip_path, "r") as zip_ref:
                zip_ref.extractall(base_temp_dir)

            # clean module through script
            studio_extract_path = f"{base_temp_dir}/studio_customization"
            os.chdir(f"{base_temp_dir}")
            os.system(f"PYTHONPATH=/home/odoo/odoo/community python3 /home/odoo/odoo/industry/industry_automation/cleanup_scripts/script.py -d {restore_db_name} -m {module_name} -c {category} -p {studio_extract_path} ")
            _logger.info("Module Clean Up successful")

            module_zip_path = self.module_dir_to_zip(module_name, base_temp_dir)
            studio_extract_zip_path = self.module_dir_to_zip("studio_customization", base_temp_dir)

            studio_extract_attachment = self.add_to_attachment(studio_extract_zip_path, task_id)
            module_attachment = self.add_to_attachment(module_zip_path, task_id)
            if not studio_extract_attachment:
                _logger.error("studio_customization.zip not upload on an attachment")
            if not module_attachment:
                _logger.error(f"{module_name}.zip not upload on an attachment")


            # message = Markup("✅ ZIP file <b>%s</b> processed successfully.<br/>✅ ZIP file <b>%s.zip</b> and <b>studio_customization.zip</b> uploaded successfully.") % (
            #     attachment.name,
            #     module_name,
            # )
            # self.message_post(
            #     body=message,
            #     attachment_ids=[studio_extract_attachment.id, module_attachment.id],
            # )

            message = Markup(
                "<div style='color:green;'>"
                "✅ ZIP file <b>%s</b> processed successfully.<br/>"
                "✅ ZIP file <b>%s.zip</b> and <b>studio_customization.zip</b> uploaded successfully."
                "</div>"
            ) % (
                attachment.name,
                module_name,
            )

            self.message_post(
                body=message,
                attachment_ids=[studio_extract_attachment.id, module_attachment.id],
                message_type="notification",
                subtype_xmlid="mail.mt_comment",
            )

            _logger.info(f"studio_customization.zip and {module_name}.zip upload to task attachment successfully.")

        except Exception as e:
            _logger.exception("export_module_zip failed. ",e)

        finally:
            self.delete_temp_file(temp_zip_file_path)
            self.delete_temp_dir(base_temp_dir)

    def download_dump_from_attachment(self, attachment):
        """
        Writes the original ZIP attachment to a temporary file.
        Returns the path to the temporary .zip file.
        """
        try:
            file_data = base64.b64decode(attachment.datas)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip', mode='wb') as temp_zip_file:
                temp_zip_file.write(file_data)
                return temp_zip_file.name
        except Exception as e:
            _logger.exception("Failed to Download Dump DB file")

    def restore_db(self, port, db_name, temp_zip_file_path):
        try:
            with open(temp_zip_file_path, 'rb') as backup_file:
                response = requests.post(
                    f'{BASE_URL}{port}/web/database/restore',
                    data={
                        'master_pwd': MASTER_PASSWORD,
                        'name': db_name,
                        'copy': True,
                    },
                    files={
                        'backup_file': ('tattoo.zip', backup_file, 'application/zip')
                    }
                )

            if response.status_code in (200, 302):
                os.system(f"psql {db_name} -c \"UPDATE res_users SET login='{LOGIN}', password='{PASSWORD}' WHERE id=2;\"")
                return True
            else:
                return False
        except Exception :
            _logger.exception("restore_db Failed")
            return False

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
            result = response.json().get("result")
            if not result or not result.get("uid"):
                _logger.error("Authentication Failed")
                raise Exception("Login failed.")
            _logger.info("Authentication Successful")
            
            # step 2: check module web_studio install
            modules = self.check_module_installed(port, db_name, result["uid"])
            if modules:
                state = modules[0]['state']
                model_id = modules[0]['id']
                if state == "uninstalled":
                    self.install_module(port, db_name, result["uid"], model_id)
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
                        result["uid"],
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
            rpc_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                                db_name,
                                result["uid"],
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

            wizard_resp = session.post(f"{BASE_URL}{port}/jsonrpc", json=rpc_payload)
            
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
            
        except Exception:
            _logger.error("studio_customization Failed to Export")
            _logger.exception("export_studio_customizations failed")

    def delete_temp_file(self, file_path):
        """
        Deletes a temporary ZIP file after use.
        
        :param zip_path: Full path to the ZIP file.
        """
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)

    def check_module_installed(self, port, db_name, uid):
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
        response = requests.post(f"{BASE_URL}{port}/jsonrpc", json=payload).json()
        
        return response["result"]

    def install_module(self, port, db_name, uid, module_id):

            # Install the module
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
            install_response = requests.post(f"{BASE_URL}{port}/jsonrpc", json=payload).json()
            
            if not install_response["result"]:
                _logger.error("Module Studio can't install")
            return install_response["result"]

    def get_port_for_version(self, db_version):
        port = VERSION_PORT_MAP.get(db_version)
        if not port:
            _logger.error(f"No port mapped for DB version {db_version}")
            raise Exception(f"No port mapped for DB version {db_version}")
        return port

    def is_port_open(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if a TCP port is open on the given host."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            try:
                sock.connect((host, port))
                return True
            except (socket.timeout, ConnectionRefusedError):
                return False

    def module_dir_to_zip(self, dir_name, parent_dir):
        module_path = os.path.join(parent_dir, dir_name) 
        module_zip_path = os.path.join(parent_dir, f"{dir_name}.zip")

        with zipfile.ZipFile(module_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(module_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, module_path)
                    zipf.write(full_path, arcname=rel_path)
        return module_zip_path
    
    def add_to_attachment(self, zip_path, task_id):
        try:
            with open(zip_path, "rb") as f:
                file_data = f.read()
            file_name = zip_path.split('/')[-1]
            attachment = self.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': base64.b64encode(file_data),
                'res_model': 'project.task',
                'res_id': task_id,
                'type': 'binary',
                'mimetype': 'application/zip',
            })
            return attachment
        except Exception:
            return False

    def delete_temp_dir(self, dir_path):
        """
        Deletes a temporary directory and all its contents.
        
        :param dir_path: Full path to the directory.
        """
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)

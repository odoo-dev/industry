import base64
import zipfile
import io
import os
import tempfile
import requests
import subprocess
import re
from xmlrpc.client import ServerProxy
import psycopg2
import logging

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def export_module_zip(attachment, output_path, module_name, version, category):
    try:
        industry_name = attachment.name.split('.')[0]
        output_path = f"{output_path}/{industry_name}"
        os.makedirs(output_path, exist_ok=True)

        print(f">>> output path ----->>> {output_path}")

        # fetch dump.zip from attachment
        temp_zip_file_path = extract_zip_file_to_temp(attachment)
        if not temp_zip_file_path:
            raise Exception("Failed to write zip file to temporary location.")

        # find server which version same as DB version 
        db_version = '.'.join(version.split('.')[:2])
        port = get_port_for_version(db_version)
        if not is_port_open('localhost', port):
            print("------------- not server found on this port -----------")
            raise Exception(f"No server is running on port {port} for DB version {db_version}.")
        print("------------- server found on this port -----------")
        
        

        # restore Database at matched version server
        restore_db_name = f"{module_name}_db"
        master_password = "hyif-nir4-qjf5"
        success = restore_db(port, master_password, restore_db_name, temp_zip_file_path)
        if not success:
            raise Exception("Database restore failed.")

        print("------------- DB restore successfullyyyyy-------------")

        # store all generated file under this directory
        base_temp_dir = os.path.join(tempfile.gettempdir(), industry_name)
        os.makedirs(base_temp_dir, exist_ok=True)

        print(f">>> base temp dir ---> {base_temp_dir}")

        # export module zip 
        login = "admin"
        password = "admin"
        path_to_store = f"{base_temp_dir}/studio_customizations.zip"
        export_studio_customizations(f"http://localhost:{port}", restore_db_name, login, password, path_to_store)

        print("------------- export  successfullyyyyy-------------")


        # extract module zip to extract_path
        os.makedirs(output_path, exist_ok=True)
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(path_to_store, "r") as zip_ref:
            zip_ref.extractall(base_temp_dir)
        
        print(f">>> extract success {temp_dir}")

        # clean module through script
        module_path = f"{output_path}/studio_customization"
        os.chdir(f"{base_temp_dir}")
        os.system(f"PYTHONPATH=/home/odoo/odoo/community python3 /home/odoo/odoo/industry/industry_automation/cleanup_scripts/script.py -d {restore_db_name} -m {module_name} -c {category} -p {module_path} ")
        logger.info("Clean Up script executed successfully.")


    except Exception as e:
        logger.exception("export_module_zip failed. ",e)

    finally:
        delete_temp_file(temp_zip_file_path)

def extract_zip_file_to_temp(attachment):
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
        logger.exception("Failed to extract zip")

def restore_db(port, master_password, db_name, temp_zip_file_path):
    try:
        with open(temp_zip_file_path, 'rb') as backup_file:
            response = requests.post(
                f'http://localhost:{port}/web/database/restore',
                data={
                    'master_pwd': master_password,
                    'name': db_name,
                    'copy': True,
                },
                files={
                    'backup_file': ('tattoo.zip', backup_file, 'application/zip')
                }
            )

        if response.status_code in (200, 302):
            os.system(f"psql {db_name} -c \"UPDATE res_users SET login='admin', password='admin' WHERE id=2;\"")
            return True
        else:
            raise Exception(f"Restore failed: status {response.status_code} | {response.text}")
    except Exception as e:
        logger.exception("restore_db . ",e)

def export_studio_customizations(base_url, db_name, login, password, path_to_store):
    try:
        session = requests.Session()
        # Step 1: Authenticate via /web/session/authenticate (sets session cookie)
        auth_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": db_name,
                "login": login,
                "password": password,
            },
            "id": 1
        }
        response = session.post(f"{base_url}/web/session/authenticate", json=auth_payload)
        response.raise_for_status()
        result = response.json().get("result")
        if not result or not result.get("uid"):
            raise Exception("Login failed.")
        
        print(">>> login success")
        
        # step 2: check module web_studio install
        modules = check_module_installed(base_url, db_name, result["uid"], password)
        if modules:
            state = modules[0]['state']
            model_id = modules[0]['id']
            if state == "uninstalled":
                install_module(base_url, db_name, result["uid"], password, model_id)
        else:
            raise Exception("web_studio module not found in registry.")
        
        print(">>> web_studio check success")

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
                    password,
                    "studio.export.model",
                    "action_preset",
                    [{}],
                ]
            },
            "id": 2
        }
        preset_resp = session.post(f"{base_url}/jsonrpc", json=preset_payload)
        preset_resp.raise_for_status()

        print(">>> preset success")

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
                            password,
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

        wizard_resp = session.post(f"{base_url}/jsonrpc", json=rpc_payload)
        
        wizard_resp.raise_for_status()
        
        if not wizard_resp.json()["result"]:
            raise Exception("wizard id not found")
        wizard_id = wizard_resp.json()["result"]
        
        print(">>> wizard create success")

        # Step 5: Call the export route (no token needed, session is authenticated)
        export_url = f"{base_url}/web_studio/export?active_id={wizard_id}&token=dummytoken"
        export_resp = session.get(export_url, stream=True)
        

        if export_resp.status_code == 200 and export_resp.headers['Content-Type'] == 'application/zip':
             with open(path_to_store, "wb") as f:
                f.write(export_resp.content)
        else:
            raise Exception(f" Export failed: {export_resp.status_code} - {export_resp.text}")
        
        print(">>> export success")
        
    except Exception as e:
        logger.exception("export_studio_customizations failed")

def delete_temp_file(file_path):
    """
    Deletes a temporary ZIP file after use.
    
    :param zip_path: Full path to the ZIP file.
    """
    if os.path.exists(file_path):
        os.remove(file_path)

def check_module_installed(base_url, db_name, uid, password):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db_name, uid, password,
                "ir.module.module", "search_read",
                [[["name", "=", "web_studio"]]],
                {"fields": ["state"], "limit": 1}
            ]
        },
        "id": 2
    }
    response = requests.post(f"{base_url}/jsonrpc", json=payload).json()
    
    return response["result"]

def install_module(base_url, db_name, uid, password, module_id):

        # Install the module
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db_name, uid, password,
                    "ir.module.module", "button_immediate_install",
                    [module_id]
                ]
            },
            "id": 4
        }
        install_response = requests.post(f"{base_url}/jsonrpc", json=payload).json()
        
        return install_response["result"]

# Map DB version to fixed port
VERSION_PORT_MAP = {
    'saas~18.1': 10001,
    'saas~18.2': 10002,
}

def get_port_for_version(db_version):
    port = VERSION_PORT_MAP.get(db_version)
    if not port:
        raise Exception(f"No port mapped for DB version {db_version}")
    return port

import socket

def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is open on the given host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False

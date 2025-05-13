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

def export_module_zip(attachment, output_path, module_name, version, category):
    try:
        industry_name = attachment.name.split('.')[0]
        output_path = f"{output_path}/{industry_name}"
        os.makedirs(output_path, exist_ok=True)
        breakpoint()

        # fetch dump.zip from attachment
        temp_zip_file_path = extract_zip_file_to_temp(attachment)
        if not temp_zip_file_path:
            raise Exception("Failed to write zip file to temporary location.")

        # # fetch .sql file from attachment
        # temp_sql_file_path = extract_sql_file_to_temp(attachment)
        # if not temp_sql_file_path:
        #     raise Exception("No .sql file found in zip.")

        # # find dump DB version
        # db_version = find_db_version(temp_sql_file_path)
        # if not db_version:
        #     raise Exception("Could not determine DB version from SQL file.")

        # find server which version same as DB version 
        db_version = '.'.join(version.split('.')[:2])
        matched_server = find_matched_server(db_version)
        if not matched_server:
            raise Exception(f"No running server found for version {db_version}.")

        # restore Database at matched version server
        restore_db_name = f"{module_name}_db"
        port = matched_server['port']
        master_password = "hyif-nir4-qjf5"
        success = restore_db(port, master_password, restore_db_name, temp_zip_file_path)
        if not success:
            raise Exception("Database restore failed.")

        # export module zip 
        login = "admin"
        password = "admin"
        path_to_store = f"{output_path}/studio_customizations.zip"
        export_studio_customizations(f"http://localhost:{port}", restore_db_name, login, password, path_to_store)

        # extract module zip to extract_path
        os.makedirs(output_path, exist_ok=True)
        with zipfile.ZipFile(path_to_store, "r") as zip_ref:
            zip_ref.extractall(output_path)

        # clean module through script
        module_path = f"{output_path}/studio_customization"
        os.chdir(f"{output_path}")
        os.system(f"PYTHONPATH=/home/odoo/odoo/community python3 /home/odoo/odoo/industry/industry_automation/cleanup_scripts/script.py -d {restore_db_name} -m {module_name} -c {category} -p {module_path} ")
        print(">>> clean Up script executed")


    except Exception as e:
        raise Exception(f"export_module_zip failed: {e}")

    finally:
        delete_temp_file(temp_zip_file_path)
        # delete_temp_file(temp_sql_file_path)

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
        raise Exception(f"Failed to extract zip: {e}")

def extract_sql_file_to_temp(attachment):
    """
    Extracts .sql file from a zip attachment and stores it in a temp file.
    Returns the path to the temporary .sql file.
    """
    try:
        file_data = base64.b64decode(attachment.datas)
        with zipfile.ZipFile(io.BytesIO(file_data), 'r') as zip_file:
            for file_info in zip_file.infolist():
                if file_info.filename.endswith('.sql'):
                    with zip_file.open(file_info) as sql_file:
                        sql_content = sql_file.read().decode('utf-8')
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.sql', mode='w') as temp_sql_file:
                            temp_sql_file.write(sql_content)
                            return temp_sql_file.name
    except Exception as e:
        raise Exception(f"Failed to extract SQL file: {e}")
    return None

def find_db_version(temp_sql_file_path):
    """
    Creates a PostgreSQL database from the given SQL file, imports it,
    and retrieves the Odoo version from the 'base' module.
    """
    db_name = os.path.basename(temp_sql_file_path).split('.')[0]
    try:
        # Step 1: Create the database
        os.system(f'createdb {db_name}')

        # Step 2: Import SQL into the database
        os.system(f'psql {db_name} < {temp_sql_file_path}')

        # Step 3: Optional - Update default admin user
        os.system(f"psql {db_name} -c \"UPDATE res_users SET login='admin', password='admin' WHERE id=2;\"")

        # Step 4: Fetch Odoo version
        conn = psycopg2.connect(dbname=db_name, user='odoo', password='odoo', host='localhost')
        cur = conn.cursor()
        cur.execute("SELECT latest_version FROM ir_module_module WHERE name = 'base' ORDER BY id DESC LIMIT 1;")
        row = cur.fetchone()
        conn.close()

        if row:
            version = '.'.join(row[0].split('.')[:2])
            return version
        else:
            raise Exception("Base module version not found.")
    except Exception as e:
        raise Exception(f"find_db_version failed: {e}")
    finally:
        os.system(f'dropdb {db_name}')

def find_matched_server(db_version):
    try:
        servers = get_running_odoo_servers()
        for server in servers:
            version = get_odoo_version(server['port'])
            if version == db_version:
                server['version'] = version
                return server
        raise Exception(f"No server found matching DB version {db_version}")
    except Exception as e:
        raise Exception(f"find_matched_server failed: {e}")
    
def get_odoo_version(port):
    """Call custom XML-RPC service to get version from a running Odoo instance."""

    try:
        url = f'http://localhost:{port}/xmlrpc/2/common'
        server = ServerProxy(url)
        version_info = server.version()
        return version_info.get('server_serie')  # e.g., '18.1'
    except Exception as e:
        return None

def get_running_odoo_servers():
    """Return a list of running odoo-bin commands with their ports, excluding current process."""
    servers = []
    current_pid = os.getpid()  # Get the PID of the current process

    try:
        output = subprocess.check_output(['ps', 'aux'], text=True)
    except subprocess.CalledProcessError as e:
        return servers

    for line in output.splitlines():
        if 'odoo-bin' in line:
            columns = line.split(None, 10)
            pid = int(columns[1])  # Second column is the PID
            if pid == current_pid:
                continue  # Skip current process

            command = columns[-1]
            port = 8069  # Default port

            match = re.search(r'-p\s*(\d+)', command)
            if match:
                port = int(match.group(1))

            bin_path_match = re.search(r'(\/[\w\/\.-]*odoo-bin)', command)
            bin_path = bin_path_match.group(1) if bin_path_match else './odoo-bin'

            servers.append({'command': command, 'port': port, 'bin_path': bin_path})

    return servers

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
        raise Exception(f"restore_db failed: {e}")

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
        
        # step 2: check module web_studio install
        modules = check_module_installed(base_url, db_name, result["uid"], password)
        if modules:
            state = modules[0]['state']
            model_id = modules[0]['id']
            if state == "uninstalled":
                install_module(base_url, db_name, result["uid"], password, model_id)
        else:
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
        

        # Step 5: Call the export route (no token needed, session is authenticated)
        export_url = f"{base_url}/web_studio/export?active_id={wizard_id}&token=dummytoken"
        export_resp = session.get(export_url, stream=True)
        

        if export_resp.status_code == 200 and export_resp.headers['Content-Type'] == 'application/zip':
            with open(path_to_store, "wb") as f:
                f.write(export_resp.content)
        else:
            raise Exception(f" Export failed: {export_resp.status_code} - {export_resp.text}")
        
    except Exception as e:
        raise Exception(f"export_studio_customizations failed: {e}")

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

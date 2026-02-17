# Part of Odoo. See LICENSE file for full copyright and licensing details.
import ast
import os
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED


class IndustryUtils:
    def __init__(self, industry_path: str):
        self.industry_path = industry_path

    def get_zip(self, module_name: str):
        output = BytesIO()
        zf = ZipFile(output, "w", ZIP_DEFLATED)
        industry_modules = self.get_industry_dependencies(module_name)
        dirs = []
        for module in industry_modules:
            if module == f"website_{module_name}":
                # Submodule lives inside industry folder
                dirs.append(os.path.join(self.industry_path, module_name, module))
            else:
                dirs.append(self.industry_path + module)
        website_sub_path = os.path.join(self.industry_path, module_name, f"website_{module_name}")
        for dir in dirs:
            for dirname, _, files in os.walk(dir):
                if dir == website_sub_path:
                    # Submodule must appear as website_<name>/ at root of zip for Odoo
                    rel = os.path.relpath(dirname, dir)
                    zip_dirname = f"website_{module_name}" if rel == "." else f"website_{module_name}{os.sep}{rel}"
                else:
                    zip_dirname = os.sep.join(dirname.split(os.sep)[1:])
                zf.write(dirname, zip_dirname)
                for filename in files:
                    zf.write(os.path.join(dirname, filename), os.path.join(zip_dirname, filename))
        zf.close()
        return output

    def get_manifest(self, industry: str):
        return self.industry_path + industry + '/__manifest__.py'

    def is_industry(self, module: str):
        return os.path.exists(self.get_manifest(module))

    def _has_website_submodule(self, module_name: str) -> bool:
        """Return True if this industry has a website_<industry> subfolder with a valid module."""
        website_sub = f"website_{module_name}"
        path = os.path.join(self.industry_path, module_name, website_sub)
        return (
            os.path.isdir(path)
            and os.path.isfile(os.path.join(path, "__manifest__.py"))
        )

    def get_dependencies(self, module_name: str):
        industries = {module_name}
        other_dep = set()
        to_check = [module_name]
        while to_check:
            manifest_file = self.get_manifest(to_check.pop())
            with open(manifest_file, encoding="utf-8") as f:
                manifest = ast.literal_eval(f.read())
            for dep in manifest.get('depends'):
                if not self.is_industry(dep):
                    other_dep.add(dep)
                elif dep not in industries:
                    to_check.append(dep)
                    industries.add(dep)
        # If this industry has a website_<industry> submodule, include it so it gets installed and activated
        if self._has_website_submodule(module_name):
            industries.add(f"website_{module_name}")
        return industries, other_dep

    def get_industry_dependencies(self, module_name: str):
        return self.get_dependencies(module_name)[0]

    def install_internal_dependencies(self, module_name: str, env):
        dependencies = self.get_dependencies(module_name)[1]
        modules = env['ir.module.module'].search([('name', 'in', dependencies)])
        return modules.button_immediate_install()

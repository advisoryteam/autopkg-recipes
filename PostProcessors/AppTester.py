#!/usr/bin/env python

from autopkglib import Processor, ProcessorError

import subprocess
import os.path
import json
import requests

__all__ = ["AppTester"]

class AppTester(Processor):
    description = ("Sends the most recently uploaded application title to a GitHub Actions workflow.")

    input_variables = {
        "munki_info": {
            "required": False,
            "description": ("Munki info dictionary to use to display info.")
        },
        "munki_repo_changed": {
            "required": False,
            "description": ("Whether or not item was imported.")
        },
        "username": {
            "required": False,
            "description": ("GitHub username.")
        },
        "access_token": {
            "required": False,
            "description": ("GitHub Personal Access Token.")
        },
        "requests_url": {
            "required": False,
            "description": ("GitHub requests URL.")
        },
        "manifest_name": {
            "required": False,
            "description": ("Name of the manifest to add the app.")
        }
    }
    output_variables = {
    }

    __doc__ = description

    def main(self):
        was_imported = self.env.get("munki_repo_changed")
        munkiInfo = self.env.get("munki_info")
        pkg_info = self.env.get("munki_importer_summary_result")["data"]["pkginfo_path"]
        username = self.env.get("username")
        access_token = self.env.get("access_token")
        requests_url = self.env.get("requests_url")
        manifest_name = self.env.get("manifest_name")

        if was_imported:
            name = self.env.get("munki_importer_summary_result")["data"]["name"]

            if name:
                command = f"/usr/local/munki/manifestutil --add-pkg {name} --manifest '{manifest_name}' --section 'managed_installs'"
                process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                
                post_data = {
                    "event_type": "app_test",
                    "client_payload": {
                        "app": name,
                        "pkg_info": pkg_info,
                        "manifest_name": manifest_name
                    }
                }
                
                headers = {
                    "Accept": "application/vnd.github.everest-preview+json",
                    "Content-Type": "application/json"
                }
                
                auth = (username, access_token)
                
                response = requests.post(requests_url, headers=headers, data=json.dumps(post_data), auth=auth)

if __name__ == "__main__":
    processor = AppTester()
    processor.execute_shell()

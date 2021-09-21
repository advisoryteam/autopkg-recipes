#!/usr/bin/env python
#
# Copyright 2021 Ryon Riley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from autopkglib import Processor, ProcessorError

import subprocess
import os.path
import json
import requests

# Set the webhook_url to the one provided by Microsoft Teams when you create the webhook

__all__ = ["TeamsPoster"]

class TeamsPoster(Processor):
    description = ("Posts to Microsoft Teams via webhook based on output of a MunkiImporter. "
                    "Based on Graham Pugh's slacker.py - https://github.com/grahampugh/recipes/blob/master/PostProcessors/slacker.py"
                    "and "
                    "@thehill idea on macadmin slack - https://macadmins.slack.com/archives/CBF6D0B97/p1542379199001400"
                    "Takes elements from " "https://gist.github.com/devStepsize/b1b795309a217d24566dcc0ad136f784"
                    "and "
                    "https://github.com/autopkg/nmcspadden-recipes/blob/master/PostProcessors/Yo.py")

    input_variables = {
        "munki_info": {
            "required": False,
            "description": ("Munki info dictionary to use to display info.")
        },
        "munki_repo_changed": {
            "required": False,
            "description": ("Whether or not item was imported.")
        },
        "webhook_url": {
            "required": False,
            "description": ("Microsoft Teams webhook.")
        }
    }
    output_variables = {
    }

    __doc__ = description

    def main(self):
        was_imported = self.env.get("munki_repo_changed")
        munkiInfo = self.env.get("munki_info")
        webhook_url = self.env.get("webhook_url")

        if was_imported:
            name = self.env.get("munki_importer_summary_result")["data"]["name"]
            version = self.env.get("munki_importer_summary_result")["data"]["version"]
            pkg_path = self.env.get("munki_importer_summary_result")["data"]["pkg_repo_path"]
            pkginfo_path = self.env.get("munki_importer_summary_result")["data"]["pkginfo_path"]
            catalog = self.env.get("munki_importer_summary_result")["data"]["catalogs"]
            if name:
                teams_data = {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.0",
                    "body": [
                        {
                            "type": "Container",
                            "id": "2dd12537-117c-dfa2-1804-317dd43563d8",
                            "padding": "None",
                            "items": [
                                {
                                    "type": "ColumnSet",
                                    "columns": [
                                        {
                                            "type": "Column",
                                            "id": "efa405ce-8bc5-8e0b-ef40-6d435d55d7cb",
                                            "padding": "None",
                                            "width": "auto",
                                            "items": [
                                                {
                                                    "type": "Image",
                                                    "id": "4fbed97f-016e-7d8f-a8f5-a87e16e39da8",
                                                    "url": "https://emoji.slack-edge.com/T3TCY3AMU/munki/eabba2d2c6027aaf.png",
                                                    "size": "Small"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "Column",
                                            "id": "a790e77b-7324-4e65-c731-bf0b4a2d3f71",
                                            "padding": "None",
                                            "width": "stretch",
                                            "items": [
                                                {
                                                    "type": "TextBlock",
                                                    "id": "ee0da3bd-da41-bb1c-8f34-84072262e97b",
                                                    "text": "New item imported into Munki:",
                                                    "wrap": true,
                                                    "weight": "Bolder",
                                                    "horizontalAlignment": "Left"
                                                }
                                            ],
                                            "horizontalAlignment": "Left",
                                            "verticalContentAlignment": "Center"
                                        }
                                    ],
                                    "padding": "None"
                                }
                            ]
                        },
                        {
                            "type": "FactSet",
                            "id": "35f73aa7-c58e-120a-3f5b-90a542ac3a96",
                            "facts": [
                                {
                                    "title": "- Title:",
                                    "value": "%s"
                                },
                                {
                                    "title": "- Version:",
                                    "value": "%s"
                                },
                                {
                                    "title": "- Catalog:",
                                    "value": "%s"
                                },
                                {
                                    "title": "- Pkg Path:",
                                    "value": "%s"
                                },
                                {
                                    "title": "- Pkginfo Path:",
                                    "value": "%s"
                                }
                            ],
                            "separator": true
                        }
                    ],
                    "padding": "None"
                } % (name, version, catalog, pkg_path, pkginfo_path)

                response = requests.post(
                webhook_url, json=teams_data)
                if response.status_code != 200:
                    raise ValueError(
                                'Request to Teams returned an error %s, the response is:\n%s'
                                % (response.status_code, response.text)
                                )


if __name__ == "__main__":
    processor = TeamsPoster()
    processor.execute_shell()

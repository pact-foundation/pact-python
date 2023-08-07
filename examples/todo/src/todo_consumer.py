import os
import requests
import xml.etree.ElementTree as ET
import platform
target_platform = platform.platform().lower()
is_not_win = any(substring in target_platform for substring in ['linux', 'macos'])
is_gha = os.getenv("ACT") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
mime_type = 'image/jpeg' if is_not_win and is_gha else 'application/octet-stream'

class TodoConsumer(object):
    def __init__(self, base_uri):
        self.base_uri = base_uri

    def get_projects(self, format='json'):
        """Fetch all the projects from the server. Supports XML and JSON formats"""
        uri = self.base_uri + '/projects'
        response = requests.get(uri,
                                headers={'Accept': 'application/' + format})
        # TODO add query param support in PactV3 interface
        # response = requests.get(uri,
        #                         headers={'Accept': 'application/' + format},
        #                         params={'from': 'today'})
        response.raise_for_status()
        if format == 'json':
            print(f'returning json: {response.json()}')
            return response.json()
        else:
            print(f'returning xml: {response.text}')
            return ET.fromstring(response.text)

    def post_image(self, id, file_path):
        """Store an image against a project"""
        print(id)
        print(file_path)
        print(mime_type)
        print(target_platform)
        uri = self.base_uri + '/projects/' + str(id) + '/images'
        response = requests.post(uri, data=open(file_path, 'rb'), headers={'Content-Type': mime_type})
        response.raise_for_status()

import requests
import xml.etree.ElementTree as ET


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
        uri = self.base_uri + '/projects/' + str(id) + '/images'
        response = requests.post(uri, data=open(file_path, 'rb'), headers={'Content-Type': 'image/jpeg'})
        response.raise_for_status()

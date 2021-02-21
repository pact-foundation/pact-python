import requests


class TodoConsumer(object):
    def __init__(self, base_uri):
        self.base_uri = base_uri

    def get_projects(self, format='json'):
        """Fetch all the projects from the server. Supports XML and JSON formats"""
        uri = self.base_uri + '/projects'
        print(uri)
        response = requests.get(uri,
                                headers={'Accept': 'application/' + format},
                                params={'from': 'today'})
        print(response)
        response.raise_for_status()

        if format == 'json':
            return response.json()
        else:
            return response.text

#   postImage: (id, image) => {
#     const data = fs.readFileSync(image)
#     return axios.post(serverUrl + "/projects/" + id + "/images", data, {
#       headers: {
#         "Content-Type": "application/octet-stream",
#       },
#     })
#   },
# }

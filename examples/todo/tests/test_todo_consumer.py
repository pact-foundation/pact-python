import os
import pytest
from ..src.todo_consumer import TodoConsumer
from pact import PactV3
from pact.matchers_v3 import EachLike, Integer, Like, AtLeastOneLike
# from pact.matchers_v3 import EachLike, Integer, Like, DateTime, AtLeastOneLike
# import xml.etree.ElementTree as ET
import platform
target_platform = platform.platform().lower()
is_not_win = any(substring in target_platform for substring in ['linux', 'macos'])
is_gha = os.getenv("ACT") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
mime_type = 'image/jpeg' if is_not_win and is_gha else 'application/octet-stream'
@pytest.fixture
def provider():
    return PactV3('TodoApp', 'TodoServiceV3')


def test_get_projects_as_json(provider: PactV3):
    (provider
     .new_http_interaction('same_as_upon_receiving')
     .given('i have a list of projects')
        .upon_receiving('a request for projects')
        .with_request(method="GET", path="/projects", query=None, headers=[{"name": 'Accept', "value": "application/json"}])
        # .with_request(method="GET", path="/projects", query={'from': "today"}, headers=[{"name": 'Accept', "value": "application/json"}])
        .will_respond_with(
         headers=[{"name": 'Content-Type', "value": "application/json"}],
         body=EachLike({
             'id': Integer(1),
             'name': Like("Project 1"),
             # 'due': DateTime("yyyy-MM-dd'T'HH:mm:ss.SSSX", "2016-02-11T09:46:56.023Z"),
             'tasks': AtLeastOneLike({
                 'id': Integer(),
                 'name': Like("Do the laundry"),
                 'done': Like(True)
             }, examples=4)
         })))

    with provider:
        provider.start_service()
        print(f"Mock server is running at {provider.mock_server_port}")

        todo = TodoConsumer(f"http://127.0.0.1:{provider.mock_server_port}")
        projects = todo.get_projects()

        assert len(projects) == 1
        assert projects[0]['id'] == 1
        assert len(projects[0]['tasks']) == 4
        assert projects[0]['tasks'][0]['id'] != 101
        provider.verify()

@pytest.mark.skipif(
    True,
    reason="https://github.com/pact-foundation/pact-reference/issues/305")
# TODO:- This test in unreliable, sometimes xml is not returned from the mock provider
def test_with_xml_requests(provider: PactV3):
    (provider
     .new_http_interaction('same_as_upon_receiving')
     .given('i have a list of projects')
        .upon_receiving('a request for projects in XML')
        # TODO:- support passing query to native_mock_server
        .with_request(method="GET", path="/projects", query=None, headers=[{"name": 'Accept', "value": "application/xml"}])
        # .with_request(method="GET", path="/projects", query={'from': "today"}, headers=[{"name":'Accept',"value": "application/xml"}])
        .will_respond_with(
         headers=[
             # TODO:- if content-type not set, xml body not returned
             # TODO:- Test is unreliable, ran locally
             # TODO:- Probably easier just to ask for a content_type argument?
             # TODO:- Getting written to pact file as
             # TODO:-  "headers": {
             # TODO:-   "Content-Type": "application/xml",
             # TODO:-   "content-type": ", application/xml"
             # TODO:- },
             {"name": "Content-Type", "value": "application/xml"},
             {"name": "content-type", "value": "application/xml"}
         ],
         body='''<?xml version="1.0" encoding="UTF-8"?>
                    <projects>
                    <item>
                    <id>1</id>
                    <tasks>
                        <item>
                         <id>1</id>
                         <name>Do the laundry</name>
                         <done>true</done>
                        </item>
                        <item>
                         <id>2</id>
                         <name>Do the dishes</name>
                         <done>false</done>
                        </item>
                        <item>
                         <id>3</id>
                         <name>Do the backyard</name>
                         <done>false</done>
                        </item>
                        <item>
                         <id>4</id>
                         <name>Do nothing</name>
                         <done>false</done>
                        </item>
                    </tasks>
                    </item>
                    </projects>'''

     ))
    with provider:
        mock_server_port = provider.start_service()
        print(f"Mock server is running at {mock_server_port}")

        todo = TodoConsumer(f"http://127.0.0.1:{mock_server_port}")
        projects = todo.get_projects('xml')
        assert len(projects) == 1
        # print(ET.tostring(projects[0], encoding='utf8').decode('utf8'))
        assert projects[0][0].text == '1'
        tasks = projects[0].findall('tasks')[0]
        assert len(tasks) == 4
        assert tasks[0][0].text == '1'
        assert tasks[0][1].text == 'Do the laundry'
        provider.verify()


def test_with_image_upload(provider: PactV3):
    binary_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'example.jpg'))
    (provider
     .new_http_interaction('same_as_upon_receiving').given('i have a project', {'id': 1001, 'name': 'Home Chores'})
        .upon_receiving('a request to store an image against the project')
        .with_request_with_binary_file(
         headers=[{"name": 'content-type', "value": mime_type}],
         file=binary_file_path,
         path="/projects/1001/images")
        .will_respond_with(status=201))

    with provider:
        provider.start_service()
        print(f"Mock server is running at {provider.mock_server_port}")

        todo = TodoConsumer(f"http://127.0.0.1:{provider.mock_server_port}")
        todo.post_image(1001, binary_file_path)
        provider.verify()


# TODO Create XMLBuilder which supports matchers.

    # (provider.given('i have a list of projects')
    #     .upon_receiving('a request for projects in XML')
    #     .with_request(method="GET", path="/projects", query={'from': "today"}, headers={'Accept': "application/xml"})
    #     .will_respond_with(
    #     headers={"Content-Type": "application/xml"},
    #                 body= new XmlBuilder("1.0", "UTF-8", "ns1:projects").build(el => {
    #                   el.setAttributes({
    #                     id: "1234",
    #                     "xmlns:ns1": "http://some.namespace/and/more/stuff",
    #                   })
    #                   el.eachLike(
    #                     "ns1:project",
    #                     {
    #                       id: integer(1),
    #                       type: "activity",  # noqa: F821
    #                       name: string("Project 1"),
    #                       // TODO: implement XML generators
    #                       // due: timestamp(
    #                       //   "yyyy-MM-dd'T'HH:mm:ss.SZ",
    #                       //   "2016-02-11T09:46:56.023Z"
    #                       // ),
    #                     },
    #                     project => {
    #                       project.appendElement("ns1:tasks", {}, task => {
    #                         task.eachLike(
    #                           "ns1:task",
    #                           {
    #                             id: integer(1),
    #                             name: string("Task 1"),
    #                             done: boolean(true),
    #                           },
    #                           null,
    #                           { examples: 5 }
    #                         )
    #                       })
    #                     },
    #                     { examples: 2 }
    #                   )
    #                 }),

    # ))

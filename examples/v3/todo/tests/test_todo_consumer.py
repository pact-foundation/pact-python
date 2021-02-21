import pytest
from ..src.todo_consumer import TodoConsumer
from pact import PactV3
from pact.matchers_v3 import EachLike, Integer, Like, DateTime, AtLeastOneLike


@pytest.fixture
def provider():
    return PactV3('TodoApp', 'TodoServiceV3')


def test_get_projects_as_json(provider):
    (provider.given('i have a list of projects')
        .upon_receiving('a request for projects')
        .with_request(method="GET", path="/projects", query={'from': "today"}, headers={'Accept': "application/json"})
        .will_respond_with(
            headers={"Content-Type": "application/json"},
            body=EachLike({
                'id': Integer(1),
                'name': Like("Project 1"),
                'due': DateTime("yyyy-MM-dd'T'HH:mm:ss.SSSX", "2016-02-11T09:46:56.023Z"),
                'tasks': AtLeastOneLike({
                    'id': Integer(),
                    'name': Like("Do the laundry"),
                    'done': Like(True)
                }, examples=4)
        })))

    with provider as mock_server:
        print("Mock server is running at " + mock_server.get_url())

        todo = TodoConsumer(mock_server.get_url())
        projects = todo.get_projects()

        assert len(projects) == 1
        assert projects[0]['id'] == 1
        assert len(projects[0]['tasks']) == 4
        assert projects[0]['tasks'][0]['id'] != 101


def test_with_xml_requests(provider):
    (provider.given('i have a list of projects')
        .upon_receiving('a request for projects in XML')
        .with_request(method="GET", path="/projects", query={'from': "today"}, headers={'Accept': "application/xml"})
        .will_respond_with(
            headers={"Content-Type": "application/xml"},
            body='''<?xml version="1.0" encoding="UTF-8"?>
                    <projects foo="bar">
                      <project id="1" name="Project 1" due="2016-02-11T09:46:56.023Z">
                        <tasks>
                          <task id="1" name="Do the laundry" done="true"/>
                          <task id="2" name="Do the dishes" done="false"/>
                          <task id="3" name="Do the backyard" done="false"/>
                          <task id="4" name="Do nothing" done="false"/>
                        </tasks>
                      </project>
                      <project/>
                    </projects>'''
            #             body: new XmlBuilder("1.0", "UTF-8", "ns1:projects").build(el => {
            #               el.setAttributes({
            #                 id: "1234",
            #                 "xmlns:ns1": "http://some.namespace/and/more/stuff",
            #               })
            #               el.eachLike(
            #                 "ns1:project",
            #                 {
            #                   id: integer(1),
            #                   type: "activity",
            #                   name: string("Project 1"),
            #                   // TODO: implement XML generators
            #                   // due: timestamp(
            #                   //   "yyyy-MM-dd'T'HH:mm:ss.SZ",
            #                   //   "2016-02-11T09:46:56.023Z"
            #                   // ),
            #                 },
            #                 project => {
            #                   project.appendElement("ns1:tasks", {}, task => {
            #                     task.eachLike(
            #                       "ns1:task",
            #                       {
            #                         id: integer(1),
            #                         name: string("Task 1"),
            #                         done: boolean(true),
            #                       },
            #                       null,
            #                       { examples: 5 }
            #                     )
            #                   })
            #                 },
            #                 { examples: 2 }
            #               )
            #             }),

        ))

    with provider as mock_server:
        print("Mock server is running at " + mock_server.get_url())

        todo = TodoConsumer(mock_server.get_url())
        projects = todo.get_projects('xml')

        assert len(projects) == 2
        assert projects[0].get('id') == '1'
        tasks = projects[0][0].findall('task')
        assert len(tasks) == 4
        assert tasks[0].get('id') == '1'


#     describe("with image uploads", () => {
#       before(() => {
#         provider = new PactV3({
#           consumer: "TodoApp",
#           provider: "TodoServiceV3",
#           dir: path.resolve(process.cwd(), "pacts"),
#         })
#         provider
#           .given("i have a project", { id: "1001", name: "Home Chores" })
#           .uponReceiving("a request to store an image against the project")
#           .withRequestBinaryFile(
#             { method: "POST", path: "/projects/1001/images" },
#             "image/jpeg",
#             path.resolve(__dirname, "example.jpg")
#           )
#           .willRespondWith({ status: 201 })
#       })

#       it("stores the image against the project", async () => {
#         let result = await provider.executeTest(mockserver => {
#           console.log("In Test Function", mockserver)
#           return TodoApp.setUrl(mockserver.url).postImage(
#             1001,
#             path.resolve(__dirname, "example.jpg")
#           )
#         })
#         console.log("result from runTest", result.status)
#         expect(result.status).to.be.eq(201)
#         return result
#       })
#     })
#   })
# })

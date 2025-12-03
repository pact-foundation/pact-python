---
authors:
    - JP-Ellis
date:
    created: 2025-12-04
---

# Announcing: Pact Python v3

It's been a couple of months since we released Pact Python v3, and after ironing out a couple of early issues, I think it's finally time to reflect on this milestone and its implications. This post is a look back at the journey, some of the challenges, the people, and the future of this project within the Pact ecosystem.

<!-- more -->

Pact is an approach to contract testing that sits neatly between traditional unit tests (which check individual components) and end-to-end tests (which exercise the whole system). With Pact, you can verify that your services communicate correctly, without needing to spin up every dependency. By capturing the expected interactions between consumer and provider, Pact allows you to test each side in isolation and replay those interactions, giving you fast, reliable feedback and confidence that your APIs and microservices will work together in the real world. Pact Python brings this powerful workflow to the Python ecosystem, making it easy to test everything from REST APIs to event-driven systems.

## Looking Back: Why v3?

Pact has a diverse ecosystem, with SDKs in all major languages. Pact Python was (and still is) the most popular implementation of Pact for Python. As with many of the early Pact SDKs, Pact Python was built on top of the Pact Ruby codebase, as that was _the_ reference implementation of Pact.

This came with a few problems:

1.  The reference implementation of Pact moved to [Rust](https://github.com/pact-foundation/pact-reference), and development for versions 3 and 4 of the Pact specification took place there, with limited features being backported to Pact Ruby.
2.  It required bundling Ruby as part of the Python wheels, which significantly bloated distributions and slowed down Pact Python.
3.  The Python code served primarily as a wrapper to calling the Ruby-based CLIs, and some aspects of that implementation were exposed to end-users, such as manually checking process exit codes, resulting in a non-"pythonic" experience.

As the Pact specification evolved and the needs of our users grew, it became clear that the old architecture was starting to show its age. Supporting new features, keeping up with upstream changes, and maintaining compatibility across platforms was becoming increasingly difficult.

Version 3 of Pact Python was an opportunity to do things differently. Not only could we move away from the Ruby dependency and unlock support for the latest Pact specifications, but we could also make Pact Python much more "pythonic." This meant embracing modern Python best practices: proper exception handling, context management, full typing, and a more intuitive API. The goal was to make the library feel natural for Python developers, whether they were new to Pact or contract testing veterans.

With these objectives in mind, the development of v3 commenced.

## The Journey: From Idea to Release

Very early in the development of v3, it was clear to me that this was an opportunity to fundamentally rethink the library's architecture. While the core Pact idioms from the broader ecosystem have been retained, the internal flow and structure of Pact Python were comprehensively overhauled. This decision was not made lightly, as it does introduce a burden on end-users; however, I hoped this would provide significant long-term benefits for maintainability, extensibility, and user experience. Now looking back, I do think this was the right decision, and I'm glad that I was allowed to implement these changes even though I was a newcomer to Pact's ecosystem.

Migrating a large codebase from Pact Python v2 to v3 is an onerous task. Accordingly, considerable effort was invested in ensuring compatibility and a smooth transition. This included the preparation of detailed migration guides, the parallel support of both v2 and v3 for an extended period, and the incorporation of feedback from early adopters who trialed the new version in production environments. The ongoing support for v2 alongside v3 is intended to allow users to migrate incrementally and at their own pace.

The development process for v3 was iterative and, at times, complex. There were periods of rapid progress, such as the initial successful execution of contract tests using the new Rust core, as well as periods where platform-specific issues or subtle bugs required significant investigation and resolution (sometimes making me question my most basic reasoning abilities). Throughout, the primary objective remained to ensure that the new implementation not only matched the previous feature set, but also delivered tangible improvements in usability, reliability, and performance.

The support of the PactFlow team at SmartBear was instrumental throughout this process, providing code reviews, testing, and guidance. The broader community also played a crucial role, contributing issues, pull requests, and practical insights that informed many of the design decisions. In particular, feedback and real-world testing from early adopters were invaluable during the preview and stabilization phases, helping to shape the final release.

## What's New in v3?

### Faster, Leaner, and More Reliable

The move to a Rust FFI core is a game changer. Tests run faster, memory usage is lower, and the behaviour is aligned with most Pact SDKs in the ecosystem. I have already noticed significant speed-ups in test suites, and I hope end-users will notice this too. And with full support for both v3 and v4 of the Pact specification, you get access to the latest features, like asynchronous message support and improved matching rules, right out of the box.

### A Truly Pythonic Experience

Pact Python v3 is designed to feel like it belongs in the Python ecosystem. The API has been completely reimagined: context management, proper exception handling, and full type hints are now first-class citizens. The new interface is more intuitive, with less boilerplate and clearer error messages.

Matchers are more expressive and flexible, making it easier to write robust, maintainable tests for even the most complex data structures. Provider state handling is now much more flexible too: you can use plain Python functions to manage test data and state, instead of relying on bespoke HTTP endpoints.

All of this means writing and verifying contracts should feel natural, whether you're new to Pact or a seasoned pro.

What does this look like in practice? Here's a side-by-side comparison of a simple Pact test in v2 and v3:

```python title="Pact Python v2"
from pact.v2 import Consumer, Provider
import requests

consumer = Consumer('my-web-front-end')
provider = Provider('my-backend-service')

pact = consumer.has_pact_with(provider, pact_dir='/path/to/pacts')
(
    pact
    .given('user exists')  # 1
    .upon_receiving('a request for user data')
    .with_request(
        'GET',
        '/users/123',
        headers={'Accept': 'application/json'},
        query={'include': 'profile'}
    )
    .will_respond_with(
        200,
        headers={'Content-Type': 'application/json'},
        body={'id': 123, 'name': 'Alice'}
    )
)

pact.start_service()  # 2
pact.setup()
response = requests.get(pact.uri + '/users/123')
assert response.json() == {'id': 123, 'name': 'Alice'}
pact.verify()         # 3
pact.stop_service()   # 4
# Pact file is written as part of verify() or when the service stops
```

1.  Provider states in v2 are simple strings, which can lead to duplication if you need to test similar states with different parameters.
2.  The mock service must be started manually before running tests.
3.  Verification and Pact file writing are triggered explicitly.
4.  The mock service must be stopped manually after tests.

```python title="Pact Python v3"
from pact import Pact
import requests

pact = Pact('my-web-front-end', 'my-backend-service')
(
    pact
    .upon_receiving('a request for user data')
    .given('user exists', id=123, name='Alice')  # 1
    .with_request('GET', '/users/123')
    .with_header('Accept', 'application/json')
    .with_query_parameter('include', 'profile')
    .will_respond_with(200)
    .with_header('Content-Type', 'application/json')
    .with_body({'id': 123, 'name': 'Alice'}, content_type='application/json')
)

with pact.serve() as srv:  # 2
    response = requests.get(f"{srv.url}/users/123")
    assert response.json() == {'id': 123, 'name': 'Alice'}
pact.write_file('/path/to/pacts')  # 3
```

1.  In v3, provider states can be parameterized, making it easier to reuse and manage test data across different scenarios.
2.  The new `serve()` method provides a more Pythonic and flexible way to run the mock service, automatically handling setup and teardown.
3.  Pact files are written explicitly, giving you more control over when and where they are saved.

### Migration, with You in Mind

We know big upgrades can be daunting, especially for teams with large codebases. That's why v3 includes a backwards compatibility module: you can keep your old tests running while you gradually adopt the new API, at your own pace. Many of the changes in v3 came directly from user feedback; feature requests, bug reports, and discussions on Slack have all shaped this release. The transition is designed to be as smooth as possible, so you can take advantage of new features without disrupting your workflow.

## Reflections and Gratitude

No open source project is a solo effort, and Pact Python v3 is no exception. This release stands on the shoulders of a vibrant community, and I want to take a moment to recognize the many people who have shaped this project.

**Special thanks to the contributors to the v3 codebase:**

-   **[valkolovos](https://github.com/valkolovos):** for his work on matchers, generators, asynchronous message support, and being an early adopter of Pact Python v3.
-   **[Nikhil Arora](https://github.com/Nikhil172913832):** for a number of recent improvements, including improvements to the developer experience.
-   **[Amit Singh](https://github.com/amit828as):** for expanding v3 HTTP interaction examples and real-world testing.
-   **[Kevin Rohan Vaz](https://github.com/kevinrvaz):** For fixing and improving the v3 verifier.

I would also like to acknowledge contributors to the (now legacy) v2 codebase and the original project:

-   **Core architecture and early development:** [Elliott Murray](https://github.com/elliottmurray), [Matthew Balvanz](https://github.com/matthewbalvanz-wf).
-   **Message pact and provider support:** [Tuan Pham](https://github.com/tuan-pham), [William Infante](https://github.com/williaminfante), [Fabio Pulvirenti](https://github.com/pulphix).
-   **Testing and verification:** [Peter Yasi](https://github.com/pyasi), S[imon Nizov](https://github.com/thatguysimon), [mikahjc](https://github.com/mikahjc), [Maciej Olko](https://github.com/m-aciek), [Matt Fellows](https://github.com/mefellows), [Janneck Wullschleger](https://github.com/jawu), [Rory Hart](https://github.com/hartror), [simkev2](https://github.com/SimKev2).
-   **Other features, fixes, and support:** [B3nnyL](https://github.com/B3nnyL), [Yousaf Nabi](https://github.com/YOU54F), [Beth Skurrie](https://github.com/bethesque), [Francois Campbell](https://github.com/francoiscampbell), [Serghei Iakovlev](https://github.com/sergeyklay), and many others over the years.

And certainly not least, a huge thank you to those who have helped with documentation, onboarding, and community support:

-   **Documentation and onboarding:** [Elliott Murray](https://github.com/elliottmurray), [Matthew Balvanz](https://github.com/matthewbalvanz-wf), [Yousaf Nabi](https://github.com/YOU54F), [Beth Skurrie](https://github.com/bethesque), [Matt Fellows](https://github.com/mefellows), [Serghei Iakovlev](https://github.com/sergeyklay).
-   **Examples and reliability:** [mikegeeves](https://github.com/mikegeeves), [William Infante](https://github.com/williaminfante), [Artur Neumann](https://github.com/individual-it).
-   **Community support and feedback:** and everyone who has opened issues, submitted PRs, or shared their experiences, on Slack, GitHub, and elsewhere!

## Where to Next?

With v3 as our new foundation, we are already seeing new features and integrations become possible that would have been out of reach before. If you are using Pact Python in your projects, I would welcome your stories, whether it's a simple 'we're using this', or more feedback on what is working, what could be improved, and what you would like to see next.

If you are ready to get started, you will find everything you need in the [documentation](https://pact-foundation.github.io/pact-python/), including a [migration guide](https://pact-foundation.github.io/pact-python/MIGRATION/) for those moving from v2. The [GitHub repository](https://github.com/pact-foundation/pact-python) is always open for issues, discussions, and contributions. If you are new to Pact entirely, you can read more about it on [`pact.io`](https://pact.io/).

Thank you for being part of this journey. Here's to a new chapter in contract testing for Python. Happy testing!

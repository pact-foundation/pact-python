---
authors:
    - JP-Ellis
date:
    created: 2024-04-11
---

# A Sneak Peek into the Pact Python Future

We are thrilled to announce the release of [Pact Python `v2.2`](https://github.com/pact-foundation/pact-python/releases/tag/v2.2.0), a significant milestone that not only improves upon the existing features but also offers an exclusive preview into the future of contract testing with Python.

## A Glimpse Ahead with [`pact.v3`][pact.v3]

The work is taking shape in a branch-new module – [`pact.v3`][pact.v3] – that serves as an early preview of what will become Pact Python `v3`. This will provide full support for Pact Specifications `v3` and `v4`.

This new version harnesses the power of Rust's foreign function interface (FFI) library, promising enhanced performance and reliability. It will also make it easier to incorporate upstream changes in the future. Although it's just a sneak peek, it's an open invitation for you to explore what's coming and contribute to shaping its final form.

<!-- more -->

## Your Feedback Is Invaluable

The journey toward perfection is never solitary. We count on your insights and experiences to refine our offerings. If you run into any hiccups or have thoughts you'd like to share:

-   Report issues on our GitHub page: [Pact Python Issues](https://github.com/pact-foundation/pact-python/issues).
-   Join the conversation on GitHub discussions: [Pact Python Discussions](https://github.com/pact-foundation/pact-python/discussions).
-   Connect with us on Slack: [Pact Foundation Slack](https://slack.pact.io/).

We eagerly await your input!

## The Roadmap Ahead

Transitioning to a new version can be daunting; thus, we've planned a staged migration:

### :construction: Stage 1 (from v2.2)

-   The existing library remains operational with continued support for minor updates.
-   The new `pact.v3` is available for trial but should be used cautiously as changes are expected.
-   It's not recommended for production use yet, but feedback from experimentation is encouraged.
-   Expect [`PendingDeprecationWarning`](https://docs.python.org/3/library/exceptions.html#PendingDeprecationWarning) alerts when using the current library.

### :hammer_and_wrench: Stage 2 (from v2.3, to be confirmed)

-   The `pact.v3` module is anticipated to stabilize and we urge users to start planning their migration.
-   Comprehensive migration guidance will be provided for a seamless transition.
-   More assertive [`DeprecationWarning`](https://docs.python.org/3/library/exceptions.html#DeprecationWarning) notifications will prompt users to switch to the new module.
-   This phase will provide ample time, likely spanning a few months, for users to adapt.

### :rocket: Stage 3 (from v3)

-   The `pact.v3` module graduates to simply `pact`, signaling its readiness as the primary library.
    -   Migrators from `pact.v3` can expect minimal effort adjustments – mostly a find-and-replace task from `pact.v3` to `pact`.
    -   Any necessary breaking changes identified during Stage 2 will be implemented, with detailed guidance provided.
-   The original library moves under the `pact.v2` umbrella.
    -   This significant shift means that code written for Pact Python v2 will require attention to function with `v3`.
    -   Users loyal to `v2` must update their imports to accommodate the new `pact.v2` scope.
    -   With its move, `pact.v2` steps into the sunset of its lifecycle, focusing on critical fixes until its eventual retirement.

## Embrace the Evolution

Ready to dive in? Check out Pact Python `v2.2` today and start exploring what's ahead with `pact.v3`. As developers and testers, your role in this evolution is pivotal. By engaging with this preview and sharing your findings, you help us refine and perfect the tools you rely on.

We want to make this transition as smooth as possible for our community. We encourage you to explore, test drive the new features, and share your experiences.

Stay tuned for more updates as we progress through each stage of this exciting journey!

Lastly, a big thank you to all our contributors!

Happy testing!

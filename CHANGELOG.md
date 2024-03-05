## v2.1.2 (2024-03-05)

### BREAKING CHANGE

-   The public functions within the constants module have been removed. If you previously used them, please make use of the constants. For example, instead of `pact.constants.broker_client_exe()` use `pact.constants.BROKER_CLIENT_PATH` instead.
-   It is possible to use the system installed Pact executables by setting `PACT_USE_SYSTEM_BINS` to `True` or `Yes` (case insensitive).

### Feat

-   add support for musllinux_aarch64
-   **v3**: add specification attribute to pacts
-   **v3**: upgrade ffi to 0.4.18
-   determine version from vcs
-   **v3**: add with_matching_rules
-   add python 3.12 support
-   **v3**: implement server log methods
-   **v3**: add mock server mismatches
-   **v3**: implement Pact Handle methods
-   **ffi**: add OwnedString class
-   **v3**: implement interaction methods
-   **v3**: implement pact class
-   **v3**: add v3.ffi module

### Fix

-   clean pact interactions on exception
-   **v3**: incorrect arg order
-   **v3**: rename `with_binary_file`
-   **example**: publish message pact
-   **example**: publish_verification_results typo
-   **example**: unknown action
-   **v3**: add `__next__` implementation
-   **deps**: add yarl dependency
-   **v3**: unconventional `__repr__` implementation
-   **build**: include omitted `lib` dir
-   **test**: ignore internal deprecation warnings
-   **ci**: add missing environment

### Refactor

-   **v3**: split interactions into modules
-   refactor constants

## v2.1.1 (2023-10-04)

Identical to 2.1.0, but with a fix to the publication process to PyPI.

## v2.1.0 (2023-10-04)

### BREAKING CHANGE

-   Drop support for Python 3.6 and 3.7

### Feat

-   bump pact standalone to 2.0.7
-   **example**: simplify docker-compose

### Fix

-   **ci**: pypi publish
-   **github**: fix typo in template
-   migrate to pyproject.toml and hatch

## 2.0.1

-   d3397b7 - chore(examples): update docker setup for non linux os (Yousaf Nabi, Tue Jul 25 14:55:42 2023 +0100)
-   ef12e56 - feat: update standalone to 2.0.3 (Yousaf Nabi, Tue Jul 25 14:00:38 2023 +0100)
-   1429d2f - chore: update MANIFEST file to note 2.0.2 standalone (Yousaf Nabi, Tue Jul 25 13:56:08 2023 +0100)

## 2.0.0

-   2a244ea - chore: update to 2.0.2 pact-ruby-standalone (Yousaf Nabi, Sat Jul 8 14:12:18 2023 +0100)
-   819f0a7 - test: v2.0.1 (pact-2.0.1) - pact-ruby-standalone (Yousaf Nabi, Thu May 18 23:30:30 2023 +0100)
-   9bc3e21 - chore(docs): improve table alignment and abs links (Yousaf Nabi, Thu May 4 12:10:39 2023 +0100)
-   80f06cf - chore(docs): correct table (Yousaf Nabi, Wed May 3 19:20:37 2023 +0100)
-   c70573c - chore(docs): update provider verifier options table (Yousaf Nabi, Wed May 3 19:17:28 2023 +0100)
-   fc6ced8 - style: add missing newline/linefeed (Serghei Iakovlev, Thu May 4 09:51:19 2023 +0200)
-   7b14aa3 - build(deps-dev): bump flask from 2.2.2 to 2.2.5 (dependabot[bot], Wed May 3 20:30:31 2023 +0000)
-   a0efd69 - build(deps): bump flask from 2.2.2 to 2.2.5 in /examples/flask_provider (dependabot[bot], Wed May 3 20:30:24 2023 +0000)
-   1267d7d - build(deps): bump flask from 2.2.2 to 2.2.5 in /examples/message (dependabot[bot], Wed May 3 19:51:09 2023 +0000)
-   4e3ca38 - feat: use pact-ruby-standalone 2.0.0 release (Yousaf Nabi, Sat Apr 29 00:43:31 2023 +0100)
-   2c673ea - ci: skip 3.6 python arm64 failing in cirrus, passing locally with cirrus run (Yousaf Nabi, Fri Apr 21 15:46:22 2023 +0100)
-   7aff538 - feat: support x86 and x86_64 windows (Yousaf Nabi, Fri Apr 21 15:44:48 2023 +0100)
-   28440da - ci: test arm64 on cirrus-ci / test win/osx on gh (Yousaf Nabi, Fri Apr 21 15:37:30 2023 +0100)
-   93db8ae - feat: support arm64 osx/linux (Yousaf Nabi, Fri Apr 21 12:35:23 2023 +0100)
-   19be499 - fix: fix cors parameter not doing anything (Lukas Riedersberger, Fri Apr 14 12:22:21 2023 +0200)
-   e721d81 - docs: reformat releasing documentation (Serghei Iakovlev, Wed Apr 5 12:39:35 2023 +0200)
-   71f1529 - chore: do not add merge commits to the change log (Serghei Iakovlev, Wed Apr 5 12:27:49 2023 +0200)
-   9ce2d69 - chore: Releasing version 1.7.0 (Elliott Murray, Sun Feb 19 11:28:01 2023 +0000)
-   429e171 - build: use a single Dockerfile, providing args for the Python version instead of multiple files (Mike Geeves, Mon Apr 3 09:01:37 2023 +0100)
-   e99e7fb - docs: rephrase the instructions for running the tests (Serghei Iakovlev, Sun Apr 2 22:20:07 2023 +0200)
-   a5d3a2e - docs: paraphrase the instructions for running the tests (Serghei Iakovlev, Sun Apr 2 22:19:37 2023 +0200)
-   24c2dbf - docs: fix instruction to build python 3.11 image (Serghei Iakovlev, Sun Apr 2 22:18:10 2023 +0200)
-   55dcaf2 - feat(test): add docker images for Python 3.9-3.11 for testing purposes (Serghei Iakovlev, Fri Mar 17 11:24:42 2023 +0100)
-   28fc7d3 - docs: fix link for GitHub badge (Serghei Iakovlev, Fri Mar 31 22:50:23 2023 +0200)
-   26eaaac - fix: remove dead code (Serghei Iakovlev, Sun Mar 5 02:05:14 2023 +0100)
-   f7c5006 - docs: add Python 3.11 to CONTRIBUTING.md (Serghei Iakovlev, Thu Mar 30 23:22:22 2023 +0200)
-   348bf5e - build: use compatible dependency versions for Python 3.6 (Serghei Iakovlev, Thu Mar 30 23:18:57 2023 +0200)
-   4d9f4cd - feat: describe classifiers and python version for pypi package (Serghei Iakovlev, Sun Mar 5 09:16:29 2023 +0100)
-   7603815 - ci: add python 3.11 to test matrix (Serghei Iakovlev, Sun Mar 5 09:15:23 2023 +0100)
-   bea1563 - doc: improve commit messages guide (Serghei Iakovlev, Sat Mar 4 00:30:56 2023 +0100)
-   60f2aac - doc: correct links in contributing manual (Serghei Iakovlev, Fri Mar 3 21:38:58 2023 +0100)
-   a219f49 - fix: actualize doc on how to make contributions (Serghei Iakovlev, Thu Mar 2 08:56:48 2023 +0100)
-   4919772 - feat: add matchers for ISO 8601 date format (Serghei Iakovlev, Sun Mar 12 16:03:44 2023 +0100)

## 1.7.0

-   44cda33 - chore: /s/Pactflow/PactFlow (Yousaf Nabi, Thu Jan 26 16:11:54 2023 +0000)
-   1bbdd37 - feat: Enhance provider states for pact-message (#322) (nsfrias, Tue Jan 24 17:04:29 2023 +0000)
-   53ca129 - chore: add workflow to create a jira issue for pactflow team when smartbear-supported label added to github issue (Beth Skurrie, Wed Jan 18 10:51:05 2023 +1100)
-   d87d54b - fix: setup security issue (#318) (Elliott Murray, Mon Nov 21 09:39:41 2022 +0000)
-   55f2a64 - fix: requirements_dev.txt to reduce vulnerabilities (#317) (Matt Fellows, Sun Nov 6 02:12:30 2022 +1100)

## 1.6.0

-   ceff89b - Publish verify branches (#306) (Yousaf Nabi, Sun Sep 11 11:33:44 2022 +0100)
-   89733d6 - feat: Support verify with branch (#302) (B3nnyL, Sun Sep 11 20:14:13 2022 +1000)
-   42e0db8 - feat: Support publish pact with branch (#300) (B3nnyL, Sun Sep 11 20:06:27 2022 +1000)
-   80d7b13 - chore(test): fix consumer message test (#301) (B3nnyL, Tue Aug 23 23:50:27 2022 +1000)
-   2015f72 - build: Correct download logic when installing. Add a helper target to setup a pyenv via make (#297) (mikegeeves, Sun Jun 19 09:27:07 2022 +0100)
-   c17ac70 - docs: Update docs to reflect usage for native Python (#227) (Jiayun Fang, Wed Apr 27 10:00:50 2022 -0700)

## 1.5.2

-   25823ae - chore: update PACT_STANDALONE_VERSION to 1.88.83 (#292) (Yousaf Nabi, Mon Mar 21 22:14:40 2022 +0000)

## 1.5.1

-   e645b24 - feat: message_pact -> with_metadata() updated to accept term (#289) (sunsathish88, Tue Mar 8 12:08:34 2022 -0500)
-   b981865 - docs(examples-consumer): add pip install requirements to the consumer… (#291) (mikegeeves, Sun Mar 6 10:12:32 2022 +0000)
-   4c76ae8 - test(examples): move shared fixtures to a common folder so they can b… (#280) (mikegeeves, Sun Mar 6 10:10:11 2022 +0000)

## 1.5.0

-   8085be0 - feat: No include pending (#284) (Abraham Gonzalez, Wed Feb 2 13:20:39 2022 +0100)
-   f169f3b - ci: python36-support-removed (#283) (mikegeeves, Sat Jan 22 10:26:44 2022 +0000)

## 1.4.6

-   6c25844 - chore: flake8 config to ignore direnv (Elliott Murray, Mon Jan 3 18:33:47 2022 +0000)
-   891134a - feat(matcher): Allow bytes type in from_term function (#281) (joshua-badger, Mon Jan 3 11:23:40 2022 -0700)
-   588b55d - fix(consumer): ensure a description is provided for all interactions (#278) (mikegeeves, Thu Dec 30 16:57:03 2021 +0000)
-   02643d4 - test(examples-fastapi): tidy FastAPI example, making consistent with Flask (#274) (mikegeeves, Sun Oct 31 21:52:54 2021 +0000)
-   bf110e2 - docs: Docs/examples (#273) (Elliott Murray, Tue Oct 26 21:54:00 2021 +0100)

## 1.4.5

-   695d51f - fix: update standalone to 1.88.77 to fix Let's Encrypt CA issue (Matt Fellows, Mon Oct 11 13:29:34 2021 +1100)

## 1.4.4

-   b90cf3d - fix(ruby): update ruby standalone to support disabling SSL verification via an environment variable (m-aciek, Sat Oct 2 03:04:14 2021 +0200)

## 1.4.3

-   08f0dc0 - feat: added support for message provider using pact broker (#257) (Fabio Pulvirenti, Sun Sep 5 22:49:51 2021 +0200)

## 1.4.2

-   f2230b6 - chore: Bundle Ruby standalones into dist artifact. (#256) (Taj Pereira, Sun Aug 22 19:53:53 2021 +0930)
-   e370786 - chore: Releasing version 1.4.1 (Elliott Murray, Tue Aug 17 18:55:53 2021 +0100)
-   7dc8864 - fix: make uvicorn versions over 0.14 (#255) (Elliott Murray, Tue Aug 17 18:51:52 2021 +0100)
-   da49cd7 - chore: Releasing version 1.4.0 (Elliott Murray, Sat Aug 7 10:17:26 2021 +0100)
-   0089937 - fix: issue originating from snyk with requests and urllib (#252) (Elliott Murray, Sat Jul 31 12:46:15 2021 +0100)
-   903371b - feat: added support for message provider (#251) (Fabio Pulvirenti, Sat Jul 31 13:24:19 2021 +0200)
-   2c81029 - chore(snyk): update fastapi (#239) (Elliott Murray, Fri Jun 11 09:12:38 2021 +0100)

## 1.4.1

-   7dc8864 - fix: make uvicorn versions over 0.14 (#255) (Elliott Murray, Tue Aug 17 18:51:52 2021 +0100)

## 1.4.0

-   0089937 - fix: issue originating from snyk with requests and urllib (#252) (Elliott Murray, Sat Jul 31 12:46:15 2021 +0100)
-   903371b - feat: added support for message provider (#251) (Fabio Pulvirenti, Sat Jul 31 13:24:19 2021 +0200)
-   2c81029 - chore(snyk): update fastapi (#239) (Elliott Murray, Fri Jun 11 09:12:38 2021 +0100)

## 1.3.9

-   98d9a4b - chore(ruby): update ruby standalen (#233) (Elliott Murray, Thu May 13 20:21:10 2021 +0100)
-   657e770 - fix: change default from empty string to empty list (#235) (Vasile Tofan, Thu May 13 22:20:47 2021 +0300)
-   99fd965 - chore: Releasing version 1.3.8 (Elliott Murray, Sat May 1 12:26:47 2021 +0100)
-   3c909f1 - docs: example uses date matcher (#231) (Elliott Murray, Sat May 1 11:51:28 2021 +0100)
-   6390144 - fix: fix datetime serialization issues in Format (#230) (Syed Muhammad Dawoud Sheraz Ali, Thu Apr 29 01:49:53 2021 +0500)

## 1.3.8

-   3c909f1 - docs: example uses date matcher (#231) (Elliott Murray, Sat May 1 11:51:28 2021 +0100)
-   6390144 - fix: fix datetime serialization issues in Format (#230) (Syed Muhammad Dawoud Sheraz Ali, Thu Apr 29 01:49:53 2021 +0500)

## 1.3.7

-   20f828f - fix(broker): token added to verify steps (#226) (Elliott Murray, Sat Apr 24 13:47:22 2021 +0100)
-   c4fe422 - chore: Releasing version 1.3.6 (Elliott Murray, Tue Apr 20 20:58:50 2021 +0100)
-   34160a8 - fix: publish verification results was wrong (#222) (Elliott Murray, Tue Apr 20 20:58:20 2021 +0100)
-   2c0252c - Merge pull request #219 from pact-foundation/ci/revert_snyk_36 (Elliott Murray, Sat Apr 3 11:13:49 2021 +0100)
-   1a162cf - ci: revert docker36 back (Elliott Murray, Sat Apr 3 11:00:37 2021 +0100)
-   4282de4 - Merge pull request #217 from pact-foundation/snyk-fix-8f994ea63cfa41070b04b182dbd11c74 (Elliott Murray, Sat Apr 3 10:54:58 2021 +0100)
-   4eb3fbb - Merge pull request #216 from pact-foundation/snyk-fix-fc54d9c7fe536fffe78fbd34fc5fd7ea (Elliott Murray, Sat Apr 3 10:54:10 2021 +0100)
-   47373ff - fix: docker/py37.Dockerfile to reduce vulnerabilities (snyk-bot, Fri Apr 2 03:13:49 2021 +0000)
-   e572221 - fix: docker/py38.Dockerfile to reduce vulnerabilities (snyk-bot, Fri Apr 2 01:10:57 2021 +0000)
-   f293dbb - Merge pull request #215 from pact-foundation/snyk-fix-ab489d8931bdf95d6ef0d217aa1b2eb6 (Elliott Murray, Wed Mar 31 09:27:02 2021 +0100)
-   5946872 - fix: docker/py36.Dockerfile to reduce vulnerabilities (snyk-bot, Tue Mar 30 21:41:35 2021 +0000)

## 1.3.6

-   34160a8 - fix: publish verification results was wrong (#222) (Elliott Murray, Tue Apr 20 20:58:20 2021 +0100)
-   2c0252c - Merge pull request #219 from pact-foundation/ci/revert_snyk_36 (Elliott Murray, Sat Apr 3 11:13:49 2021 +0100)
-   1a162cf - ci: revert docker36 back (Elliott Murray, Sat Apr 3 11:00:37 2021 +0100)
-   4282de4 - Merge pull request #217 from pact-foundation/snyk-fix-8f994ea63cfa41070b04b182dbd11c74 (Elliott Murray, Sat Apr 3 10:54:58 2021 +0100)
-   4eb3fbb - Merge pull request #216 from pact-foundation/snyk-fix-fc54d9c7fe536fffe78fbd34fc5fd7ea (Elliott Murray, Sat Apr 3 10:54:10 2021 +0100)
-   47373ff - fix: docker/py37.Dockerfile to reduce vulnerabilities (snyk-bot, Fri Apr 2 03:13:49 2021 +0000)
-   e572221 - fix: docker/py38.Dockerfile to reduce vulnerabilities (snyk-bot, Fri Apr 2 01:10:57 2021 +0000)
-   f293dbb - Merge pull request #215 from pact-foundation/snyk-fix-ab489d8931bdf95d6ef0d217aa1b2eb6 (Elliott Murray, Wed Mar 31 09:27:02 2021 +0100)
-   5946872 - fix: docker/py36.Dockerfile to reduce vulnerabilities (snyk-bot, Tue Mar 30 21:41:35 2021 +0000)
-   d6c5f4a - chore: Releasing version 1.3.5 (Elliott Murray, Sun Mar 28 15:32:45 2021 +0100)
-   5864e47 - Merge pull request #213 from pact-foundation/fix/revert_some_publish (Elliott Murray, Sun Mar 28 15:27:50 2021 +0100)
-   94e597a - fix(publish): fixing the fix. Pact Python api uses only publish_version and ensures it follows that (Elliott Murray, Sun Mar 28 15:20:04 2021 +0100)
-   e00f320 - chore: Releasing version 1.3.4 (Elliott Murray, Sat Mar 27 21:26:29 2021 +0000)
-   c778c71 - Merge pull request #212 from pact-foundation/fix/verify_in_provider (Elliott Murray, Sat Mar 27 18:59:25 2021 +0000)
-   ea0b64a - fix: verifier should now publish (Elliott Murray, Sat Mar 27 16:21:25 2021 +0000)
-   2c8779b - chore: Releasing version 1.3.3 (Elliott Murray, Thu Mar 25 21:23:29 2021 +0000)
-   5e282ff - Merge pull request #211 from anneschuth/fix/pass-pact-dir (Elliott Murray, Thu Mar 25 21:21:56 2021 +0000)
-   987c4fc - fix: pass pact_dir to publish() (Anne Schuth, Thu Mar 25 10:06:54 2021 +0100)
-   23a5129 - chore: Releasing version 1.3.2 (Elliott Murray, Sun Mar 21 14:32:50 2021 +0000)
-   57c8ae8 - Merge pull request #209 from pact-foundation/bug/fix_test_dir (Elliott Murray, Sun Mar 21 14:29:40 2021 +0000)
-   af3dadf - fix: remove pacts from examples (Elliott Murray, Sun Mar 21 14:21:10 2021 +0000)
-   579f3f8 - fix: ensure path is passed to broker and allow running from root rather than test file (Elliott Murray, Sun Mar 21 13:18:01 2021 +0000)
-   7e0feab - Merge pull request #208 from pact-foundation/dependabot/pip/examples/e2e/jinja2-2.11.3 (Elliott Murray, Sat Mar 20 12:46:32 2021 +0000)
-   f82c008 - chore(deps): bump jinja2 from 2.11.2 to 2.11.3 in /examples/e2e (dependabot[bot], Sat Mar 20 04:53:58 2021 +0000)
-   ea6f635 - Merge pull request #206 from pact-foundation/chore/use-testcontainers (Elliott Murray, Sun Mar 14 11:05:01 2021 +0000)
-   565bc80 - chore: added some docs about how to use the e2e example (Elliott Murray, Sun Mar 14 11:02:35 2021 +0000)
-   1b4be80 - chore: spiking testcontainers (Elliott Murray, Sat Mar 13 11:15:52 2021 +0000)
-   01e4ec4 - chore: wip on using test containers on examples (Elliott Murray, Tue Mar 2 21:30:48 2021 +0000)
-   882f4a2 - Merge pull request #204 from pact-foundation/chore/use_pytest (Elliott Murray, Sat Feb 27 10:58:19 2021 +0000)
-   261f24b - chore: more clean up (Elliott Murray, Sat Feb 27 10:10:23 2021 +0000)
-   5a0934c - chore: update ci stuff (Elliott Murray, Sat Feb 27 09:57:31 2021 +0000)
-   66e79e2 - chore: move from nose to pytests as we are now 3.6+ (Elliott Murray, Sat Feb 27 09:34:37 2021 +0000)
-   6aee3e2 - chore: Releasing version 1.3.1 (Elliott Murray, Sat Feb 27 09:16:35 2021 +0000)
-   4440022 - Merge pull request #203 from pact-foundation/fix/version_confusion (Elliott Murray, Sat Feb 27 09:15:08 2021 +0000)
-   9cac2d7 - fix: introduced and renamed specification version (Elliott Murray, Tue Feb 23 21:22:36 2021 +0000)
-   64d7bdc - chore: Releasing version 1.3.0 (Elliott Murray, Tue Jan 26 18:45:58 2021 +0000)
-   eaa90e1 - Merge pull request #194 from williaminfante/feat/pact-message-2 (Elliott Murray, Mon Jan 25 08:48:00 2021 +0000)
-   5ed73db - test: consider publish to broker with no pact_dir argument (William Infante, Mon Jan 25 17:19:08 2021 +1100)
-   e097153 - docs: update readme (William Infante, Mon Jan 25 17:18:35 2021 +1100)
-   fc0d91c - feat: address PR comments (William Infante, Mon Jan 25 10:30:33 2021 +1100)
-   5448d8c - test: remove mock and check generated json file (William Infante, Wed Jan 20 21:07:39 2021 +1100)
-   abd3574 - fix: few more tests to improve coverage (Tuan Pham, Wed Jan 20 09:23:13 2021 +1100)
-   0ef971f - fix: improve test coverage (Tuan Pham, Tue Jan 19 15:11:11 2021 +1100)
-   e543f04 - chore: add missing import (William Infante, Tue Jan 19 13:58:17 2021 +1100)
-   bc7ff78 - chore: pydocstyle (Tuan Pham, Tue Jan 19 10:40:12 2021 +1100)
-   d4235f9 - chore: flake8, clean up deadcode (Tuan Pham, Tue Jan 19 00:53:03 2021 +1100)
-   19827d0 - chore: remove test param for provider (Tuan Pham, Mon Jan 18 16:06:42 2021 +1100)
-   912b477 - chore: flake8 revert (Tuan Pham, Mon Jan 18 16:04:00 2021 +1100)
-   4a730ae - fix: revert changes to quotes (Tuan Pham, Mon Jan 18 15:57:14 2021 +1100)
-   cfe35cc - feat: update message hander to be independent of pact (William Infante, Mon Jan 18 13:12:17 2021 +1100)
-   12b4a50 - fix: flake8 warning (Tuan Pham, Mon Jan 18 12:50:50 2021 +1100)
-   7afe693 - test: update message handler condition based on content (William Infante, Mon Jan 18 12:37:50 2021 +1100)
-   79106bb - feat: move publish function to broker class (Tuan Pham, Mon Jan 18 11:30:35 2021 +1100)
-   a04b954 - docs: add readme for message consumer (William Infante, Mon Jan 18 09:48:01 2021 +1100)
-   8672e2f - feat: update handler to handle error exceptions (William Infante, Fri Jan 15 16:24:38 2021 +1100)
-   47b7434 - feat: change dummy handler to a message handler (William Infante, Fri Jan 15 14:06:55 2021 +1100)
-   a18ce3e - test: create external dummy handler in test (William Infante, Fri Jan 15 12:31:49 2021 +1100)
-   7358049 - chore: remove log_dir, refactor test (Tuan Pham, Fri Jan 15 09:11:55 2021 +1100)
-   6718b4c - feat: update message pact tests (William Infante, Thu Jan 14 16:12:44 2021 +1100)
-   bf9864f - feat: add more test (William Infante, Thu Jan 14 16:09:52 2021 +1100)
-   84681b4 - fix: try different way to mock (Tuan Pham, Thu Jan 14 15:10:36 2021 +1100)
-   86cfe8e - chore: add generate_pact_test (Tuan Pham, Thu Jan 14 14:26:42 2021 +1100)
-   a1c19b6 - fix: add missing conftest (Tuan Pham, Thu Jan 14 11:02:08 2021 +1100)
-   a98850a - chore: add missing files in src (Tuan Pham, Thu Jan 14 10:53:35 2021 +1100)
-   63452aa - chore: fix bad merge (Tuan Pham, Thu Jan 14 10:47:43 2021 +1100)
-   85fc77f - feat: add pact-message integration test (Tuan Pham, Thu Jan 14 10:32:02 2021 +1100)
-   11793f5 - feat: add pact-message integration (Tuan Pham, Thu Jan 14 10:30:35 2021 +1100)
-   8546a26 - fix: linting (Tuan Pham, Thu Jan 14 10:38:52 2021 +1100)
-   65b69d7 - fix: remove publish fn for now (Tuan Pham, Thu Jan 14 10:38:10 2021 +1100)
-   e31dd45 - feat: add constants test (William Infante, Wed Jan 13 17:28:45 2021 +1100)
-   955dbe1 - feat: update MessageConsumer and tests (William Infante, Wed Jan 13 16:38:30 2021 +1100)
-   af5c9fb - feat: create basic tests for single pact message (William Infante, Wed Jan 13 15:52:07 2021 +1100)
-   fea27c8 - feat: single message flow (William Infante, Wed Jan 13 15:03:41 2021 +1100)
-   9047855 - feat: add MessageConsumer (William Infante, Wed Jan 13 12:45:19 2021 +1100)
-   40edd39 - feat: initial interface (William Infante, Tue Jan 12 16:59:46 2021 +1100)
-   2946242 - Merge pull request #198 from pact-foundation/chore/deprecate_python35 (Elliott Murray, Sat Jan 23 15:26:01 2021 +0000)
-   0111698 - fix: add e2e example test into ci back in (Elliott Murray, Sat Jan 23 15:25:07 2021 +0000)
-   0cdc7e9 - chore: remove python35 and 34 and add 39 (Elliott Murray, Sat Jan 23 15:20:47 2021 +0000)
-   3885c60 - Merge pull request #197 from pact-foundation/fix/pull_request_trigger_workflow (Elliott Murray, Sat Jan 23 10:51:06 2021 +0000)
-   925b0ac - ci: pr not triggering workflow (Elliott Murray, Sat Jan 23 10:44:36 2021 +0000)
-   8f9a925 - Merge pull request #195 from cdambo/pass-pact-dir-to-cli (Elliott Murray, Sat Jan 23 10:39:53 2021 +0000)
-   545fc37 - fix: send to cli pact_files with the pact_dir in their path (Chanan Damboritz, Tue Jan 19 18:51:17 2021 +0200)

## 1.3.5

-   5864e47 - Merge pull request #213 from pact-foundation/fix/revert_some_publish (Elliott Murray, Sun Mar 28 15:27:50 2021 +0100)
-   94e597a - fix(publish): fixing the fix. Pact Python api uses only publish_version and ensures it follows that (Elliott Murray, Sun Mar 28 15:20:04 2021 +0100)

## 1.3.4

-   c778c71 - Merge pull request #212 from pact-foundation/fix/verify_in_provider (Elliott Murray, Sat Mar 27 18:59:25 2021 +0000)
-   ea0b64a - fix: verifier should now publish (Elliott Murray, Sat Mar 27 16:21:25 2021 +0000)

## 1.3.3

-   5e282ff - Merge pull request #211 from anneschuth/fix/pass-pact-dir (Elliott Murray, Thu Mar 25 21:21:56 2021 +0000)
-   987c4fc - fix: pass pact_dir to publish() (Anne Schuth, Thu Mar 25 10:06:54 2021 +0100)

### 1.3.2

-   57c8ae8 - Merge pull request #209 from pact-foundation/bug/fix_test_dir (Elliott Murray, Sun Mar 21 14:29:40 2021 +0000)
-   af3dadf - fix: remove pacts from examples (Elliott Murray, Sun Mar 21 14:21:10 2021 +0000)
-   579f3f8 - fix: ensure path is passed to broker and allow running from root rather than test file (Elliott Murray, Sun Mar 21 13:18:01 2021 +0000)
-   7e0feab - Merge pull request #208 from pact-foundation/dependabot/pip/examples/e2e/jinja2-2.11.3 (Elliott Murray, Sat Mar 20 12:46:32 2021 +0000)
-   f82c008 - chore(deps): bump jinja2 from 2.11.2 to 2.11.3 in /examples/e2e (dependabot[bot], Sat Mar 20 04:53:58 2021 +0000)
-   ea6f635 - Merge pull request #206 from pact-foundation/chore/use-testcontainers (Elliott Murray, Sun Mar 14 11:05:01 2021 +0000)
-   565bc80 - chore: added some docs about how to use the e2e example (Elliott Murray, Sun Mar 14 11:02:35 2021 +0000)
-   1b4be80 - chore: spiking testcontainers (Elliott Murray, Sat Mar 13 11:15:52 2021 +0000)
-   01e4ec4 - chore: wip on using test containers on examples (Elliott Murray, Tue Mar 2 21:30:48 2021 +0000)
-   882f4a2 - Merge pull request #204 from pact-foundation/chore/use_pytest (Elliott Murray, Sat Feb 27 10:58:19 2021 +0000)
-   261f24b - chore: more clean up (Elliott Murray, Sat Feb 27 10:10:23 2021 +0000)
-   5a0934c - chore: update ci stuff (Elliott Murray, Sat Feb 27 09:57:31 2021 +0000)
-   66e79e2 - chore: move from nose to pytests as we are now 3.6+ (Elliott Murray, Sat Feb 27 09:34:37 2021 +0000)

## 1.3.1

-   4440022 - Merge pull request #203 from pact-foundation/fix/version_confusion (Elliott Murray, Sat Feb 27 09:15:08 2021 +0000)
-   9cac2d7 - fix: introduced and renamed specification version (Elliott Murray, Tue Feb 23 21:22:36 2021 +0000)

## 1.3.0

-   eaa90e1 - Merge pull request #194 from williaminfante/feat/pact-message-2 (Elliott Murray, Mon Jan 25 08:48:00 2021 +0000)
-   5ed73db - test: consider publish to broker with no pact_dir argument (William Infante, Mon Jan 25 17:19:08 2021 +1100)
-   e097153 - docs: update readme (William Infante, Mon Jan 25 17:18:35 2021 +1100)
-   fc0d91c - feat: address PR comments (William Infante, Mon Jan 25 10:30:33 2021 +1100)
-   5448d8c - test: remove mock and check generated json file (William Infante, Wed Jan 20 21:07:39 2021 +1100)
-   abd3574 - fix: few more tests to improve coverage (Tuan Pham, Wed Jan 20 09:23:13 2021 +1100)
-   0ef971f - fix: improve test coverage (Tuan Pham, Tue Jan 19 15:11:11 2021 +1100)
-   e543f04 - chore: add missing import (William Infante, Tue Jan 19 13:58:17 2021 +1100)
-   bc7ff78 - chore: pydocstyle (Tuan Pham, Tue Jan 19 10:40:12 2021 +1100)
-   d4235f9 - chore: flake8, clean up deadcode (Tuan Pham, Tue Jan 19 00:53:03 2021 +1100)
-   19827d0 - chore: remove test param for provider (Tuan Pham, Mon Jan 18 16:06:42 2021 +1100)
-   912b477 - chore: flake8 revert (Tuan Pham, Mon Jan 18 16:04:00 2021 +1100)
-   4a730ae - fix: revert changes to quotes (Tuan Pham, Mon Jan 18 15:57:14 2021 +1100)
-   cfe35cc - feat: update message hander to be independent of pact (William Infante, Mon Jan 18 13:12:17 2021 +1100)
-   12b4a50 - fix: flake8 warning (Tuan Pham, Mon Jan 18 12:50:50 2021 +1100)
-   7afe693 - test: update message handler condition based on content (William Infante, Mon Jan 18 12:37:50 2021 +1100)
-   79106bb - feat: move publish function to broker class (Tuan Pham, Mon Jan 18 11:30:35 2021 +1100)
-   a04b954 - docs: add readme for message consumer (William Infante, Mon Jan 18 09:48:01 2021 +1100)
-   8672e2f - feat: update handler to handle error exceptions (William Infante, Fri Jan 15 16:24:38 2021 +1100)
-   47b7434 - feat: change dummy handler to a message handler (William Infante, Fri Jan 15 14:06:55 2021 +1100)
-   a18ce3e - test: create external dummy handler in test (William Infante, Fri Jan 15 12:31:49 2021 +1100)
-   7358049 - chore: remove log_dir, refactor test (Tuan Pham, Fri Jan 15 09:11:55 2021 +1100)
-   6718b4c - feat: update message pact tests (William Infante, Thu Jan 14 16:12:44 2021 +1100)
-   bf9864f - feat: add more test (William Infante, Thu Jan 14 16:09:52 2021 +1100)
-   84681b4 - fix: try different way to mock (Tuan Pham, Thu Jan 14 15:10:36 2021 +1100)
-   86cfe8e - chore: add generate_pact_test (Tuan Pham, Thu Jan 14 14:26:42 2021 +1100)
-   a1c19b6 - fix: add missing conftest (Tuan Pham, Thu Jan 14 11:02:08 2021 +1100)
-   a98850a - chore: add missing files in src (Tuan Pham, Thu Jan 14 10:53:35 2021 +1100)
-   63452aa - chore: fix bad merge (Tuan Pham, Thu Jan 14 10:47:43 2021 +1100)
-   85fc77f - feat: add pact-message integration test (Tuan Pham, Thu Jan 14 10:32:02 2021 +1100)
-   11793f5 - feat: add pact-message integration (Tuan Pham, Thu Jan 14 10:30:35 2021 +1100)
-   8546a26 - fix: linting (Tuan Pham, Thu Jan 14 10:38:52 2021 +1100)
-   65b69d7 - fix: remove publish fn for now (Tuan Pham, Thu Jan 14 10:38:10 2021 +1100)
-   e31dd45 - feat: add constants test (William Infante, Wed Jan 13 17:28:45 2021 +1100)
-   955dbe1 - feat: update MessageConsumer and tests (William Infante, Wed Jan 13 16:38:30 2021 +1100)
-   af5c9fb - feat: create basic tests for single pact message (William Infante, Wed Jan 13 15:52:07 2021 +1100)
-   fea27c8 - feat: single message flow (William Infante, Wed Jan 13 15:03:41 2021 +1100)
-   9047855 - feat: add MessageConsumer (William Infante, Wed Jan 13 12:45:19 2021 +1100)
-   40edd39 - feat: initial interface (William Infante, Tue Jan 12 16:59:46 2021 +1100)
-   2946242 - Merge pull request #198 from pact-foundation/chore/deprecate_python35 (Elliott Murray, Sat Jan 23 15:26:01 2021 +0000)
-   0111698 - fix: add e2e example test into ci back in (Elliott Murray, Sat Jan 23 15:25:07 2021 +0000)
-   0cdc7e9 - chore: remove python35 and 34 and add 39 (Elliott Murray, Sat Jan 23 15:20:47 2021 +0000)
-   3885c60 - Merge pull request #197 from pact-foundation/fix/pull_request_trigger_workflow (Elliott Murray, Sat Jan 23 10:51:06 2021 +0000)
-   925b0ac - ci: pr not triggering workflow (Elliott Murray, Sat Jan 23 10:44:36 2021 +0000)
-   8f9a925 - Merge pull request #195 from cdambo/pass-pact-dir-to-cli (Elliott Murray, Sat Jan 23 10:39:53 2021 +0000)
-   545fc37 - fix: send to cli pact_files with the pact_dir in their path (Chanan Damboritz, Tue Jan 19 18:51:17 2021 +0200)

## 1.2.11

-   ba10318 - Merge pull request #192 from pact-foundation/fix/deploy_wheel_fix (Elliott Murray, Tue Dec 29 20:05:52 2020 +0000)
-   289e784 - fix: not creating wheel (Elliott Murray, Tue Dec 29 20:00:19 2020 +0000)
-   d217e67 - chore: Releasing version 1.2.10 (Elliott Murray, Sat Dec 19 12:41:02 2020 +0000)
-   9438449 - Merge pull request #191 from pact-foundation/build-and-test-with-github-actions (Elliott Murray, Sat Dec 19 12:38:23 2020 +0000)
-   2796ef5 - docs: Added badge to README (Elliott Murray, Sat Dec 19 09:37:22 2020 +0000)
-   f1b6968 - ci: add publishing actions (Matthew Balvanz, Thu Dec 17 09:09:10 2020 -0600)
-   287a32e - ci: removed Travis CI configuration (Matthew Balvanz, Wed Dec 16 21:18:09 2020 -0600)
-   77dd4d5 - ci(github actions): added Github Actions configuration for build and test (Matthew Balvanz, Wed Dec 16 21:07:06 2020 -0600)
-   d6f02ca - Merge pull request #189 from noelslice/master (Elliott Murray, Fri Dec 4 08:39:33 2020 +0000)
-   c24a73f - docs: typo in pact-verifier help string: PUT -> POST for --provider-states-setup-url (Noel Dawe, Thu Dec 3 22:39:31 2020 -0500)
-   4cdabd1 - Merge pull request #188 from pact-foundation/docs/example/fastapi (Elliott Murray, Sun Nov 29 14:53:24 2020 +0000)
-   6728cb9 - docs(example): created example and have relative imports kinda working. Provider not working as it cant find one of our urls (Elliott Murray, Sun Nov 29 13:34:42 2020 +0000)
-   9358097 - Merge pull request #184 from pact-foundation/chore/update_python_version (Elliott Murray, Sat Nov 28 10:06:53 2020 +0000)
-   48a2a21 - Merge pull request #186 from jstoebel/patch-2 (Elliott Murray, Sat Nov 21 10:39:48 2020 +0000)
-   74f9a4f - docs: fix small typo in `with_request` doc string (Jacob Stoebel, Wed Nov 18 14:51:03 2020 -0500)
-   4e4ed26 - chore: added run test to travis (Elliott Murray, Sun Nov 1 11:49:38 2020 +0000)
-   37e2f3a - chore: wqshell script to run flask in exmaples (Elliott Murray, Sun Nov 1 11:41:59 2020 +0000)
-   b5d9d7b - chore(upgrade): upgrade python version to 3.8 (Elliott Murray, Sun Nov 1 11:12:10 2020 +0000)

## 1.2.10

-   9438449 - Merge pull request #191 from pact-foundation/build-and-test-with-github-actions (Elliott Murray, Sat Dec 19 12:38:23 2020 +0000)
-   2796ef5 - docs: Added badge to README (Elliott Murray, Sat Dec 19 09:37:22 2020 +0000)
-   f1b6968 - ci: add publishing actions (Matthew Balvanz, Thu Dec 17 09:09:10 2020 -0600)
-   287a32e - ci: removed Travis CI configuration (Matthew Balvanz, Wed Dec 16 21:18:09 2020 -0600)
-   77dd4d5 - ci(github actions): added Github Actions configuration for build and test (Matthew Balvanz, Wed Dec 16 21:07:06 2020 -0600)
-   d6f02ca - Merge pull request #189 from noelslice/master (Elliott Murray, Fri Dec 4 08:39:33 2020 +0000)
-   c24a73f - docs: typo in pact-verifier help string: PUT -> POST for --provider-states-setup-url (Noel Dawe, Thu Dec 3 22:39:31 2020 -0500)
-   4cdabd1 - Merge pull request #188 from pact-foundation/docs/example/fastapi (Elliott Murray, Sun Nov 29 14:53:24 2020 +0000)
-   6728cb9 - docs(example): created example and have relative imports kinda working. Provider not working as it cant find one of our urls (Elliott Murray, Sun Nov 29 13:34:42 2020 +0000)
-   9358097 - Merge pull request #184 from pact-foundation/chore/update_python_version (Elliott Murray, Sat Nov 28 10:06:53 2020 +0000)
-   48a2a21 - Merge pull request #186 from jstoebel/patch-2 (Elliott Murray, Sat Nov 21 10:39:48 2020 +0000)
-   74f9a4f - docs: fix small typo in `with_request` doc string (Jacob Stoebel, Wed Nov 18 14:51:03 2020 -0500)
-   4e4ed26 - chore: added run test to travis (Elliott Murray, Sun Nov 1 11:49:38 2020 +0000)
-   37e2f3a - chore: wqshell script to run flask in exmaples (Elliott Murray, Sun Nov 1 11:41:59 2020 +0000)
-   b5d9d7b - chore(upgrade): upgrade python version to 3.8 (Elliott Murray, Sun Nov 1 11:12:10 2020 +0000)

## 1.2.9

-   4430681 - Merge pull request #183 from thatguysimon/feat/verifier-class-consumer-version-selectors (Elliott Murray, Mon Oct 19 15:35:47 2020 +0100)
-   683a931 - fix: Fix flaky tests using OrderedDict (Simon Nizov, Mon Oct 19 17:21:21 2020 +0300)
-   33be267 - style: Fix one more linting issue (Simon Nizov, Mon Oct 19 11:22:05 2020 +0300)
-   e7c87ce - style: Fix linting issues (Simon Nizov, Mon Oct 19 11:16:59 2020 +0300)
-   ee2eda0 - feat(verifier): Allow setting consumer_version_selectors on Verifier (Simon Nizov, Mon Oct 19 11:01:18 2020 +0300)

## 1.2.8

-   4c68fd4 - Merge pull request #182 from thatguysimon/feat/enable-wip-pacts (Elliott Murray, Sat Oct 17 16:00:50 2020 +0100)
-   9ea14d3 - refactor: Extract input validation in call_verify out into a dedicated method (Simon Nizov, Sat Oct 17 17:27:49 2020 +0300)
-   5a5969d - fix: Fix command building bug (Simon Nizov, Sat Oct 17 15:40:55 2020 +0300)
-   b8c0006 - style: Fix linting (Simon Nizov, Sat Oct 17 15:18:29 2020 +0300)
-   fc3d7ae - feat(verifier): Support include-wip-pacts-since in CLI (Simon Nizov, Sat Oct 17 15:03:38 2020 +0300)
-   a0eca4c - Merge pull request #180 from elliottmurray/docs/example_flaskr (Elliott Murray, Fri Oct 16 11:13:11 2020 +0100)
-   a8a07d4 - docs(examples): changed provider example to use atexit (Elliott Murray, Fri Oct 16 10:54:25 2020 +0100)
-   186f4f4 - Merge pull request #179 from pact-foundation/docs/example_readme (Elliott Murray, Thu Oct 15 10:13:13 2020 +0100)
-   2f66618 - docs(examples): tweak to readme (Elliott Murray, Thu Oct 15 10:08:52 2020 +0100)

## 1.2.7

-   90b71d2 - Merge pull request #178 from pact-foundation/fix/custom_header_typo (Elliott Murray, Fri Oct 9 12:47:37 2020 +0100)
-   b07ef69 - fix(verifier): headers not propogated properly (Elliott Murray, Fri Oct 9 12:24:25 2020 +0100)
-   0e9b71c - Merge pull request #177 from pact-foundation/docs/remove_handcrafted_broker (Elliott Murray, Fri Oct 9 12:01:24 2020 +0100)
-   2db7008 - docs(examples): removed manaul publish to broker (Elliott Murray, Fri Oct 9 11:54:30 2020 +0100)

## 1.2.6

-   1192bd6 - Merge pull request #173 from copalco/master (Elliott Murray, Thu Sep 10 15:30:07 2020 +0100)
-   5db7100 - feat(verifier): allow to use unauthenticated brokers (Piotr Kopalko, Thu Sep 10 14:12:12 2020 +0200)

## 1.2.5

-   46372c7 - Merge pull request #171 from m-aciek/enable-pending (Elliott Murray, Wed Sep 9 10:03:02 2020 +0100)
-   e840587 - fix(verifier): remove superfluous verbose mentions (Maciej Olko, Sat Sep 5 21:33:52 2020 +0200)
-   c64bec1 - refactor(verifier): add enable_pending to signature of verify methods (Maciej Olko, Sat Sep 5 21:32:33 2020 +0200)
-   e6c9ed0 - feat(verifier): support --enable-pending flag in CLI (Maciej Olko, Thu Sep 3 15:33:40 2020 +0200)
-   2b57446 - feat(verifier): pass enable_pending flag in Verifier's methods (Maciej Olko, Thu Sep 3 17:03:08 2020 +0200)
-   d51c88d - test: bump mock to 3.0.5 (m-aciek, Thu Sep 3 23:42:00 2020 +0200)
-   39de1f3 - feat(verifier): add enable_pending argument handling in verify wrapper (Maciej Olko, Thu Sep 3 15:33:07 2020 +0200)
-   fc6c365 - fix(verifier): remove superfluous option from verify CLI command (Maciej Olko, Thu Sep 3 13:30:57 2020 +0200)
-   fbbd5fa - ci(pre-commit): add commitizen to pre-commit configuration (Maciej Olko, Thu Sep 3 17:19:45 2020 +0200)

## 1.2.4

-   a594e22 - Merge pull request #170 from alecgerona/feat/consumer-version-selector (Elliott Murray, Thu Aug 27 15:21:45 2020 +0100)
-   05c5e41 - docs(cli): improve cli help grammar (Alexandre Gerona, Thu Aug 27 06:28:56 2020 +0800)
-   49d5f7c - docs: update README.md with relevant option documentation (Alexandre Gerona, Thu Aug 27 06:22:37 2020 +0800)
-   5a99528 - feat(cli): add consumer-version-selector option (Alexandre Gerona, Thu Aug 27 06:22:07 2020 +0800)

## 1.2.3

-   8188d88 - chore: fix release script (Elliott Murray, Wed Aug 26 12:46:10 2020 +0100)
-   e0e5106 - Merge pull request #169 from pact-foundation/chore/update_pr_scripts (Elliott Murray, Wed Aug 26 10:24:47 2020 +0100)
-   81fd653 - chore: release script updates version automaitcally now (Elliott Murray, Wed Aug 26 10:16:14 2020 +0100)
-   773d3f9 - chore: script now uses gh over hub (Elliott Murray, Wed Aug 26 10:03:06 2020 +0100)
-   468e4ad - Merge pull request #168 from pact-foundation/chore/upgrade-to-pact-ruby-standalone-1-88-3 (Elliott Murray, Wed Aug 26 09:49:33 2020 +0100)
-   ce944fe - feat: update standalone to 1.88.3 (Elliott Murray, Wed Aug 26 09:08:27 2020 +0100)

## 1.2.2

-   2c52053 - Merge pull request #167 from pact-foundation/feat/add_env_vars_verify (Elliott Murray, Mon Aug 24 16:08:04 2020 +0100)
-   ce62588 - feat: added env vars for broker verify (Elliott Murray, Mon Aug 24 16:03:44 2020 +0100)
-   880fff2 - Merge pull request #165 from pact-foundation/docs/https_fix (Elliott Murray, Thu Aug 20 12:43:12 2020 +0100)
-   1a3605e - docs: https svg (Elliott Murray, Thu Aug 20 12:37:01 2020 +0100)

## 1.2.1

-   69a4a9a - Merge pull request #163 from elliottmurray/fix/custom_header (Elliott Murray, Sat Aug 8 10:17:20 2020 +0100)
-   88b7d9f - fix: custom headers had a typo (Elliott Murray, Sat Aug 1 11:08:54 2020 +0100)
-   f501f19 - Merge pull request #161 from pact-foundation/docs/verifier_docs_examples (Elliott Murray, Fri Jul 24 12:30:35 2020 +0100)
-   9875c71 - docs: merged 2 examples (Elliott Murray, Fri Jul 24 12:00:37 2020 +0100)
-   6f0d3ac - docs: Example code verifier (Elliott Murray, Fri Jul 24 11:31:17 2020 +0100)

## 1.2.0

-   2b844c5 - Merge pull request #159 from pact-foundation/feat/fix_provider_classs (Elliott Murray, Fri Jul 24 09:47:46 2020 +0100)
-   9c565bb - feat: fixing up tests and examples and code for provider class (Elliott Murray, Mon Jul 20 15:57:49 2020 +0100)
-   d4072ed - Merge pull request #156 from pact-foundation/feat/provider_verifier (Elliott Murray, Thu Jul 16 13:31:18 2020 +0100)
-   926a611 - feat: create beta verifier class and api (Elliott Murray, Wed Jun 10 21:31:47 2020 +0100)
-   4635a07 - chore: added semantic yml for git messages (Elliott Murray, Sun Jun 28 12:43:24 2020 +0100)
-   ff9894a - Merge pull request #154 from elliottmurray/style/git_message (Elliott Murray, Sat Jun 27 13:31:16 2020 +0100)
-   be6697f - fix: change to head from master (Elliott Murray, Sat Jun 27 13:08:08 2020 +0100)

## 1.1.0

-   1079417 - test (Elliott Murray, Thu Jun 25 10:02:14 2020 +0100)
-   7fe1ef4 - Releasing version 1.1.0 (Elliott Murray, Thu Jun 25 09:41:42 2020 +0100)
-   fafc3d5 - Merge pull request #147 from pact-foundation/feat/add_logging_params (Elliott Murray, Thu Jun 25 09:24:34 2020 +0100)
-   8ce7d44 - Added logging params (Elliott Murray, Wed Jun 24 11:58:25 2020 +0100)
-   b6450b8 - Merge pull request #146 from pact-foundation/chore/upgrade-to-pact-ruby-standalone-1-86-0 (Elliott Murray, Wed Jun 24 10:59:29 2020 +0100)
-   bf43d8a - feat: update standalone to 1.86.0 (Beth Skurrie, Wed Jun 24 09:31:18 2020 +1000)
-   529dfb7 - Merge pull request #145 from jstoebel/patch-1 (Elliott Murray, Thu Jun 11 12:00:51 2020 +0100)
-   9359d34 - Remove typo from examples/e2e requirements.txt (Jacob Stoebel, Thu Jun 11 06:47:02 2020 -0400)
-   aee95ed - Merge pull request #144 from pact-foundation/chore_cleanup (Elliott Murray, Wed Jun 10 21:38:12 2020 +0100)
-   9c71ea0 - chore: removed some files and moved a few things around (Elliott Murray, Wed Jun 10 21:33:37 2020 +0100)

## v1.0.1

-   8c78ff7 - Releasing version 1.0.1 (Elliott Murray, Wed Jun 3 11:01:39 2020 +0100)
-   63f0e3e - Merge pull request #142 from elliottmurray/ssl_verify (Elliott Murray, Wed Jun 3 09:50:10 2020 +0100)
-   cd43bd0 - Removed coverage (Elliott Murray, Tue Jun 2 21:41:52 2020 +0100)
-   30e6f86 - Fixed flake (Elliott Murray, Tue Jun 2 21:32:01 2020 +0100)
-   1a11320 - Fix unit tests (Elliott Murray, Tue Jun 2 21:29:56 2020 +0100)
-   353d054 - travis code coverage (Elliott Murray, Tue Jun 2 21:14:37 2020 +0100)
-   c08babd - Fixing unit tests command in tox and travis (Elliott Murray, Tue Jun 2 18:30:10 2020 +0100)
-   157676c - Allowed https communication to mock. Didnt fix tests (Elliott Murray, Tue Jun 2 17:47:08 2020 +0100)
-   60c9f5a - Fix deploy to pypi2 (Elliott Murray, Fri May 22 13:50:41 2020 +0100)
-   e2c7e4e - Fix deploy to pypi (Elliott Murray, Fri May 22 13:41:27 2020 +0100)

## v1.0.0

-   2c6e4eb - Releasing version 1.0.0 (Elliott Murray, Fri May 22 13:30:49 2020 +0100)
-   c68ccb7 - Merge pull request #140 from elliottmurray/python2_deprecate (Elliott Murray, Fri May 22 13:29:38 2020 +0100)
-   8bc6d48 - Release script to make life a bit easier (Elliott Murray, Thu May 21 12:32:27 2020 +0100)
-   a845f71 - Removed 2.x support (Elliott Murray, Thu May 21 12:19:16 2020 +0100)
-   562e047 - Merge pull request #138 from pyasi/pyasi_add_matcher_regexes (Elliott Murray, Fri May 15 14:10:28 2020 +0100)
-   db39d87 - remove virtualenv (Peter Yasi, Fri May 15 09:02:01 2020 -0400)
-   cccd30a - Add Format to the standard pact package (Peter Yasi, Fri May 15 08:55:57 2020 -0400)
-   b78ac6d - Merge branch 'master' into pyasi_add_matcher_regexes (Peter Yasi, Fri May 15 08:13:30 2020 -0400)
-   35dfa0d - add enum34 a a dep for py27-install (Peter Yasi, Thu May 14 20:52:09 2020 -0400)
-   1fcc6c1 - Pydocstyle fixes, will still need fix for no enum in 2.7 (Peter Yasi, Thu May 14 19:49:23 2020 -0400)
-   fe068e5 - Add examples to e2e tests (Peter Yasi, Thu May 14 19:07:31 2020 -0400)
-   5aaa82f - README documentation (Peter Yasi, Thu May 14 18:46:42 2020 -0400)
-   0d588f7 - pydocs and formatting (Peter Yasi, Thu May 14 18:19:32 2020 -0400)
-   a21118c - Use raw strings to avoid deprecated escape sequence (Peter Yasi, Thu May 14 08:54:01 2020 -0400)
-   715d10f - Initial implementation with example unit tests (Peter Yasi, Thu May 14 00:00:30 2020 -0400)

## 0.22.0

-   d112a4a - Merge pull request #134 from elliottmurray/multiple-custom-provider-header (Elliott Murray, Mon May 11 16:32:49 2020 +0100)
-   58f8e6b - Fix some style issues (Elliott Murray, Wed Apr 29 12:35:00 2020 +0100)
-   bf9bc2d - Added multiple click options for custom headers (Elliott Murray, Tue Apr 28 18:14:02 2020 +0100)
-   254ffc5 - Merge pull request #130 from elliottmurray/examples (Elliott Murray, Sat May 9 18:02:46 2020 +0100)
-   3898aee - Created examples folder (Elliott Murray, Thu Apr 2 14:03:17 2020 +0100)
-   b859443 - Merge pull request #129 from elliottmurray/docker (Elliott Murray, Sat May 9 17:54:01 2020 +0100)
-   9b83da7 - Added bash to containers (Elliott Murray, Fri Apr 10 11:52:43 2020 +0100)
-   73db8fc - Remove subprocess requirement (Elliott Murray, Fri Apr 10 11:32:38 2020 +0100)
-   f3315a1 - Added 38 and created build helper script (Elliott Murray, Wed Apr 1 17:11:06 2020 +0100)
-   e7743de - Some readme and python37 (Elliott Murray, Wed Apr 1 14:25:20 2020 +0100)
-   515aeb2 - Tweaked the run script (Elliott Murray, Wed Apr 1 12:57:02 2020 +0100)
-   5a6acaf - Merge pull request #131 from elliottmurray/python38 (Elliott Murray, Sat May 9 17:47:13 2020 +0100)
-   bb921eb - Updated to 3.8 (Elliott Murray, Sat Apr 4 16:39:18 2020 +0100)
-   12108c4 - Merge pull request #132 from pyasi/pyasi_test_refactor (Elliott Murray, Sat May 9 17:33:59 2020 +0100)
-   48ad173 - Merge pull request #135 from m-aciek/master (Elliott Murray, Sat May 9 17:21:52 2020 +0100)
-   6948482 - Merge pull request #136 from pact-foundation/chore/upgrade-to-pact-ruby-standalone-1-84-0 (Elliott Murray, Sat May 9 15:13:07 2020 +0100)
-   14603ac - feat: update standalone to 1.84.0 (Beth Skurrie, Sat May 2 09:43:30 2020 +1000)
-   410caf1 - chore: add script to create a PR to update the pact-ruby-standalone version (Beth Skurrie, Sat May 2 09:42:55 2020 +1000)
-   b5af1fc - Fix missing normalization of consumer name while publishing pact (Maciej Olko, Thu Apr 30 08:50:17 2020 +0200)
-   5785782 - Move tests to standard tests dir (Peter Yasi, Fri Apr 17 14:03:04 2020 -0400)
-   88ea23d - docs: update RELEASING.md (Beth Skurrie, Tue Feb 18 10:46:11 2020 +1100)

## 0.21.0

-   6352dda - feat: update to pact-ruby-standalone-1.79.0 (#127) (Beth Skurrie, Tue Feb 18 10:25:59 2020 +1100)
-   758d6ea - Converting to kwargs (Elliott Murray, Sat Feb 1 16:24:49 2020 +1100)
-   1388b8f - feat: support using environment variables to set pact broker configuration (mikahjc, Wed Jan 29 17:52:33 2020 -0700)
-   ec7ff99 - Make verify tests compatible with Click v7.x (mikahjc, Tue Jun 11 16:37:13 2019 -0600)
-   5dcb56c - Add broker_token parameter for authentication (mikahjc, Tue Jun 11 16:16:46 2019 -0600)
-   1bdfb42 - Integrate the Ruby pact broker client to allow for automatic publishing of pacts (mikahjc, Tue Jun 11 11:13:18 2019 -0600)

## 0.20.0

-   978d9f3 - fix typo (Jingjing Duan, Wed May 24 15:48:43 2017 -0700)
-   4ede7d5 - Merge pull request #117 from dlmiddlecote/feature/expose-more-options (Matt Fellows, Fri Jan 17 10:00:56 2020 +1100)
-   73ae8d2 - Update docs (Daniel Middlecote, Tue Jan 14 22:11:40 2020 +0000)
-   2bffe5e - Simple test case (Daniel Middlecote, Tue Jan 14 22:11:25 2020 +0000)
-   3ba51b5 - Add --broker-token support (Daniel Middlecote, Tue Jan 14 22:04:39 2020 +0000)
-   d3a8ba6 - Update pact-ruby-standalone (Daniel Middlecote, Tue Jan 14 21:45:01 2020 +0000)
-   0cbb9d4 - Merge pull request #115 from ejrb/patch-1 (Matthew Balvanz, Sat Dec 14 20:49:56 2019 -0600)
-   0c85502 - match platforms like 'macOS-\*' to osx suffix (ejrb, Mon Dec 9 11:13:19 2019 +0000)
-   9a0eaa7 - Merge pull request #109 from pact-foundation/dependabot/pip/flask-1.0 (Matthew Balvanz, Mon Sep 30 21:35:20 2019 -0500)
-   6f70a28 - Bump flask from 0.11.1 to 1.0 (dependabot[bot], Sat Sep 28 19:20:11 2019 +0000)

## 0.19.0

-   fed5fba - Start testing in Python 3.7 (Matthew Balvanz, Sat Sep 28 15:18:17 2019 -0500)
-   19aa689 - Adjust tests to support click 2.0.0 to 7.0.0 (Matthew Balvanz, Sat Sep 28 15:04:53 2019 -0500)
-   9d4d6f3 - Merge pull request #94 from yangineer/optional_given (Matthew Balvanz, Sat Sep 28 14:52:49 2019 -0500)
-   b286b30 - Merge branch 'master' into optional_given (Matthew Balvanz, Sat Sep 28 14:50:02 2019 -0500)
-   68e792a - Merge pull request #93 from francoiscampbell/pass_file_write_mode (Matthew Balvanz, Sat Sep 28 14:18:59 2019 -0500)
-   8927df6 - Updated the tests for Click v7 (Yang Wang, Sat Oct 20 00:34:37 2018 -0400)
-   125a1de - Changed given to be optional (Yang Wang, Sat Oct 20 00:27:07 2018 -0400)
-   68527e0 - max out click at 6.7 because 7.0 fails tests (Francois Campbell, Thu Oct 4 10:57:13 2018 -0400)
-   2452f42 - update tests (Francois Campbell, Thu Oct 4 10:56:42 2018 -0400)
-   1116601 - Add param docs (Francois Campbell, Thu Oct 4 10:04:50 2018 -0400)
-   48a7591 - Pass file_write_mode from Consumer to Pact (Francois Campbell, Thu Oct 4 10:00:37 2018 -0400)
-   6d39609 - Merge pull request #91 from szekar1/small_updates_to_docs (Matthew Balvanz, Fri Aug 24 13:49:05 2018 -0500)
-   a5c8146 - Update README.md (bvccaneer, Fri Aug 24 19:23:26 2018 +0200)
-   4d40485 - adding documentation around #52 and fixing dead link for Matching docs (szekar1, Fri Aug 24 19:19:10 2018 +0200)

## 0.18.0

-   4e8bb85 - Upgrade pact-ruby-standalone (Matthew Balvanz, Tue Aug 21 08:56:53 2018 -0500)
-   8a44feb - chore(docs): update contact information (Matt Fellows, Thu Aug 2 17:18:43 2018 +1000)

## 0.17.0

-   cf5d5bc - Merge pull request #87 from acabelloj/custom-provider-header-support (Matthew Balvanz, Fri Jul 20 22:27:33 2018 -0500)
-   cc61427 - Fixes #83 The verifier always returns exit code 0 (Matthew Balvanz, Fri Jul 20 22:08:26 2018 -0500)
-   239da1c - Remove Python 3.3 from Travis builds (Matthew Balvanz, Wed Jul 4 10:39:12 2018 -0500)
-   273b3fd - Remove Python 3.3 testing (Matthew Balvanz, Wed Jul 4 10:36:01 2018 -0500)
-   01c6763 - Add support to custom provider header (Alejandro Cabello Jiménez, Fri Jun 1 11:40:32 2018 +0200)

## 0.16.1

-   eecbb60 - Merge pull request #79 from shahha/fix-stopping-mock-service-on-windows (Matthew Balvanz, Fri Mar 16 08:45:19 2018 -0500)
-   4115264 - Added windows specific code to check if mock service is stopped. (Hardik Shah, Wed Mar 7 10:44:33 2018 +1100)

## 0.16.0

-   30af240 - Merge pull request #78 from pact-foundation/standalone-1-29-2 (Matthew Balvanz☃, Fri Mar 2 22:05:12 2018 -0600)
-   d428951 - Update to pact-ruby-standalone 1.29.2 (Matthew Balvanz, Fri Mar 2 21:59:08 2018 -0600)

## 0.15.0

-   eb925c3 - Merge pull request #77 from pact-foundation/standalone-1-9-1 (Matthew Balvanz☃, Fri Mar 2 21:22:35 2018 -0600)
-   2a2dcd1 - Upgrade to pact-ruby-standalone 1.9.1 (Matthew Balvanz, Fri Mar 2 21:18:25 2018 -0600)
-   53545be - Merge pull request #72 from fabianbuechler/reduce-server-start-timeout (Matthew Balvanz☃, Fri Mar 2 21:04:03 2018 -0600)
-   b782e43 - Merge pull request #76 from pact-foundation/hide-ruby-stacks (Matthew Balvanz☃, Fri Mar 2 21:03:14 2018 -0600)
-   589224a - Hide Ruby stack traces by default (Matthew Balvanz, Fri Mar 2 20:56:59 2018 -0600)
-   e952b37 - Reduce timeout in \_wait_for_server_start to 25s (Fabian Büchler, Fri Feb 9 11:04:01 2018 +0100)

## 0.14.0

-   3070638 - Merge pull request #71 from pact-foundation/update-standalone-1-9-0 (Matthew Balvanz, Sat Feb 3 23:25:37 2018 -0600)
-   475703c - Resolves #58: Update to pact-ruby-standalone 1.9.0 (Matthew Balvanz, Sat Feb 3 23:12:22 2018 -0600)

## 0.13.0

-   3316743 - Merge pull request #69 from jawu/#52-helper-function-for-assertion-with-matchers (Matthew Balvanz, Sat Jan 20 16:43:56 2018 -0600)
-   ae7f333 - Merge pull request #70 from bethesque/issues/pact-provider-verifier-19 (Matthew Balvanz, Sat Jan 20 16:40:31 2018 -0600)
-   81597d9 - docs: remove reference to v3 pact in provider-states-setup-url (Beth Skurrie, Tue Jan 9 12:27:18 2018 +1100)
-   8bedfd4 - removed local files (Janneck Wullschleger, Wed Dec 20 05:12:08 2017 +0100)
-   5ab2648 - solves #52 added get_generated_values to resolve Mathers to their generated value for assertion (Janneck Wullschleger, Wed Dec 20 05:06:33 2017 +0100)

## 0.12.0

-   149dfc7 - Merge pull request #67 from jawu/enable-possibility-to-use-mathers-in-path (Matthew Balvanz, Sun Dec 17 10:32:34 2017 -0600)
-   fb97d2f - fixed doc string of Request (Janneck Wullschleger, Sat Dec 16 20:44:11 2017 +0100)
-   c2c24cc - adjusted doc string of Request calss to allow str and Matcher as path parameter (Janneck Wullschleger, Sat Dec 16 20:40:35 2017 +0100)
-   697a6a2 - fixed port parameter in e2e test for python 2.7 (Janneck Wullschleger, Thu Dec 14 15:08:05 2017 +0100)
-   ca2eb92 - added from_term call in Request constructor to process path property for json transport (Janneck Wullschleger, Thu Dec 14 14:45:11 2017 +0100)

## 0.11.0

-   ad69039 - Merge pull request #63 from pact-foundation/run-specific-interactions (Matthew Balvanz, Sun Dec 17 09:53:35 2017 -0600)
-   eb63864 - Output a rerun command when a verification fails (Matthew Balvanz, Sun Nov 19 20:44:06 2017 -0600)
-   7c7bc7d - Merge pull request #62 from dhoomakethu/master (Matthew Balvanz, Sun Nov 19 19:53:48 2017 -0600)
-   c27a7a9 - #62 Fix flake8 issues 2 (sanjay, Sun Nov 19 11:18:15 2017 +0530)
-   382c46c - #62 fix flake issues (sanjay, Sun Nov 19 11:13:58 2017 +0530)
-   cdcc85d - Add support to publish verification result to pact broker (sanjay, Tue Oct 31 12:41:52 2017 +0530)
-   c1a5402 - Merge pull request #2 from pact-foundation/master (dhoomakethu, Tue Oct 31 12:15:53 2017 +0530)
-   b91f6c3 - Merge pull request #1 from pact-foundation/master (dhoomakethu, Mon Aug 21 12:36:15 2017 +0530)

## 0.10.0

-   821671e - Merge pull request #53 from pact-foundation/verify-directories (Matthew Balvanz, Sat Nov 18 23:26:05 2017 -0600)
-   8291bb7 - Resolve #22: --pact-url accepts directories (Matthew Balvanz, Sat Oct 7 11:35:37 2017 -0500)

## 0.9.0

-   735aa87 - Set new project minimum requirements (Matthew Balvanz, Sun Oct 22 16:30:12 2017 -0500)
-   295f17c - Merge pull request #60 from ftobia/requirements (Matthew Balvanz, Sun Oct 22 16:09:59 2017 -0500)
-   1dc72da - Merge pull request #48 from bassdread/allow-later-versions-of-requests (Matthew Balvanz, Sun Oct 22 16:09:39 2017 -0500)
-   3265b45 - add suggestion (Chris Hannam, Fri Oct 20 09:33:05 2017 +0100)
-   33504a6 - Resolve #51 verify outputs text instead of bytes (Matthew Balvanz, Thu Oct 19 21:28:39 2017 -0500)
-   51dcda3 - Merge pull request #57 from jceplaras/fix-e2e-test-incorrect-number-of-arg (Matthew Balvanz, Thu Oct 19 20:57:49 2017 -0500)
-   1a4d136 - Relax version requirements in setup.py (vs requirements.txt) (ftobia, Fri Oct 13 19:42:46 2017 -0400)
-   8ece1d6 - Fix incorrect indent on test_incorrect_number_of_arguments on test_e2e (James Plaras, Fri Oct 13 12:54:56 2017 +0800)
-   5f8257b - Resolve #50: Note which version of the Pact specification is supported (Matthew Balvanz, Sat Oct 7 14:05:26 2017 -0500)
-   e728301 - Resolve #45: Document request query parameter (Matthew Balvanz, Sat Oct 7 13:58:07 2017 -0500)
-   5de7200 - Merge pull request #49 from pact-foundation/rename-somethinglike (Matt Fellows, Wed Oct 4 22:36:21 2017 +1100)
-   d73aa1c - Resolve #43: Rename SomethingLike to Like (Matthew Balvanz, Mon Sep 4 15:49:13 2017 -0500)
-   a07c8b6 - Merge pull request #46 from bassdread/fix-setup-url-name (Matthew Balvanz, Mon Sep 4 15:44:45 2017 -0500)
-   b5e1f95 - allow later versions of requests (Chris Hannam, Tue Aug 29 13:38:42 2017 +0100)
-   08fe123 - make setup-url name format match above reference (Chris Hannam, Fri Aug 25 11:03:35 2017 +0100)

## 0.8.0

-   edb6c72 - Merge pull request #41 from pact-foundation/fix-running-on-windows (Matthew Balvanz, Thu Aug 10 21:39:27 2017 -0500)
-   244fff1 - Merge pull request #42 from pact-foundation/deprecate-provider-states-url (Matthew Balvanz, Thu Aug 10 21:38:44 2017 -0500)
-   447b8bb - Resolve #17: Deprecate --provider-states-url (Matthew Balvanz, Sat Jul 29 11:53:05 2017 -0500)
-   4661406 - Move to using the `service` command with pact-mock-service (Matthew Balvanz, Sat Jul 29 10:00:47 2017 -0500)
-   04107db - Remove the PyPi server declaration to use the defaults (Matthew Balvanz, Sun Jul 16 09:05:30 2017 -0500)

## v0.7.0

-   223ea76 - Merge pull request #32 from SimKev2/pacturls (Matthew Balvanz, Sun Jul 16 08:41:14 2017 -0500)
-   e382eb4 - Add tests for #36 SomethingLike not supporting Terms (Matthew Balvanz, Sun Jul 16 08:36:58 2017 -0500)
-   05b4d70 - Merge pull request #37 from jeanbaptistepriez/fix-somethinglike (Matthew Balvanz, Sun Jul 16 08:30:28 2017 -0500)
-   29a2518 - Fix json generation of SomethingLike (https://github.com/pact-foundation/pact-python/issues/36) (jean-baptiste.priez, Wed Jul 12 20:01:58 2017 +0200)
-   b6e1a8b - Issue: Cannot supply multiple files to pact-verifier - PR: Added deprecation warning instead of making api-breaking change (simkev2, Sat Jun 24 20:05:05 2017 -0500)
-   17aa15b - Issue: Cannot supply multiple files to pact-verifier - Updated '--pact-urls' to be a single comma separated string argument - Added '--pact-url' which can be specified multiple times (simkev2, Sat Jun 24 12:57:51 2017 -0500)
-   65b493d - Merge pull request #33 from bethesque/reamde (Matthew Balvanz, Tue Jun 27 08:58:08 2017 -0500)
-   f5a5958 - Update README.md (Beth Skurrie, Sun Jun 25 10:37:03 2017 +1000)

## v0.6.2

-   69caa40 - Merge pull request #35 from pact-foundation/fix-broker-credentials (Matt Fellows, Tue Jun 27 20:49:35 2017 +1000)
-   d60f37f - Fix the use of broker credentials (Matthew Balvanz, Mon Jun 26 21:14:53 2017 -0500)

## v0.6.1

-   14968ea - Merge pull request #34 from hartror/rh_version_fix (Matthew Balvanz, Mon Jun 26 20:23:29 2017 -0500)
-   aca520f - pydocstyle is fussy, should have run it before pushing (Rory Hart, Sun Jun 25 20:11:26 2017 +1000)
-   b70103c - Added docstring for **version**.py (Rory Hart, Sun Jun 25 20:08:50 2017 +1000)
-   2076e34 - Disabled flake8 F401 for **version** import (Rory Hart, Sun Jun 25 20:05:24 2017 +1000)
-   2912e07 - Version in setup.py reading **version**.py directly (Rory Hart, Sun Jun 25 19:40:08 2017 +1000)
-   d137a21 - Split tox environments into test & install to replicate installation issue #31 (Rory Hart, Sun Jun 25 19:16:57 2017 +1000)
-   f549ddf - Merge pull request #30 from bethesque/contributing (Matthew Balvanz, Sat Jun 24 12:43:30 2017 -0500)
-   1f19a0e - Update CONTRIBUTING.md (Beth Skurrie, Thu Jun 22 08:51:35 2017 +1000)
-   3198817 - Update CONTRIBUTING.md (Beth Skurrie, Thu Jun 22 08:36:57 2017 +1000)
-   7a08bb2 - Update CONTRIBUTING.md (Beth Skurrie, Thu Jun 22 08:35:27 2017 +1000)

## v0.6.0

-   10aaaf6 - Merge pull request #27 from pact-foundation/download-pre-package-mock-service-and-verifier (Matthew Balvanz, Tue Jun 20 21:51:40 2017 -0500)
-   a9b991b - Update to pact-ruby-standalone 1.0.0 (Matthew Balvanz, Mon Jun 19 10:17:09 2017 -0500)
-   ab43c8b - Switch to installing the packages from pact-ruby-standalone (Matthew Balvanz, Wed May 31 21:00:51 2017 -0500)
-   db3e7c3 - Use the compiled Ruby applications from pact-mock-service and pact-provider-verifier (Matthew Balvanz, Mon May 29 22:18:47 2017 -0500)

## v0.5.0

-   c085a01 - Merge pull request #26 from AnObfuscator/stub-multiple-requests (Matthew Balvanz, Mon Jun 19 09:14:51 2017 -0500)
-   22c0272 - Add support for stubbing multiple requests at the same time (AnObfuscator, Fri Jun 16 23:18:01 2017 -0500)

## v0.4.1

-   66cf151 - Add RELEASING.md closes #18 (Matthew Balvanz, Tue May 30 22:41:06 2017 -0500)
-   3f61c91 - Add support for request bodies that are False in Python (Matthew Balvanz, Tue May 30 21:57:46 2017 -0500)
-   a39c62f - Merge pull request #19 from ftobia/patch-1 (Matthew Balvanz, Tue May 30 21:42:41 2017 -0500)
-   95aa93a - Allow falsy responses (e.g. 0 not as a string). (Frank Tobia, Mon May 29 19:22:13 2017 -0400)
-   dd3c703 - Merge pull request #16 from jduan/master (Jose Salvatierra, Thu May 25 09:20:10 2017 +0100)
-   978d9f3 - fix typo (Jingjing Duan, Wed May 24 15:48:43 2017 -0700)

## v0.4.0

-   8bec271 - Setup Travis CI to publish to PyPi (Matthew Balvanz, Wed May 24 16:51:05 2017 -0500)
-   d67a015 - Merge pull request #14 from pact-foundation/verify-pacts (Matthew Balvanz, Wed May 24 16:46:49 2017 -0500)
-   78bd029 - Add CONTRIBUTING.md file resolves #4 (Matthew Balvanz, Mon May 22 20:41:09 2017 -0500)
-   d7c32c4 - Repository badges (Matthew Balvanz, Mon May 22 20:22:14 2017 -0500)
-   97122f1 - Merge pull request #13 from pact-foundation/update-developer-documentation (Matthew Balvanz, Sat May 20 20:55:06 2017 -0500)
-   ea015eb - Increment project to v0.4.0 (Matthew Balvanz, Fri May 19 23:46:00 2017 -0500)
-   51eb338 - Command line application for verifying pacts (Matthew Balvanz, Fri May 19 22:24:06 2017 -0500)
-   4b0bbd7 - Update the developer instructions (Matthew Balvanz, Fri May 19 22:05:54 2017 -0500)

## v0.3.0

-   3130f9a - Merge pull request #11 from pact-foundation/update-mock-service (Matthew Balvanz, Sun May 14 09:03:43 2017 -0500)
-   9b20d36 - Updated Versions of Pact Ruby applications (Matthew Balvanz, Sat May 13 09:43:44 2017 -0500)

## v0.2.0

-   140f583 - Merge pull request #8 from pact-foundation/manage-mock-service (Matthew Balvanz, Sat May 13 09:18:40 2017 -0500)
-   5994c3a - pact-python manages the mock service for the user (Matthew Balvanz, Tue May 9 21:58:08 2017 -0500)
-   4bf7b8b - pact-python manages the mock service for the user (Matthew Balvanz, Mon May 1 20:12:53 2017 -0500)
-   0a278af - pact-python manages the mock service for the user (Matthew Balvanz, Tue Apr 18 21:23:18 2017 -0500)
-   fd68b41 - Merge pull request #2 from pact-foundation/package-ruby-apps (Matthew Balvanz, Sat Apr 22 10:55:48 2017 -0500)
-   75a96dc - Package the Ruby Mock Service and Verifier (Matthew Balvanz, Tue Apr 4 23:14:11 2017 -0500)

## v0.1.0

-   189c647 - Merge pull request #3 from pact-foundation/travis-ci (Jose Salvatierra, Fri Apr 7 21:40:02 2017 +0100)
-   559efb8 - Add Travis CI build (Matthew Balvanz, Fri Apr 7 11:12:01 2017 -0500)
-   8f074a0 - Merge pull request #1 from pact-foundation/initial-framework (Matthew Balvanz, Fri Apr 7 09:55:34 2017 -0500)
-   f5caf9c - Initial pact-python implementation (Matthew Balvanz, Mon Apr 3 09:16:59 2017 -0500)
-   bfb8380 - Initial pact-python implementation (Matthew Balvanz, Thu Mar 30 20:41:05 2017 -0500)

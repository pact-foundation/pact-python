### 0.16.1
  * eecbb60 - Merge pull request #79 from shahha/fix-stopping-mock-service-on-windows (Matthew Balvanz, Fri Mar 16 08:45:19 2018 -0500)
  * 4115264 - Added windows specific code to check if mock service is stopped. (Hardik Shah, Wed Mar 7 10:44:33 2018 +1100)

### 0.16.0
  * 30af240 - Merge pull request #78 from pact-foundation/standalone-1-29-2 (Matthew Balvanz☃, Fri Mar 2 22:05:12 2018 -0600)
  * d428951 - Update to pact-ruby-standalone 1.29.2 (Matthew Balvanz, Fri Mar 2 21:59:08 2018 -0600)
 
### 0.15.0
  * eb925c3 - Merge pull request #77 from pact-foundation/standalone-1-9-1 (Matthew Balvanz☃, Fri Mar 2 21:22:35 2018 -0600)
  * 2a2dcd1 - Upgrade to pact-ruby-standalone 1.9.1 (Matthew Balvanz, Fri Mar 2 21:18:25 2018 -0600)
  * 53545be - Merge pull request #72 from fabianbuechler/reduce-server-start-timeout (Matthew Balvanz☃, Fri Mar 2 21:04:03 2018 -0600)
  * b782e43 - Merge pull request #76 from pact-foundation/hide-ruby-stacks (Matthew Balvanz☃, Fri Mar 2 21:03:14 2018 -0600)
  * 589224a - Hide Ruby stack traces by default (Matthew Balvanz, Fri Mar 2 20:56:59 2018 -0600)
  * e952b37 - Reduce timeout in _wait_for_server_start to 25s (Fabian Büchler, Fri Feb 9 11:04:01 2018 +0100)

### 0.14.0
  * 3070638 - Merge pull request #71 from pact-foundation/update-standalone-1-9-0 (Matthew Balvanz, Sat Feb 3 23:25:37 2018 -0600)
  * 475703c - Resolves #58: Update to pact-ruby-standalone 1.9.0 (Matthew Balvanz, Sat Feb 3 23:12:22 2018 -0600)

### 0.13.0
  * 3316743 - Merge pull request #69 from jawu/#52-helper-function-for-assertion-with-matchers (Matthew Balvanz, Sat Jan 20 16:43:56 2018 -0600)
  * ae7f333 - Merge pull request #70 from bethesque/issues/pact-provider-verifier-19 (Matthew Balvanz, Sat Jan 20 16:40:31 2018 -0600)
  * 81597d9 - docs: remove reference to v3 pact in provider-states-setup-url (Beth Skurrie, Tue Jan 9 12:27:18 2018 +1100)
  * 8bedfd4 - removed local files (Janneck Wullschleger, Wed Dec 20 05:12:08 2017 +0100)
  * 5ab2648 - solves #52 added get_generated_values to resolve Mathers to their generated value for assertion (Janneck Wullschleger, Wed Dec 20 05:06:33 2017 +0100)

### 0.12.0
 * 149dfc7 - Merge pull request #67 from jawu/enable-possibility-to-use-mathers-in-path (Matthew Balvanz, Sun Dec 17 10:32:34 2017 -0600)
 * fb97d2f - fixed doc string of Request (Janneck Wullschleger, Sat Dec 16 20:44:11 2017 +0100)
 * c2c24cc - adjusted doc string of Request calss to allow str and Matcher as path parameter (Janneck Wullschleger, Sat Dec 16 20:40:35 2017 +0100)
 * 697a6a2 - fixed port parameter in e2e test for python 2.7 (Janneck Wullschleger, Thu Dec 14 15:08:05 2017 +0100)
 * ca2eb92 - added from_term call in Request constructor to process path property for json transport (Janneck Wullschleger, Thu Dec 14 14:45:11 2017 +0100)

### 0.11.0
 * ad69039 - Merge pull request #63 from pact-foundation/run-specific-interactions (Matthew Balvanz, Sun Dec 17 09:53:35 2017 -0600)
 * eb63864 - Output a rerun command when a verification fails (Matthew Balvanz, Sun Nov 19 20:44:06 2017 -0600)
 * 7c7bc7d - Merge pull request #62 from dhoomakethu/master (Matthew Balvanz, Sun Nov 19 19:53:48 2017 -0600)
 * c27a7a9 - #62 Fix flake8 issues 2 (sanjay, Sun Nov 19 11:18:15 2017 +0530)
 * 382c46c - #62 fix flake issues (sanjay, Sun Nov 19 11:13:58 2017 +0530)
 * cdcc85d - Add support to publish verification result to pact broker (sanjay, Tue Oct 31 12:41:52 2017 +0530)
 * c1a5402 - Merge pull request #2 from pact-foundation/master (dhoomakethu, Tue Oct 31 12:15:53 2017 +0530)
 * b91f6c3 - Merge pull request #1 from pact-foundation/master (dhoomakethu, Mon Aug 21 12:36:15 2017 +0530)

### 0.10.0
  * 821671e - Merge pull request #53 from pact-foundation/verify-directories (Matthew Balvanz, Sat Nov 18 23:26:05 2017 -0600)
  * 8291bb7 - Resolve #22: --pact-url accepts directories (Matthew Balvanz, Sat Oct 7 11:35:37 2017 -0500)

### 0.9.0
  * 735aa87 - Set new project minimum requirements (Matthew Balvanz, Sun Oct 22 16:30:12 2017 -0500)
  * 295f17c - Merge pull request #60 from ftobia/requirements (Matthew Balvanz, Sun Oct 22 16:09:59 2017 -0500)
  * 1dc72da - Merge pull request #48 from bassdread/allow-later-versions-of-requests (Matthew Balvanz, Sun Oct 22 16:09:39 2017 -0500)
  * 3265b45 - add suggestion (Chris Hannam, Fri Oct 20 09:33:05 2017 +0100)
  * 33504a6 - Resolve #51 verify outputs text instead of bytes (Matthew Balvanz, Thu Oct 19 21:28:39 2017 -0500)
  * 51dcda3 - Merge pull request #57 from jceplaras/fix-e2e-test-incorrect-number-of-arg (Matthew Balvanz, Thu Oct 19 20:57:49 2017 -0500)
  * 1a4d136 - Relax version requirements in setup.py (vs requirements.txt) (ftobia, Fri Oct 13 19:42:46 2017 -0400)
  * 8ece1d6 - Fix incorrect indent on test_incorrect_number_of_arguments on test_e2e (James Plaras, Fri Oct 13 12:54:56 2017 +0800)
  * 5f8257b - Resolve #50: Note which version of the Pact specification is supported (Matthew Balvanz, Sat Oct 7 14:05:26 2017 -0500)
  * e728301 - Resolve #45: Document request query parameter (Matthew Balvanz, Sat Oct 7 13:58:07 2017 -0500)
  * 5de7200 - Merge pull request #49 from pact-foundation/rename-somethinglike (Matt Fellows, Wed Oct 4 22:36:21 2017 +1100)
  * d73aa1c - Resolve #43: Rename SomethingLike to Like (Matthew Balvanz, Mon Sep 4 15:49:13 2017 -0500)
  * a07c8b6 - Merge pull request #46 from bassdread/fix-setup-url-name (Matthew Balvanz, Mon Sep 4 15:44:45 2017 -0500)
  * b5e1f95 - allow later versions of requests (Chris Hannam, Tue Aug 29 13:38:42 2017 +0100)
  * 08fe123 - make setup-url name format match above reference (Chris Hannam, Fri Aug 25 11:03:35 2017 +0100)

### 0.8.0
 * edb6c72 - Merge pull request #41 from pact-foundation/fix-running-on-windows (Matthew Balvanz, Thu Aug 10 21:39:27 2017 -0500)
 * 244fff1 - Merge pull request #42 from pact-foundation/deprecate-provider-states-url (Matthew Balvanz, Thu Aug 10 21:38:44 2017 -0500)
 * 447b8bb - Resolve #17: Deprecate --provider-states-url (Matthew Balvanz, Sat Jul 29 11:53:05 2017 -0500)
 * 4661406 - Move to using the `service` command with pact-mock-service (Matthew Balvanz, Sat Jul 29 10:00:47 2017 -0500)
 * 04107db - Remove the PyPi server declaration to use the defaults (Matthew Balvanz, Sun Jul 16 09:05:30 2017 -0500)

### v0.7.0
 * 223ea76 - Merge pull request #32 from SimKev2/pacturls (Matthew Balvanz, Sun Jul 16 08:41:14 2017 -0500)
 * e382eb4 - Add tests for #36 SomethingLike not supporting Terms (Matthew Balvanz, Sun Jul 16 08:36:58 2017 -0500)
 * 05b4d70 - Merge pull request #37 from jeanbaptistepriez/fix-somethinglike (Matthew Balvanz, Sun Jul 16 08:30:28 2017 -0500)
 * 29a2518 - Fix json generation of SomethingLike (https://github.com/pact-foundation/pact-python/issues/36) (jean-baptiste.priez, Wed Jul 12 20:01:58 2017 +0200)
 * b6e1a8b - Issue: Cannot supply multiple files to pact-verifier  - PR: Added deprecation warning instead of making api-breaking change (simkev2, Sat Jun 24 20:05:05 2017 -0500)
 * 17aa15b - Issue: Cannot supply multiple files to pact-verifier  - Updated '--pact-urls' to be a single comma separated string argument  - Added '--pact-url' which can be specified multiple times (simkev2, Sat Jun 24 12:57:51 2017 -0500)
 * 65b493d - Merge pull request #33 from bethesque/reamde (Matthew Balvanz, Tue Jun 27 08:58:08 2017 -0500)
 * f5a5958 - Update README.md (Beth Skurrie, Sun Jun 25 10:37:03 2017 +1000)

### v0.6.2
* 69caa40 - Merge pull request #35 from pact-foundation/fix-broker-credentials (Matt Fellows, Tue Jun 27 20:49:35 2017 +1000)
* d60f37f - Fix the use of broker credentials (Matthew Balvanz, Mon Jun 26 21:14:53 2017 -0500)

### v0.6.1
* 14968ea - Merge pull request #34 from hartror/rh_version_fix (Matthew Balvanz, Mon Jun 26 20:23:29 2017 -0500)
* aca520f - pydocstyle is fussy, should have run it before pushing (Rory Hart, Sun Jun 25 20:11:26 2017 +1000)
* b70103c - Added docstring for __version__.py (Rory Hart, Sun Jun 25 20:08:50 2017 +1000)
* 2076e34 - Disabled flake8 F401 for __version__ import (Rory Hart, Sun Jun 25 20:05:24 2017 +1000)
* 2912e07 - Version in setup.py reading __version__.py directly (Rory Hart, Sun Jun 25 19:40:08 2017 +1000)
* d137a21 - Split tox environments into test & install to replicate installation issue #31 (Rory Hart, Sun Jun 25 19:16:57 2017 +1000)
* f549ddf - Merge pull request #30 from bethesque/contributing (Matthew Balvanz, Sat Jun 24 12:43:30 2017 -0500)
* 1f19a0e - Update CONTRIBUTING.md (Beth Skurrie, Thu Jun 22 08:51:35 2017 +1000)
* 3198817 - Update CONTRIBUTING.md (Beth Skurrie, Thu Jun 22 08:36:57 2017 +1000)
* 7a08bb2 - Update CONTRIBUTING.md (Beth Skurrie, Thu Jun 22 08:35:27 2017 +1000)

### v0.6.0
* 10aaaf6 - Merge pull request #27 from pact-foundation/download-pre-package-mock-service-and-verifier (Matthew Balvanz, Tue Jun 20 21:51:40 2017 -0500)
* a9b991b - Update to pact-ruby-standalone 1.0.0 (Matthew Balvanz, Mon Jun 19 10:17:09 2017 -0500)
* ab43c8b - Switch to installing the packages from pact-ruby-standalone (Matthew Balvanz, Wed May 31 21:00:51 2017 -0500)
* db3e7c3 - Use the compiled Ruby applications from pact-mock-service and pact-provider-verifier (Matthew Balvanz, Mon May 29 22:18:47 2017 -0500)

### v0.5.0
* c085a01 - Merge pull request #26 from AnObfuscator/stub-multiple-requests (Matthew Balvanz, Mon Jun 19 09:14:51 2017 -0500)
* 22c0272 - Add support for stubbing multiple requests at the same time (AnObfuscator, Fri Jun 16 23:18:01 2017 -0500)

### v0.4.1
* 66cf151 - Add RELEASING.md closes #18 (Matthew Balvanz, Tue May 30 22:41:06 2017 -0500)
* 3f61c91 - Add support for request bodies that are False in Python (Matthew Balvanz, Tue May 30 21:57:46 2017 -0500)
* a39c62f - Merge pull request #19 from ftobia/patch-1 (Matthew Balvanz, Tue May 30 21:42:41 2017 -0500)
* 95aa93a - Allow falsy responses (e.g. 0 not as a string). (Frank Tobia, Mon May 29 19:22:13 2017 -0400)
* dd3c703 - Merge pull request #16 from jduan/master (Jose Salvatierra, Thu May 25 09:20:10 2017 +0100)
* 978d9f3 - fix typo (Jingjing Duan, Wed May 24 15:48:43 2017 -0700)

### v0.4.0
* 8bec271 - Setup Travis CI to publish to PyPi (Matthew Balvanz, Wed May 24 16:51:05 2017 -0500)
* d67a015 - Merge pull request #14 from pact-foundation/verify-pacts (Matthew Balvanz, Wed May 24 16:46:49 2017 -0500)
* 78bd029 - Add CONTRIBUTING.md file resolves #4 (Matthew Balvanz, Mon May 22 20:41:09 2017 -0500)
* d7c32c4 - Repository badges (Matthew Balvanz, Mon May 22 20:22:14 2017 -0500)
* 97122f1 - Merge pull request #13 from pact-foundation/update-developer-documentation (Matthew Balvanz, Sat May 20 20:55:06 2017 -0500)
* ea015eb - Increment project to v0.4.0 (Matthew Balvanz, Fri May 19 23:46:00 2017 -0500)
* 51eb338 - Command line application for verifying pacts (Matthew Balvanz, Fri May 19 22:24:06 2017 -0500)
* 4b0bbd7 - Update the developer instructions (Matthew Balvanz, Fri May 19 22:05:54 2017 -0500)

### v0.3.0
* 3130f9a - Merge pull request #11 from pact-foundation/update-mock-service (Matthew Balvanz, Sun May 14 09:03:43 2017 -0500)
* 9b20d36 - Updated Versions of Pact Ruby applications (Matthew Balvanz, Sat May 13 09:43:44 2017 -0500)

### v0.2.0
* 140f583 - Merge pull request #8 from pact-foundation/manage-mock-service (Matthew Balvanz, Sat May 13 09:18:40 2017 -0500)
* 5994c3a - pact-python manages the mock service for the user (Matthew Balvanz, Tue May 9 21:58:08 2017 -0500)
* 4bf7b8b - pact-python manages the mock service for the user (Matthew Balvanz, Mon May 1 20:12:53 2017 -0500)
* 0a278af - pact-python manages the mock service for the user (Matthew Balvanz, Tue Apr 18 21:23:18 2017 -0500)
* fd68b41 - Merge pull request #2 from pact-foundation/package-ruby-apps (Matthew Balvanz, Sat Apr 22 10:55:48 2017 -0500)
* 75a96dc - Package the Ruby Mock Service and Verifier (Matthew Balvanz, Tue Apr 4 23:14:11 2017 -0500)

### v0.1.0
* 189c647 - Merge pull request #3 from pact-foundation/travis-ci (Jose Salvatierra, Fri Apr 7 21:40:02 2017 +0100)
* 559efb8 - Add Travis CI build (Matthew Balvanz, Fri Apr 7 11:12:01 2017 -0500)
* 8f074a0 - Merge pull request #1 from pact-foundation/initial-framework (Matthew Balvanz, Fri Apr 7 09:55:34 2017 -0500)
* f5caf9c - Initial pact-python implementation (Matthew Balvanz, Mon Apr 3 09:16:59 2017 -0500)
* bfb8380 - Initial pact-python implementation (Matthew Balvanz, Thu Mar 30 20:41:05 2017 -0500)

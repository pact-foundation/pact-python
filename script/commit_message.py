#!/usr/bin/env python
import re
import sys
import subprocess

examples = """+ 61c8ca9 fix: navbar not responsive on mobile
+ 479c48b test: prepared test cases for user authentication
+ a992020 chore: moved to semantic versioning
+ b818120 fix: button click even handler firing twice
+ c6e9a97 fix: login page css
+ dfdc715 feat(auth): added social login using twitter
"""


def main():

    cmd_tag = "git describe --abbrev=0"
    tag = subprocess.check_output(cmd_tag,
                                  shell=True).decode("utf-8").split('\n')[0]

    cmd = "git log --pretty=format:'%s' {}..HEAD".format(tag)
    commits = subprocess.check_output(cmd, shell=True)
    commits = commits.decode("utf-8").split('\n')
    for commit in commits:

        pattern = r'((build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert)(\([\w\-]+\))?:\s.*)|((Merge|Fixed)(\([\w\-]+\))?\s.*)'  # noqa
        m = re.match(pattern, commit)
        if m is None:
            print("\nError with git message '{}' style".format(commit))
            print("\nPlease change commit message to the conventional format and try to commit again. Examples:")  # noqa

            print("\n" + examples)
            sys.exit(1)

    print("Commit messages valid")


if __name__ == "__main__":
    main()

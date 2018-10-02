"""bob-builder: builds things.

Usage:
  bob-builder <name> <path-to-code> [--push <docker-push>] [--insecure] [--username=<username> --password=<password>]
"""

from docopt import docopt

from .builds import Build


def main():
    args = docopt(__doc__)
    name = args["<name>"]
    codepath = args["<path-to-code>"]
    push = args["<docker-push>"] if args["--push"] else False
    (username, password) = (args["--username"], args["--password"])

    insecure = args["--insecure"]

    build = Build(
        name=name, codepath=codepath, push=push, username=username, password=password
    )


if __name__ == "__main__":
    main()

"""bob-builder: builds things.

Usage:
  bob-builder <code_path> <image-name>  [--push] [--username=<username> --password=<password>] [--insecure]
"""

from docopt import docopt

from .builds import Build


def main():
    args = docopt(__doc__)
    image_name = args["<image-name>"]
    codepath = args["<code_path>"]
    do_push = args["--push"]
    (username, password) = (args["--username"], args["--password"])

    allow_insecure = args["--insecure"]

    build = Build(
        image_name=image_name,
        codepath=codepath,
        do_push=do_push,
        username=username,
        password=password,
        allow_insecure=allow_insecure,
    )


if __name__ == "__main__":
    main()

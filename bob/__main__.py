"""bob-builder: builds things.

Usage:
  bob-builder <path-to-code> [--push <docker-repository>]
"""

from docopt import docopt


def main():
    args = docopt(__doc__)
    print(args)


if __name__ == "__main__":
    main()

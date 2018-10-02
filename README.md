# bob-the-builder: Builds images, from your code.

UNDER DEVELOPMENT

## Usage

    # Build a Dockerfile-based image.
    $ bob-builder <path-to-code>
    Building with orca-build.

    # Build a Heroku-style repo.
    $ bob-builder <path-to-code>
    Building with Heroku-ish.

    # Push to registry too.
    $ bob-builder <path-to-code> --push registry:80

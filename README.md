# bob-builder: builds images, from your code.

UNDER DEVELOPMENT

## Usage

    # Build a Dockerfile-based image.
    $ bob-builder <code-path> <image-name>
    Building with Docker.

    # Build a Buildpack-style repo.
    $ bob-builder <code-path> <image-name>
    Building with Heroku-ish.

    # Push to registry too.
    $ bob-builder <path-to-code> <image-name> --push

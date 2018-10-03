# bob-builder: builds images, from your code.

UNDER DEVELOPMENT

## Usage

This software is intended to be used with Docker. It requires Docker privlidges, as it runs Docker itself.

First, we'll go through the basics of running this software in Docker, then I'll show you the basics of running it, pretending Docker isn't involved.


### Running with Docker

Run a build of your current working directory:

    $ docker run --privileged -v $(pwd):/app kennethreitz/bob-builder some-imagename

Run a build of your current working directory, using your native docker instance:

    $ docker run --privileged -v $(pwd):/app -v /var/run/docker.sock:/var/run/docker.sock kennethreitz/bob-builder some-imagename

### Using the Software

    # Build a Dockerfile-based image.
    $ <codepath> <image-name>
    Building with Docker.

    # Build a Buildpack-style repo.
    $ bob-builder <codepath> <image-name>
    Building with Heroku-ish.

    # Push to registry too.
    $ bob-builder <path-to-code> <image-name> --push

    # Push to registry (with credentials) too.
    $ bob-builder <path-to-code> <image-name> --username=username --password=password --push

By default, each build will be tagged with a uuid4, unless you specify your own tag in the image name.

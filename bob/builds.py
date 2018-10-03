import os
import time
import json

from uuid import uuid4
from pathlib import Path

import logme
import delegator

from .env import HEROKUISH_IMAGE, BUILD_TIMEOUT

delegator.TIMEOUT = BUILD_TIMEOUT


@logme.log
class Build:
    def __init__(
        self,
        *,
        image_name,
        codepath,
        allow_insecure=False,
        username=None,
        password=None,
        trigger_build=True,
        trigger_push=True,
    ):
        self.uuid = uuid4().hex
        self.image_name = image_name
        self.codepath = Path(codepath)
        self.username = username
        self.password = password
        self.allow_insecure = allow_insecure
        self.was_built = None

        assert os.path.exists(self.codepath)

        if trigger_build:
            self.build()

        if trigger_push:
            self.push()

    def docker(self, cmd, assert_ok=True, fail=True):
        cmd = f"docker {cmd}"
        self.logger.debug(f"$ {cmd}")
        c = delegator.run(cmd)
        try:
            assert c.ok
        except AssertionError as e:
            self.logger.debug(c.out)
            self.logger.debug(c.err)

            if fail:
                raise e

        return c

    @property
    def requires_login(self):
        return all([self.username, self.password])

    @property
    def docker_tag(self):
        if ":" in self.image_name:
            return self.image_name
        else:
            return f"{self.image_name}:{self.uuid}"

    @property
    def has_dockerfile(self):
        return os.path.isfile((self.codepath / "Dockerfile").resolve())

    @property
    def registry_specified(self):
        if len(self.image_name.split("/")) > 1:
            return self.image_name.split("/")[0]

    def ensure_docker(self):

        if self.allow_insecure and self.registry_specified:
            logger.debug("Configuring docker service to allow our insecure registry...")
            # Configure our registry as insecure.
            try:
                with open("/etc/docker/daemon.json", "w") as f:
                    data = {"insecure-registries": [self.registry_specified]}
                    json.dump(data, f)
            # This fails when running on Windows...
            except FileNotFoundError:
                pass

        # Start docker service.
        c = delegator.run("service docker start")
        time.sleep(0.3)

        try:
            # Login to Docker.
            if self.requires_login:

                self.docker(f"login -u {self.username} -p {self.password}")
            c = self.docker("ps")
            assert c.ok
        except AssertionError:
            raise RuntimeError("Docker is not available.")

    def docker_build(self):
        self.logger.info(f"Using Docker to build {self.uuid!r} of {self.image_name!r}.")

        self.ensure_docker()

        c = self.docker(f"build {self.codepath} --tag {self.docker_tag}", block=True)
        self.logger.debug(c.out)
        self.logger.debug(c.err)
        assert c.ok

    def buildpack_build(self):
        self.logger.info(f"Using buildpacks to build {self.uuid!r}.")
        docker_cmd = (
            f"run -i --name={self.uuid} -v {self.codepath}:/tmp/app"
            f" {HEROKUISH_IMAGE} /bin/herokuish buildpack build"
        )
        c = self.docker(docker_cmd)
        self.logger.debug(c.out)
        self.logger.debug(c.err)

    def build(self):
        self.logger.info(f"Starting build {self.uuid!r} of {self.image_name!r}.")
        if self.has_dockerfile:
            self.docker_build()
        else:
            self.buildpack_build()

        self.was_built = True

    def push(self):
        assert self.was_built
        assert self.push

        c = self.docker(f"push {self.docker_tag}")
        self.logger.debug(c.out)
        self.logger.debug(c.err)
        assert c.ok

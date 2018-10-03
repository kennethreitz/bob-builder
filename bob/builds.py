import io
import os
import time
import json
import tempfile
import tarfile

from uuid import uuid4
from pathlib import Path

import logme
import delegator
from requests import Session

from .env import HEROKUISH_IMAGE, BUILD_TIMEOUT

delegator.TIMEOUT = BUILD_TIMEOUT
requests = Session()


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
        buildpack=None,
        trigger_build=True,
        trigger_push=True,
    ):
        self.uuid = uuid4().hex
        self.image_name = image_name
        self.codepath = Path(os.path.abspath(codepath))
        self.username = username
        self.password = password
        self.allow_insecure = allow_insecure
        self.was_built = None

        self.buildpack = buildpack
        self.buildpack_dir = None

        assert os.path.exists(self.codepath)

        if self.buildpack:
            self.ensure_buildpack()

        if trigger_build:
            self.build()

        if trigger_push:
            self.push()

    @property
    def custom_buildpacks_path(self):
        if self.buildpack:
            if not self.buildpack_dir:
                self.buildpack_dir = Path(tempfile.gettempdir())
            return self.buildpack_dir

    @property
    def custom_buildpack_path(self):
        if self.buildpack:
            dl_dir = (self.custom_buildpacks_path / "buildpack").resolve()

            # Ensure the download dir exists.
            os.makedirs(dl_dir, exist_ok=True)

            return dl_dir

    def ensure_buildpack(self):
        assert self.buildpack

        untargz = False
        clone = False

        if self.buildpack.endswith(".tgz") or self.buildpack.endswith(".tar.gz"):
            untargz = True
        else:
            clone = True

        if untargz:
            self.logger.info("Downloading buildpack...")
            r = requests.get(self.buildpack, stream=False)
            self.logger.info("Extracting buildpack...")
            b = io.BytesIO(r.content)
            t = tarfile.open(mode="r:gz", fileobj=b)
            t.extractall(path=self.custom_buildpack_path)

        elif unzip:
            r = requests.get(self.buildpack)
        elif clone:
            cmd = f"git clone {self.buildpack} {self.custom_buildpack_path}"
            self.logger.debug(f"$ {cmd}")
            c = delegator.run(cmd)
            assert c.ok

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
        self.logger.info("Starting docker")
        c = delegator.run("service docker start")
        # assert c.ok
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

        c = self.docker(f"build {self.codepath} --tag {self.docker_tag}")
        self.logger.debug(c.out)
        self.logger.debug(c.err)

    def buildpack_build(self):
        self.logger.info(f"Using buildpacks to build {self.uuid!r}.")
        buildpacks = (
            f"-v {self.custom_buildpacks_path}:/tmp/buildpacks"
            if self.buildpack
            else ""
        )
        docker_cmd = (
            f"run -i --name=build-{self.uuid} -v {self.codepath}:/tmp/app {buildpacks}"
            f" {HEROKUISH_IMAGE} /bin/herokuish buildpack build"
        )
        c = self.docker(docker_cmd)
        self.logger.debug(c.out)
        self.logger.debug(c.err)

        # Commit the Docker build.
        commit = self.docker(f"commit build-{self.uuid}")
        commit_output = commit.out.strip()

        docker_cmd = (
            f"create --expose 80 --env PORT=80 "
            f"--name={self.uuid} {commit_output} /bin/herokuish procfile start web"
        )
        create = self.docker(docker_cmd)
        create_output = create.out.strip()
        self.logger.debug(create_output)

        # Commit service to Docker.
        commit = self.docker(f"commit {self.uuid}")
        commit_output = commit.out.strip()

        tag = self.docker(f"tag {commit_output} {self.docker_tag}")
        tag_output = tag.out.strip()

    def build(self):
        self.logger.info(f"Starting build {self.uuid!r} of {self.image_name!r}.")
        if self.has_dockerfile:
            self.docker_build()
        else:
            self.buildpack_build()

        self.was_built = True
        self.logger.info(f"{self.docker_tag} successfully built!")

    def push(self):
        assert self.was_built
        assert self.push

        c = self.docker(f"push {self.docker_tag}")
        self.logger.debug(c.out)
        self.logger.debug(c.err)
        assert c.ok

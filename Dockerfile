FROM heroku/heroku:18-build

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# -- Install Pipenv:
RUN apt update && apt upgrade -y && apt install python3.7-dev -y
RUN curl --silent https://bootstrap.pypa.io/get-pip.py | python3.7

# Backwards compatility.
RUN rm -fr /usr/bin/python3 && ln /usr/bin/python3.7 /usr/bin/python3

RUN pip3 install pipenv

# -- Install Application into container:
RUN set -ex && mkdir /bob
WORKDIR /bob

# -- Adding Pipfiles
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# Install Docker.
RUN apt install -y docker.io

# Install daemontools
# RUN apt-get update -qq && apt-get install -qq -y daemontools && apt-get -qq -y --allow-downgrades --allow-remove-essential --allow-change-held-packages dist-upgrade && apt-get clean  && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* /var/tmp/*

# Install Herokuish.
# RUN curl --location --silent https://github.com/gliderlabs/herokuish/releases/download/v0.4.4/herokuish_0.4.4_linux_x86_64.tgz | tar -xzC /bin

# -- Install dependencies:
RUN set -ex && pipenv install --deploy --system

COPY . /bob
RUN pip3 install -e .

ENTRYPOINT ["bob-builder", "/app"]
VOLUME /var/lib/docker
VOLUME /app

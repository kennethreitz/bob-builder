import os

HEROKUISH_IMAGE = os.environ.get("HEROKUISH_IMAGE", "gliderlabs/herokuish:latest")
BUILD_TIMEOUT = 60 * 60

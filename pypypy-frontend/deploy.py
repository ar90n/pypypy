#!/usr/bin/env python3
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
)
from constructs import Construct


def get_build_version() -> str:
    ABOUT_PY_PATH = Path(__file__).parent / "pypypy_frontend" / "__about__.py"
    vars = {}
    exec(ABOUT_PY_PATH.read_text(), vars)
    return vars["__version__"]


API_ID = "c84ibhg2yd"
REGION = "ap-northeast-1"
STAGE = "dev"
BUILD_VERSION = get_build_version()
SETUP_PY = f"""import os
import micropip  # type: ignore # noqa: F401

os.environ["API_ID"] = "{API_ID}"
os.environ["REGION"] = "{REGION}"
os.environ["STAGE"] = "{STAGE}"

await micropip.install("./pkgs/pypypy_frontend-{BUILD_VERSION}-py3-none-any.whl")  # type: ignore # noqa: F704
"""


class PypypyFrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "StaticFiles",
            bucket_name="pypypy-static-files",
            website_index_document="index.html",
            public_read_access=True,
            versioned=False,
            removal_policy=RemovalPolicy.DESTROY,
        )

        s3deploy.BucketDeployment(
            self,
            "StaticFilesDeploy",
            sources=[
                s3deploy.Source.asset("./public"),
                s3deploy.Source.data("setup.py", SETUP_PY),
            ],
            destination_bucket=bucket,
        )


app = cdk.App()
PypypyFrontendStack(app, "PypypyFrontendStack")

app.synth()

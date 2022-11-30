#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_apigatewayv2 as apigateway
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from constructs import Construct

stage_name = os.environ.get("STAGE", "dev")


class PypypyBackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=[
                "execute-api:ManageConnections",
            ],
        )

        lambda_role = iam.Role(
            self,
            "pypypy-backend-iam-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchLogsFullAccess"
                ),
            ],
        )
        lambda_role.add_to_policy(lambda_policy)

        websocket_connection = dynamodb.Table(
            self,
            "PypypyBackendWebSocketConnection",
            partition_key={
                "name": "connectionId",
                "type": dynamodb.AttributeType.STRING,
            },
            table_name="pypypy-websocket-connection",
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        message_relay_api = apigateway.CfnApi(
            self,
            "PypypyBackendApi",
            name="pypypy-websocket-relay-api",
            protocol_type="WEBSOCKET",
            route_selection_expression=r"\$default",
        )

        connect_lambda = _lambda.Function(
            self,
            "PypypyBackendConnect",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="connect.handler",
            environment={},
        )

        disconnect_lambda = _lambda.Function(
            self,
            "PypypyBackendDisconnect",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="disconnect.handler",
            environment={},
        )
        relay_lambda = _lambda.Function(
            self,
            "PypypyBackendRelay",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="relay.handler",
            environment={"STAGE": stage_name, "API_ID": message_relay_api.ref},
            role=lambda_role,
        )

        websocket_connection.grant_write_data(connect_lambda)
        websocket_connection.grant_write_data(connect_lambda)
        websocket_connection.grant_read_write_data(relay_lambda)

        apigw_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[
                connect_lambda.function_arn,
                disconnect_lambda.function_arn,
                relay_lambda.function_arn,
            ],
            actions=["lambda:InvokeFunction"],
        )

        apigw_role = iam.Role(
            self,
            "pypypy-backend-iam-apigw-role",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
        )
        apigw_role.add_to_policy(apigw_policy)

        connect_integration = apigateway.CfnIntegration(
            self,
            "connect-integration",
            api_id=message_relay_api.ref,
            integration_type="AWS_PROXY",
            integration_uri=f"arn:aws:apigateway:ap-northeast-1:lambda:path/2015-03-31/functions/{connect_lambda.function_arn}/invocations",  # noqa: E501
            credentials_arn=apigw_role.role_arn,
        )

        apigateway.CfnRoute(
            self,
            "connect-route",
            api_id=message_relay_api.ref,
            route_key="$connect",
            authorization_type="NONE",
            target=f"integrations/{connect_integration.ref}",
        )
        disconnect_integration = apigateway.CfnIntegration(
            self,
            "disconnect-integration",
            api_id=message_relay_api.ref,
            integration_type="AWS_PROXY",
            integration_uri=f"arn:aws:apigateway:ap-northeast-1:lambda:path/2015-03-31/functions/{disconnect_lambda.function_arn}/invocations",  # noqa: E501
            credentials_arn=apigw_role.role_arn,
        )

        apigateway.CfnRoute(
            self,
            "disconnect-route",
            api_id=message_relay_api.ref,
            route_key="$disconnect",
            authorization_type="NONE",
            target=f"integrations/{disconnect_integration.ref}",
        )

        default_integration = apigateway.CfnIntegration(
            self,
            "default-integration",
            api_id=message_relay_api.ref,
            integration_type="AWS_PROXY",
            integration_uri=f"arn:aws:apigateway:ap-northeast-1:lambda:path/2015-03-31/functions/{relay_lambda.function_arn}/invocations",  # noqa: E501
            credentials_arn=apigw_role.role_arn,
        )

        apigateway.CfnRoute(
            self,
            "default-route",
            api_id=message_relay_api.ref,
            route_key="$default",
            authorization_type="NONE",
            target=f"integrations/{default_integration.ref}",
        )

        deployment = apigateway.CfnDeployment(
            self, "pypypy-backend-deployment", api_id=message_relay_api.ref
        )

        apigateway.CfnStage(
            self,
            "pypypy-backend-stage",
            api_id=message_relay_api.ref,
            auto_deploy=True,
            deployment_id=deployment.ref,
            stage_name=stage_name,
        )


app = cdk.App()
PypypyBackendStack(app, "PypypyBackendStack")

app.synth()

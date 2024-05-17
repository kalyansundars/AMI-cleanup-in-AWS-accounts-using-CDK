from os import path
from aws_cdk import (
    Stack,
    aws_events as events,
    aws_lambda as lambda_,
    aws_events_targets as targets,
    aws_iam as _iam,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions
)
import aws_cdk as cdk
from constructs import Construct

class AmiCleanUpStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, cron_schedule, notify_email, rule, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        my_topic = sns.Topic(self, "Topic")
        my_topic.add_subscription(subscriptions.EmailSubscription(notify_email))

         #Create role        
        lambda_role = _iam.Role(scope=self, id='cdk-lambda-role',
                                assumed_by =_iam.ServicePrincipal('lambda.amazonaws.com'),
                                role_name='AmiCleanUpStack-amicleanuplambdaServiceRole',
                                managed_policies=[
                                _iam.ManagedPolicy.from_aws_managed_policy_name(
                                    'service-role/AWSLambdaBasicExecutionRole')
                                ]
                                
                        )
        lambda_role.add_to_policy(_iam.PolicyStatement(
            resources=["*"],
            actions=[   'ec2:DescribeSnapshots',
                        'ec2:DeleteSnapshot',
                        'ec2:DeregisterImage',
                        'ec2:DescribeImages',
                        'ec2:DescribeInstances',
                        'ec2:DescribeInstanceStatus',
                        'sns:Publish'
                    ],
        ))
            
        lambdaFn = lambda_.Function(
            self, "ami-cleanup-lambda",           
            code=lambda_.Code.from_asset(path.join("lambda_cleaner")),           
            handler="index.handler",
            timeout=cdk.Duration.seconds(900),
            runtime=lambda_.Runtime.PYTHON_3_8,
            role=lambda_role,
            environment={'SNS_ARN': my_topic.topic_arn, 'rule': rule}
        )

        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.cron(minute=cron_schedule['minute'], hour=cron_schedule['hour'], month=cron_schedule['month'], day=cron_schedule['day'], year=cron_schedule['year'])            
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))

        
        

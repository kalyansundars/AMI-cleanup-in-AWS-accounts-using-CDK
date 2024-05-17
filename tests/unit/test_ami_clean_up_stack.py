import aws_cdk as core
import aws_cdk.assertions as assertions

from ami_clean_up.ami_clean_up_stack import AmiCleanUpStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ami_clean_up/ami_clean_up_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AmiCleanUpStack(app, "ami-clean-up")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

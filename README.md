  

# Schedule AMI cleanup in AWS accounts using CDK

  

Amazon Machine Images (AMIs) and underlying Amazon Elastic Block Store (Amazon EBS) Snapshots are often created automatically based on schedule or other automated process. Old AMIs that are no longer in use and left unattended for a long time can add unnecessary costs. Identifying and clearing up these unused AMIs and related snapshots manually is time consuming. This Serverless event driven pattern helps in identifying those unused images and snapshots and de-registers them on a scheduled basis. This helps in reducing snapshot costs. 

- This pattern creates the required AWS Lambda services using AWS Cloud Development Kit (AWS CDK) that runs on a schedule to identify those unused AMI based on set rules and cleans up automatically.

- This pattern, also uses tags and or, dictionary, Max age configuration to identify pattern, fresh/master AMIs to be excluded from the cleanup process.

- This pattern describes how to use this code to automatically get the snapshot ids and deregister the older AMI associated with it after deleting the snapshots and send notifications.

  

## Prerequisites  

- An Understanding of [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) and usage.

- An active AWS account

- AWS CDK CLI

- A web browser that is supported for use with the AWS Management Console. ([See the list of supported browsers](https://aws.amazon.com/premiumsupport/knowledge-center/browsers-management-console/))

- Python CLI version 3.8+

  

## Limitations

- Targeted AMIs will be scoped to the account where the pattern is being deployed.
- This pattern does not support AMI’s created from other region/account
  

## Product versions

-  AWS Lambda runtime v3.8

  

## Architecture  
  ![](https://1a9zxhkqsj.execute-api.us-west-2.amazonaws.com/v1/contents/38061334-a7fe-4ba7-a466-9ab0255018ba/images/55e32415-5312-4b1e-a8c0-191ad6d2441b.png)

 

## High Level Workflow 

The workflow illustrated in the diagram consists of these high-level steps:

1.  AWS CDK stack deploys the Amazon Amazon EventBridge, AWS Lambda, Amazon SNS.    
2.  Amazon EventBridge triggers the Lambda based on the schedule defined.    
3.  AWS Lambda identifies the AMIs based on the rule set and then it removes those AMIs and sends email notification.    
4.  Logs are written to Amazon CloudWatch.

  

## Setup

This project is set up like a standard Python project. The initialization process also creates
a virtualenv within this project, stored under the .venv directory. 
To create the virtualenv it assumes that there is a `python3` executable in your path with access to the `venv` package.
If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv
manually once the init process completes.
To manually create a virtualenv on MacOS and Linux:
```
$ python3 -m venv .venv
```
After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.
```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:
```
% .venv\Scripts\activate.bat
```
Once the virtualenv is activated, you can install the required dependencies.
```
$ pip3 install -r requirements.txt
```

To create the stack for a specific region, open **config/config.json** file.
Update config.json file with AWS Region, Cron Schedule, rule and email address to be notified.  
Schema: 

```
{
  "definitions": {
    
  },
  "title": "Root",
  "type": "object",
  "required": [
    "region",
    "cron_schedule",
    "notify_email",
    "rule"
  ],
  "properties": {
    "region": {
      "$id": "#root/region",
      "title": "Region",
      "type": "string",
      "default": "",
      "examples": [
        "us-east-1"
      ],
      "pattern": "^.*$"
    },
    "cron_schedule": {
      "$id": "#root/cron_schedule",
      "title": "Cron_schedule",
      "type": "object",
      "required": [
        "minute",
        "hour",
        "month",
        "day",
        "year"
      ],
      "properties": {
        "minute": {
          "$id": "#root/cron_schedule/minute",
          "title": "Minute",
          "type": "string",
          "default": "",
          "examples": [
            "0"
          ],
          "pattern": "^.*$"
        },
        "hour": {
          "$id": "#root/cron_schedule/hour",
          "title": "Hour",
          "type": "string",
          "default": "",
          "examples": [
            "10"
          ],
          "pattern": "^.*$"
        },
        "month": {
          "$id": "#root/cron_schedule/month",
          "title": "Month",
          "type": "string",
          "default": "",
          "examples": [
            "*"
          ],
          "pattern": "^.*$"
        },
        "day": {
          "$id": "#root/cron_schedule/day",
          "title": "Day",
          "type": "string",
          "default": "",
          "examples": [
            "*"
          ],
          "pattern": "^.*$"
        },
        "year": {
          "$id": "#root/cron_schedule/year",
          "title": "Year",
          "type": "string",
          "default": "",
          "examples": [
            "*"
          ],
          "pattern": "^.*$"
        }
      }
    },
    "notify_email": {
      "$id": "#root/notify_email",
      "title": "Notify_email",
      "type": "string",
      "default": "",
      "examples": [
        "xxx@yyy.com"
      ],
      "pattern": "^.*$"
    },
    "rule": {
      "$id": "#root/rule",
      "title": "Rule",
      "type": "object",
      "required": [
        "include",
        "exclude"
      ],
      "properties": {
        "include": {
          "$id": "#root/rule/include",
          "title": "Include",
          "type": "object",
          "required": [
            "max_days",
            "tag"
          ],
          "properties": {
            "max_days": {
              "$id": "#root/rule/include/max_days",
              "title": "Max_days",
              "type": "integer",
              "examples": [
                0
              ],
              "default": 0
            },
            "tag": {
              "$id": "#root/rule/include/tag",
              "title": "Tag",
              "type": "object",
              "required": [
                "env",
                "cost_center"
              ],
              "properties": {
                "env": {
                  "$id": "#root/rule/include/tag/env",
                  "title": "Env",
                  "type": "array",
                  "default": [
                    
                  ],
                  "items": {
                    "$id": "#root/rule/include/tag/env/items",
                    "title": "Items",
                    "type": "string",
                    "default": "",
                    "examples": [
                      "dev"
                    ],
                    "pattern": "^.*$"
                  }
                },
                "cost_center": {
                  "$id": "#root/rule/include/tag/cost_center",
                  "title": "Cost_center",
                  "type": "array",
                  "default": [
                    
                  ],
                  "items": {
                    "$id": "#root/rule/include/tag/cost_center/items",
                    "title": "Items",
                    "type": "string",
                    "default": "",
                    "examples": [
                      "120"
                    ],
                    "pattern": "^.*$"
                  }
                }
              }
            }
          }
        },
        "exclude": {
          "$id": "#root/rule/exclude",
          "title": "Exclude",
          "type": "object",
          "required": [
            "tag"
          ],
          "properties": {
            "tag": {
              "$id": "#root/rule/exclude/tag",
              "title": "Tag",
              "type": "object",
              "required": [
                "env",
                "cost_center"
              ],
              "properties": {
                "env": {
                  "$id": "#root/rule/exclude/tag/env",
                  "title": "Env",
                  "type": "array",
                  "default": [
                    
                  ],
                  "items": {
                    "$id": "#root/rule/exclude/tag/env/items",
                    "title": "Items",
                    "type": "string",
                    "default": "",
                    "examples": [
                      "uat"
                    ],
                    "pattern": "^.*$"
                  }
                },
                "cost_center": {
                  "$id": "#root/rule/exclude/tag/cost_center",
                  "title": "Cost_center",
                  "type": "array",
                  "default": [
                    
                  ],
                  "items": {
                    "$id": "#root/rule/exclude/tag/cost_center/items",
                    "title": "Items",
                    "type": "string",
                    "default": "",
                    "examples": [
                      "150"
                    ],
                    "pattern": "^.*$"
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

Example:

```
{
    "region": String <region to be deployed> (eg: us-east-1, us-west-1),
    "cron_schedule": {
      "minute": "0",
      "hour": "10",
      "month": "*",
      "day": "*",
      "year": "*"
    },
    "notify_email": "xxx@yyy.com",
    "rule": {
      "include": {
        "max_days": 0,
        "tag": {
          "env": ["dev","int"],
          "cost_center": ["120","130"]
        }
      },
      "exclude": {
        "tag": {
          "env": ["uat","prod"],
          "cost_center": ["150"]
        }
      }
    }
}
```

## Installation
```
cdk deploy
```
## Verification
### Verification of Stack creation
-   Login to AWS console    
-   Navigate to cloudformation Service    
-   Look for name “AmiCleanUpStack”    
-   Verify stack creation under “resources” tab

### Verify AMi & Snapshot Deletion
-   Login to AWS console    
-   Open EC2 service and Cloudwatch    
-   Once the Amazon EventBridge triggers the AWS Lambda based on the schedule, verify the deletion of AMIs and associated snapshots on EC2 service.    
-   Logs are written to Amazon CloudWatch and email is triggered based on configuration with list of deleted AMIs and snapshots.

### Clean up
  
To tear down the solution, run  **cdk destroy**. This should remove all nested stacks. In the AWS CloudFormation console verify  **AmiCleanUpStack** is no longer present in the region in which it was deployed.

## Related Resources

- [Amazon Machine Images (AMI)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html)
- [Getting started with CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)
- [Your first AWS CDK app](https://docs.aws.amazon.com/cdk/v2/guide/hello_world.html)
- [AWS Pricing](https://calculator.aws/#/addService)
#!/usr/bin/env python3
import os
import json
import aws_cdk as cdk

from ami_clean_up.ami_clean_up_stack import AmiCleanUpStack


app = cdk.App()
with open("config/config.json") as file:
    data = json.load(file)

region = data["region"]
cron_schedule = data["cron_schedule"]
notify_email= data["notify_email"]
rule = json.dumps(data["rule"])

AmiCleanUpStack(app, "AmiCleanUpStack",
    cron_schedule,
    notify_email,
    rule,
    env=cdk.Environment(        
        region=region
    ),    
)
app.synth()
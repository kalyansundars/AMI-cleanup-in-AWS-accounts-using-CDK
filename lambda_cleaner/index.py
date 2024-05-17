import logging
import os
import re
import sys
from datetime import datetime, timedelta
import boto3
import json

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

##############
rule = json.loads(os.environ.get('rule'))
LOGGER.info('rule: %s', rule)
EXCLUDE = rule['exclude']
INCLUDE = rule['include']
EXCLUDE_TAGS = EXCLUDE['tag']
AMI_MAX_AGE = INCLUDE['max_days']
TO_REMOVE_TAGS=INCLUDE['tag']
EMAIL_OUTPUT= ''


##############
EC2 = boto3.resource("ec2")
EC2_CLIENT = boto3.client("ec2")

def handler(event, context):
    """handler method"""
    # pylint: disable=R0914, C0103,W0613      
    
    EMAIL_OUTPUT=' '
    ACCOUNT_ID = context.invoked_function_arn.split(":")[4]
    ###########################
    # identify My AMIs
    my_amis = EC2_CLIENT.describe_images(Owners=[ACCOUNT_ID])['Images']
    my_snapshots = EC2_CLIENT.describe_snapshots(OwnerIds=[ACCOUNT_ID])['Snapshots']
    #LOGGER.info('my_amis: %s', my_amis['ImageId'])   
    ###########################
    # identify Used AMIs
    used_amis = {
        instance.image_id for instance in EC2.instances.all()
    }
    LOGGER.info('used_amis: %s', used_amis)    
    ########################### 
    # identify Fresh AMIs created based on MAx Age
    fresh_amis = set()
    for ami in my_amis:
        created_at = datetime.strptime(ami['CreationDate'],"%Y-%m-%dT%H:%M:%S.000Z",)
        if created_at > datetime.now() - timedelta(AMI_MAX_AGE):
            fresh_amis.add(ami['ImageId'])
    LOGGER.info('fresh_amis: %s', fresh_amis)
    
    ###########################
    # identify Exclude AMIs
    exclude_amis = set()
    for ami in my_amis:
        if 'Tags' in ami:
            if validateExcludeList(ami):
                exclude_amis.add(ami['ImageId'])

    LOGGER.info('exclude_amis: %s', exclude_amis)
    
    ###########################
    # assign them to safe list
    safe = used_amis | fresh_amis | exclude_amis
    LOGGER.info('safe: %s', safe)

    ###########################
    # get Remaining as to remove list
    remaining_list = []
    for ami in my_amis:
        if ami['ImageId'] not in safe:
            remaining_list.append(ami)
    LOGGER.info('remaining_list: %s', remaining_list)
    
    ###########################
    # Check for Tags filter from to remove list
    to_remove_amis = []
    LOGGER.info('TO_REMOVE_TAGS: %s, %s', len(TO_REMOVE_TAGS), type(TO_REMOVE_TAGS))
    if len(TO_REMOVE_TAGS) > 0:
        for ami in remaining_list:
            if 'Tags' in ami:
                if ValidateTagFilter(ami):
                    to_remove_amis.append(ami)
    else:
        to_remove_amis = remaining_list
        
    LOGGER.info('to_remove_amis: %s', to_remove_amis)
    
    if len(to_remove_amis) > 0:
        LOGGER.info('######## Below List of AMIs will be removed ############')
        EMAIL_OUTPUT = EMAIL_OUTPUT + '\n' + '######## Below List of AMIs will be removed ############'
        for ami in to_remove_amis:
            LOGGER.info(ami['ImageId'])  
            EMAIL_OUTPUT = EMAIL_OUTPUT + '\n' + ami['ImageId']
        LOGGER.info('########################################################')  
        EMAIL_OUTPUT = EMAIL_OUTPUT + '\n' + '########################################################'


        ###########################
        # deregister AMIs
        for ami in to_remove_amis:
            EMAIL_OUTPUT = EMAIL_OUTPUT + '\n' + deregister(ami)
                
        ###########################
        # delete associated Snapshots
        LOGGER.info('########################################################')  
        EMAIL_OUTPUT = EMAIL_OUTPUT + '\n' + '########################################################'
        LOGGER.info('Searching Associated Snapshots for removal......')
        EMAIL_OUTPUT = EMAIL_OUTPUT + '\n' + 'Searching Associated Snapshots for removal......'
        for snapshot in my_snapshots:
            r = re.match(r".*for.* (ami-.*) from.*", snapshot['Description'])
            if r:
                for ami in to_remove_amis:
                    if ami['ImageId'] == r.groups()[0]:
                        EMAIL_OUTPUT = EMAIL_OUTPUT + '\n' + deleteSnapShot(ami, snapshot['SnapshotId']) 
    else:
        LOGGER.info('No ami found for removal!. Exiting!')
        EMAIL_OUTPUT = EMAIL_OUTPUT + '\n' + 'No ami found for removal!. Exiting!'
    
    sns = boto3.client('sns')
    responce = sns.publish(
    TopicArn=os.environ.get('SNS_ARN'),
    Message=EMAIL_OUTPUT
    )

def validateExcludeList(ami):
    for tag in ami['Tags']:
        for x in EXCLUDE_TAGS:
            if (tag['Key'] == x):
                if(tag['Value'] in EXCLUDE_TAGS[x]):
                    return True
            

def ValidateTagFilter(ami):
    for tag in ami['Tags']:
        for x in TO_REMOVE_TAGS:
            if (tag['Key'] == x):
                if(tag['Value'] in TO_REMOVE_TAGS[x]):
                    return True
                        
def deregister(ami):
    LOGGER.info('Deregistering %s (%s)', ami['Name'], ami['ImageId'])
    output = 'Deregistering: {} {}'.format(ami['Name'], ami['ImageId'])
    LOGGER.info('output %s', output)
    EC2_CLIENT.deregister_image(ImageId=ami['ImageId'])
    return output
    
def deleteSnapShot(ami, snapshotId):    
    LOGGER.info('Deleting Snapshot: %s for %s',snapshotId, ami['ImageId'])
    output = 'Deleting Snapshot: {} {}'.format(snapshotId, ami['ImageId'])
    EC2_CLIENT.delete_snapshot(SnapshotId=snapshotId)
    return output
    
if __name__ == "__main__":
    handler(None, None)
# -- coding: utf-8 --
import boto3
import logging
import json
import os


TAG_KEY = os.environ['TAG_KEY']


logger = logging.getLogger()
logger.setLevel(logging.INFO)
ec2_client = boto3.client('ec2')
cloudwatch_client = boto3.client('cloudwatch')


def lambda_handler(event, context):

    responce = ec2_client.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': [TAG_KEY]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    # get instance data with tag filter
    num_instances = dict()
    num_vcpus = dict()
    vcpus = 0
    for reservation in responce['Reservations']:
        for instance in reservation['Instances']:
            tag_value = 'NONE'
            for val in instance['Tags']:
                if val['Key'] == TAG_KEY:
                    tag_value = val['Value']
            
            if tag_value not in num_instances:
                num_instances[tag_value] = 0
                num_vcpus[tag_value] = 0
            
            num_instances[tag_value] += 1
            num_vcpus[tag_value] += instance['CpuOptions']['CoreCount'] * instance['CpuOptions']['ThreadsPerCore']

    print(num_instances)
    print(num_vcpus)

    # build metrics
    metricdata = []
    for tag_value in num_instances.keys():
        metricdata.append(
            {
                'MetricName': 'Number of Instances',
                'Dimensions': [{'Name': TAG_KEY, 'Value': tag_value}], 
                'Unit': 'Count',
                'Value': num_instances[tag_value]
            }
        )
        metricdata.append(
            {
                'MetricName': 'Number of vCPUs',
                'Dimensions': [{'Name': TAG_KEY, 'Value': tag_value}], 
                'Unit': 'Count',
                'Value': num_vcpus[tag_value]
            }
        )
    
    # submit metrics
    logger.debug(metricdata)
    cloudwatch_client.put_metric_data(
        Namespace = 'EC2-Counter',
        MetricData = metricdata
    )


    return {
        'statusCode': 200,
        'body': 'Succeeded'
    }

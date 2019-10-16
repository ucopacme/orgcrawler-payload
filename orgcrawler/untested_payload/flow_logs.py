import boto3


def create_flow_log(region, account):
    client = boto3.client('ec2', region_name=region, **account.credentials)
    vpc_list = [vpc['VpcId'] for vpc in client.describe_vpcs()["Vpcs"]]
<<<<<<< HEAD
    print(vpc_list)
    response = client.create_flow_logs(ResourceType='VPC',TrafficType='ALL',LogDestinationType='s3',LogDestination='arn:aws:s3:::qradar-flow-logs-centralization/*' ,ResourceIds=vpc_list)
    print(response)
=======
    #print(vpc_list)
    response = client.create_flow_logs(ResourceType='VPC',TrafficType='ALL',LogDestinationType='s3',LogDestination='arn:aws:s3:::ait-flow-logs/*' ,ResourceIds=vpc_list)
    #print(response)
    response.pop('ResponseMetadata')
    return response


'''
ashley's 57 cents:

- LogDestination should be a function param:

    def create_flow_log(region, account, log_destination_bucket):

- vpc_list creation should handle edge cases:

    - what if there are no vpc in an account?

    - what if there are lots of vpc? do we need to paganate?

- create_flow_logs call can be formatted better:

    response = client.create_flow_logs(
        ResourceType='VPC',
        TrafficType='ALL',
        LogDestinationType='s3',
        LogDestination=log_destination_bucket,
        ResourceIds=vpc_list
    )

'''


def describe_flow_logs(region, account):
    client = boto3.client('ec2', region_name=region, **account.credentials)
    response = client.describe_flow_logs()
    #print(response)
>>>>>>> a094b8ecae94a9696eda6bed89e7a18a08ab5344
    response.pop('ResponseMetadata')
    return response

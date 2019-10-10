import boto3


def create_flow_log(region, account):
    client = boto3.client('ec2', region_name=region, **account.credentials)
    vpc_list = [vpc['VpcId'] for vpc in client.describe_vpcs()["Vpcs"]]
    print(vpc_list)
    response = client.create_flow_logs(ResourceType='VPC',TrafficType='ALL',LogDestinationType='s3',LogDestination='arn:aws:s3:::ait-flow-logs/*' ,ResourceIds=vpc_list)
    print(response)
    response.pop('ResponseMetadata')
    return response

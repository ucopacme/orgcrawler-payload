import boto3


def create_flow_log(region, account):
    client = boto3.client('ec2', region_name=region, **account.credentials)
    vpc_list = [vpc[VpcId] for vpc in client.describe_vpcs()]
    response = client.create_flow_logs(ResourceType='VPC',TrafficType='ALL',LogDestinationType='s3',LogDestination='arn:aws:s3:::qradar-cloudtrailbucket-1tltlpn8gpsa2-logbucket-1gahs58bwbwlv' , ResourceIds=vpc_list )
    response.pop('ResponseMetadata')
    return response

import boto3


def list_ec2_instances(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole --regions us-west-2,us-east-1 orgcrawler.payloads.list_ec2_instances | jq -r '.[].Regions[].Output.Reservations[].Instances[]| select(.State.Name == "running") | .PrivateIpAddress'
    '''
    client = boto3.client('ec2', region_name=region, **account.credentials)
    response = client.describe_instances()
    response.pop('ResponseMetadata')
    return response


def list_vpn_gateways(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole --regions us-west-2,us-east-1 orgcrawler.payloads.list_vpn_gateways | jq -r '.[].Regions[].Output.VpnGateways[] | select(.State == "available") | .VpcAttachments[].VpcId'
    '''
    client = boto3.client('ec2', region_name=region, **account.credentials)
    response = client.describe_vpn_gateways()
    response.pop('ResponseMetadata')
    return response

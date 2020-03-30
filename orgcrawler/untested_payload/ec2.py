import boto3
from .config import get_non_compliant_resources


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


def list_rules_for_non_compliant_sg(region, account, rule_name):
    '''
    Query config service for non compliant security groups per given config rule.
    
    rule_name can be a regex

      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.ec2.list_rules_for_non_compliant_sg securityhub-vpc-default
    '''
    non_compliant_resources = get_non_compliant_resources(region, account, rule_name)['NonCompliantResources']
    non_compliant_sg = [r['ResourceId'] for r in non_compliant_resources if r['ResourceType'] == 'AWS::EC2::SecurityGroup']
    client = boto3.client('ec2', region_name=region, **account.credentials)
    ec2 = boto3.resource('ec2', region_name=region, **account.credentials)
    sg_rules = []
    for sg_id in non_compliant_sg:
        sg = ec2.SecurityGroup(sg_id)
        sg_rules.append(dict(
            group_id=sg_id,
            ingress_rules=sg.ip_permissions,
            egress_rules=sg.ip_permissions_egress,
        ))
    return dict(NonCompliantSecurityGroupRules=sg_rules)

import boto3


def paginate(client, method, **kwargs):
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result


def cf_list_stack_sets(region, account):
    client = boto3.client('cloudformation', region_name=region, **account.credentials)
    response = client.list_stack_sets()
    response.pop('ResponseMetadata')
    return response


def list_stack_names(region, account):
    client = boto3.client('cloudformation', region_name=region, **account.credentials)
    stack_paganator = paginate(client, client.describe_stacks)
    return dict(StackNames=[stack['StackName'] for stack in stack_paganator])


def stack_status(region, account, pattern=None):
    '''
    orgcrawler -r awsauth/OrgAdmin orgcrawler.untested_payload.cfn.stack_status Compliance-Engine-Benchmark-DO-NOT-DELETE --regions us-west-2,us-east-1 |
      jq -r '.[] | .Account, .Regions[].Output.StackStatus[].StackStatus'
    '''
    client = boto3.client('cloudformation', region_name=region, **account.credentials)
    stack_paganator = paginate(client, client.describe_stacks)
    if pattern is not None:
        status = [dict(StackName=stack['StackName'], StackStatus=stack['StackStatus']) for stack in stack_paganator if stack['StackName'].startswith(pattern)]
    else:
        status = [dict(StackName=stack['StackName'], StackStatus=stack['StackStatus']) for stack in stack_paganator]
    return dict(StackStatus=status)

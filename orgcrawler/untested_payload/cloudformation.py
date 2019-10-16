import boto3


def cf_list_stack_sets(region, account):
    client = boto3.client('cloudformation', region_name=region, **account.credentials)
    response = client.list_stack_sets()
    response.pop('ResponseMetadata')
    return response


def cf_list_stacks(region, account):
    client = boto3.client('cloudformation', region_name=region, **account.credentials)
    response = client.list_stacks()
    stacks = response['StackSummaries']
    while 'NextToken' in response:
        response = client.list_stacks(NextToken=response['NextToken'])
        stacks += response['StackSummaries']
    return dict(liststacks=stacks)

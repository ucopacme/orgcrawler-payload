import boto3


def status_config_svcs(region, account):
    client = boto3.client('config', region_name=region, **account.credentials)
    response = client.describe_configuration_recorder_status()
    response.pop('ResponseMetadata')
    if response['ConfigurationRecordersStatus']:
        state = dict(recording=True)
    else:
        state = dict(recording=False)
    return dict(ConfigurationRecordersStatus=state)


def resource_counts(region, account):
    client = boto3.client('config', region_name=region, **account.credentials)
    response = client.get_discovered_resource_counts()
    return dict(resourceCounts=response['resourceCounts'])


def describe_rules(region, account):
    '''
    usage example:

      orgcrawler -r OrganizationAccountAccessRole orgcrawler.payload.describe_rules

      orgcrawler -r OrganizationAccountAccessRole --regions us-west-2 orgcrawler.payload.describe_rules | jq -r '.[] | .Account, (.Regions[] | ."us-west-2".ConfigRules[].ConfigRuleName), ""' | tee config_rules_in_accounts.us-west-2
    '''
    client = boto3.client('config', region_name=region, **account.credentials)
    response = client.describe_config_rules()
    rules = response['ConfigRules']
    while 'NextToken' in response:
        response = client.describe_config_rules(NextToken=response['NextToken'])
        rules += response['ConfigRules']
    return dict(ConfigRules=rules)

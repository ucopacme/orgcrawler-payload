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

      orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.config.describe_rules

      orgcrawler -r OrganizationAccountAccessRole --regions us-west-2 orgcrawler.untested_payload.config.describe_rules | jq -r '.[] | .Account, (.Regions[] | ."us-west-2".ConfigRules[].ConfigRuleName), ""' | tee config_rules_in_accounts.us-west-2
    '''
    client = boto3.client('config', region_name=region, **account.credentials)
    response = client.describe_config_rules()
    rules = response['ConfigRules']
    while 'NextToken' in response:
        response = client.describe_config_rules(NextToken=response['NextToken'])
        rules += response['ConfigRules']
    return dict(ConfigRules=rules)


def count_rules(region, account, pattern=None):
    '''
    usage example:

      orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.config.count_rules is3
      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.config.count_rules is3 | jq -r '.[] | .Account, .Regions[].Output.Count'

    '''
    client = boto3.client('config', region_name=region, **account.credentials)
    response = client.describe_config_rules()
    rules = response['ConfigRules']
    while 'NextToken' in response:
        response = client.describe_config_rules(NextToken=response['NextToken'])
        rules += response['ConfigRules']

    if pattern is not None:
        matching_rules = [r for r in rules if r['ConfigRuleName'].startswith(pattern)]
    else:
        matching_rules = rules
    return dict(Count=len(matching_rules))


def get_compliance_details(region, account, rule_name):
    '''
      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.config.get_compliance_details COMPLIANCE_RULESET_LATEST_INSTALLED
      #| jq -r '.[] | .Account, .Regions[].Output.Count'

      botocore.errorfactory.NoSuchConfigRuleException: An error occurred (NoSuchConfigRuleException)
    '''
    client = boto3.client('config', region_name=region, **account.credentials)
    try:
        response = client.get_compliance_details_by_config_rule(ConfigRuleName=rule_name)
        response.pop('ResponseMetadata')
        return response
    except client.exceptions.NoSuchConfigRuleException as ex:
        return {}

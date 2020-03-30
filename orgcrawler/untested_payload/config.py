import re
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
    rule_paganator = paginate(client, client.describe_config_rules)
    return dict(ConfigRules=[rule for rule in rule_paganator])


def get_rule_by_regex(region, account, regex):
    '''
    return list of config rule names matching regex

      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.config.get_rule_by_regex securityhub

    '''
    config_rules = describe_rules(region, account)['ConfigRules']
    rule_re = re.compile(regex)
    matching_rules = [r['ConfigRuleName'] for r in config_rules if rule_re.match(r['ConfigRuleName'])]
    return dict(MatchingRules=matching_rules)


        

 
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


def paginate(client, method, **kwargs):
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result


def get_compliance_details(region, account, rule_name):
    '''
    rule_name can be a regex

      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.config.get_compliance_details COMPLIANCE_RULESET_LATEST_INSTALLED

    '''
    client = boto3.client('config', region_name=region, **account.credentials)
    matching_rules = get_rule_by_regex(region, account, rule_name)['MatchingRules']
    compliance_details = []
    for rule_name in matching_rules:
        response = client.get_compliance_details_by_config_rule(ConfigRuleName=rule_name)
        response.pop('ResponseMetadata')
        compliance_details.append(response)
    return dict(ComplianceDetails=compliance_details)


def get_non_compliant_resources(region, account, rule_name):
    '''
    rule_name can be a regex

      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.config.get_non_compliant_resources securityhub-vpc-default
    '''
    client = boto3.client('config', region_name=region, **account.credentials)
    compliance_details = get_compliance_details(region, account, rule_name)['ComplianceDetails']
    non_compliant_resources = []
    for rule_evaluation in compliance_details:
        for result in rule_evaluation['EvaluationResults']:
            if result['ComplianceType'] == 'NON_COMPLIANT':
                non_compliant_resources.append(result['EvaluationResultIdentifier']['EvaluationResultQualifier'])
    return dict(NonCompliantResources=non_compliant_resources)





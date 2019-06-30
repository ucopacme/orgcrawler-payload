import boto3


def securityhub_list_members(region, account):
    '''
    usage example:

      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.securityhub_list_members
    '''
    client = boto3.client('securityhub', region_name=region, **account.credentials)
    response = client.list_members()
    members = response['Members']
    while 'NextToken' in response:
        response = client.list_members(NextToken=response['NextToken'])
        members += response['Members']
    return dict(Members=members)


def securityhub_list_invitations(region, account):
    '''
    usage example:

      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 --accounts iso-poc orgcrawler.untested_payload.securityhub_list_invitations
    '''
    client = boto3.client('securityhub', region_name=region, **account.credentials)
    response = client.list_invitations()
    invitations = response['Invitations']
    while 'NextToken' in response:
        response = client.list_invitations(NextToken=response['NextToken'])
        invitations += response['Invitations']
    return dict(Invitations=invitations)


def securityhub_is_enabled(region, account):
    '''
    usage example:

      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.securityhub_is_enabled
      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.securityhub_is_enabled \
              | jq -r '.[] | .Account, (.Regions[]."us-west-2".SecurityHubStatus.Enabled), ""'
    '''
    client = boto3.client('securityhub', region_name=region, **account.credentials)
    try:
        client.get_enabled_standards()
        return dict(SecurityHubStatus=dict(Enabled=True))
    except client.exceptions.InvalidAccessException:
        return dict(SecurityHubStatus=dict(Enabled=False))

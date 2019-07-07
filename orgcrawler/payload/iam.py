'''
IAM is a global service.  For all iam payload functions, be sure to use the
option "--service iam" in orgcrawler calls.  This limits the actions to a
single region "us-east-1".
'''

import boto3
from botocore.exceptions import ClientError


def get_account_alias(region, account):
    '''
    Returns the IAM account alias.

    Usage:
      orgcrawler -r ReadOnlyRole --service iam orgcrawler.payload.iam.get_account_alias
    '''
    client = boto3.client('iam', region_name=region, **account.credentials)
    response = client.list_account_aliases()
    return dict(Alias=', '.join(response['AccountAliases']))


def set_account_alias(region, account, dryrun=True, alias=None):
    '''
    Set IAM account alias to `alias`.  If `alias` is unset,
    set alias to the account name.

    Usage:
      orgcrawler -r ReadWriteRole --service iam orgcrawler.payload.iam.set_account_alias dryrun=False
      orgcrawler -r ReadWriteRole --service iam orgcrawler.payload.iam.set_account_alias dryrun=False alias=fluffy
    '''
    client = boto3.client('iam', region_name=region, **account.credentials)
    if alias is None:
        alias = account.name
    if dryrun is True:
        return dict(Dryrun='would have set alias for account {} to {}'.format(account.name, alias))
    else:
        try:
            response = client.create_account_alias(AccountAlias=alias)
            return dict(HTTPStatusCode=response['ResponseMetadata']['HTTPStatusCode'])
        except ClientError as e:  # pragma: no cover
            e.response.pop('ResponseMetadata')
            return e.response
        except client.exceptions.EntityAlreadyExistsException as e:  # pragma: no cover
            e.response.pop('ResponseMetadata')
            return e.response


def list_users(region, account):
    '''
    List IAM User resources.

    Usage:
      orgcrawler -r ReadOnlyRole --service iam orgcrawler.payload.iam.list_users
    '''
    client = boto3.client('iam', region_name=region, **account.credentials)
    response = client.list_users()
    collector = response['Users']
    if 'IsTruncated' in response and response['IsTruncated']:   # pragma: no cover
        response = client.list_users(Marker=response['Marker'])
        collector += response['Users']
    return dict(Users=collector)

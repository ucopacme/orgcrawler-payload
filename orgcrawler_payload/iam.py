import boto3
from botocore.exceptions import ClientError


def set_account_alias(region, account, alias=None):
    client = boto3.client('iam', region_name=region, **account.credentials)
    if alias is None:
        alias = account.name
    client.create_account_alias(AccountAlias=alias)
    return


def get_account_aliases(region, account):
    client = boto3.client('iam', region_name=region, **account.credentials)
    response = client.list_account_aliases()
    return dict(Aliases=', '.join(response['AccountAliases']))


def list_users(region, account):
    '''
    orgcrawler -r awsauth/OrgAdmin --service iam orgcrawler_payload.iam.list_users
    '''
    client = boto3.client('iam', region_name=region, **account.credentials)
    response = client.list_users()
    collector = response['Users']
    if 'IsTruncated' in response and response['IsTruncated']:   # pragma: no cover
        response = client.list_users(Marker=response['Marker'])
        collector += response['Users']
    return dict(Users=collector)


def list_loginprofiles(region, account):
    '''
    orgcrawler -r awsauth/OrgAdmin --service iam orgcrawler-payloads.iam.list_loginprofiles 
    '''
    client = boto3.client('iam', region_name=region, **account.credentials)
    response = client.list_users()
    users = response['Users']
    if 'IsTruncated' in response and response['IsTruncated']:   # pragma: no cover
        response = client.list_users(Marker=response['Marker'])
        users += response['Users']
    login_profiles = []
    for user in users:
        try:
            response = client.get_login_profile(UserName=user['UserName'])
            profile = response['LoginProfile']
            profile['PasswordLastUsed'] = user.get('PasswordLastUsed', "")
            login_profiles.append(profile)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                continue
    return dict(LoginProfiles=login_profiles)


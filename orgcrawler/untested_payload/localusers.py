import boto3
def local_users_list(region, account):
    '''
    usage example:
      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.local_users_list
    '''
    iam_client = boto3.client('iam', region_name=region, **account.credentials)
    user_generator = paginate(iam_client, iam_client.list_users)
    users_list = [user['UserName'] for user in user_generator]
    return dict(Users=users_list)
def paginate(iam_client, method, **kwargs):
    paginator = iam_client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result
~

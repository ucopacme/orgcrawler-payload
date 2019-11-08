import boto3


def paginate(client, method, **kwargs):
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result


def list_eb_environments(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.eb.list_eb_environments
    '''
    client = boto3.client('elasticbeanstalk', region_name=region, **account.credentials)
    env_generator = paginate(client, client.describe_environments)
    env_names = [env['EnvironmentName'] for env in env_generator]
    return dict(Keys=env_names)



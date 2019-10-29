import boto3


def paginate(client, method, **kwargs):
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result


def list_customer_managed_keys(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.kms.list_customer_managed_keys
    '''
    client = boto3.client('kms', region_name=region, **account.credentials)
    cmk_generator = paginate(client, client.list_keys)
    key_descriptions = [client.describe_key(KeyId=cmk['KeyId']) for cmk in cmk_generator]
    customer_managed = [cmk['KeyMetadata'] for cmk in key_descriptions if cmk['KeyMetadata']['KeyManager'] == 'CUSTOMER']
    return dict(Keys=customer_managed)


def list_imported_keys(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.kms.list_imported_keys
    '''
    client = boto3.client('kms', region_name=region, **account.credentials)
    cmk_generator = paginate(client, client.list_keys)
    key_descriptions = [client.describe_key(KeyId=cmk['KeyId']) for cmk in cmk_generator]
    imported_keys = [cmk['KeyMetadata'] for cmk in key_descriptions if cmk['KeyMetadata']['Origin'] == 'EXTERNAL']
    return dict(Keys=imported_keys)


def list_non_enabled_keys(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.kms.list_non_enabled_keys
    '''
    client = boto3.client('kms', region_name=region, **account.credentials)
    cmk_generator = paginate(client, client.list_keys)
    key_descriptions = [client.describe_key(KeyId=cmk['KeyId']) for cmk in cmk_generator]
    non_enabled_keys = [cmk['KeyMetadata'] for cmk in key_descriptions if cmk['KeyMetadata']['Enabled'] is False]
    return dict(Keys=non_enabled_keys)

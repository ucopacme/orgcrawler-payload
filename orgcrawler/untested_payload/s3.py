import boto3
from botocore.exceptions import ClientError

def get_public_access_block(region, account):
    '''
    Retrieve S3 bucket public access block for account

    Usage:
      orgcrawler -r ReadOnlyRole orgcrawler.untested_payload.s3.get_public_access_block regions us-east-1
    '''
    client = boto3.client('s3control', region_name=region, **account.credentials)
    try:
        response = client.get_public_access_block(AccountId=account.id)
        response.pop('ResponseMetadata')
        return response
    except client.exceptions.NoSuchPublicAccessBlockConfiguration as e:
        return dict()


def get_bucket_website(region, account):
    client = boto3.client('s3', region_name=region, **account.credentials)
    buckets = client.list_buckets()['Buckets']
    websites = []
    for bucket in buckets:
        try:
            response = client.get_bucket_website(Bucket=bucket['Name'])
            response.pop('ResponseMetadata')
            response['BucketName'] = bucket['Name']
            websites.append(response)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchWebsiteConfiguration':
                continue
            else:
                raise e
    return dict(Bucket_websites=websites)



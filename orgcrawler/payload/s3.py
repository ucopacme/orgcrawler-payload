import boto3
from botocore.exceptions import ClientError


def create_bucket(region, account, bucket_prefix):
    '''
    usage example:
      orgcrawler -r awsauth/OrgAdmin orgcrawler.payload.create_bucket orgcrawler-testbucket
    '''
    client = boto3.client('s3', region_name=region, **account.credentials)
    bucket_name = '-'.join([bucket_prefix, account.id, region])
    bucket_attributes = {'Bucket': bucket_name}
    if not region == 'us-east-1':
        bucket_attributes['CreateBucketConfiguration'] = {'LocationConstraint': region}
    try:
        response = client.create_bucket(**bucket_attributes)
        operation_outputs = dict(
            BucketName=bucket_name,
            Succeeded=True,
            HTTPStatusCode=response['ResponseMetadata']['HTTPStatusCode']
        )
    except ClientError as e:
        operation_outputs = dict(
            BucketName=bucket_name,
            Succeeded=False,
            ErrorCode=e.response['Error']['Code']
        )
    return dict(CreateBucketOperation=operation_outputs)


def delete_bucket(region, account, bucket_prefix):
    '''
    usage example:
      orgcrawler -r awsauth/OrgAdmin orgcrawler.payload.delete_bucket orgcrawler-testbucket
    '''
    client = boto3.client('s3', region_name=region, **account.credentials)
    bucket_name = '-'.join([bucket_prefix, account.id, region])
    try:
        response = client.delete_bucket(Bucket=bucket_name)
        operation_outputs = dict(
            BucketName=bucket_name,
            Succeeded=True,
            HTTPStatusCode=response['ResponseMetadata']['HTTPStatusCode']
        )
    except ClientError as e:
        operation_outputs = dict(
            BucketName=bucket_name,
            Succeeded=False,
            ErrorCode=e.response['Error']['Code']
        )
    return dict(DeleteBucketOperation=operation_outputs)


def list_buckets(region, account):
    client = boto3.client('s3', region_name=region, **account.credentials)
    response = client.list_buckets()
    return dict(Buckets=[b['Name'] for b in response['Buckets']])

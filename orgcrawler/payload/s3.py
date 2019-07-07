import boto3
from botocore.exceptions import ClientError


def create_bucket(region, account, bucket_prefix, dryrun=True):
    '''
    Creates an S3 bucket with a name using the following pattern:
      <bucket_prefix>-<account.id>-<region>

    Usage:
      orgcrawler -r ReadWriteRole orgcrawler.payload.s3.create_bucket orgcrawler-testbucket
      orgcrawler -r ReadWriteRole orgcrawler.payload.s3.create_bucket orgcrawler-testbucket dryrun=False
    '''
    client = boto3.client('s3', region_name=region, **account.credentials)
    bucket_name = '-'.join([bucket_prefix, account.id, region])
    bucket_attributes = {'Bucket': bucket_name}
    if dryrun is False:
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
    else:
        return dict(Dryrun='would have created bucket {}'.format(bucket_name))


def delete_bucket(region, account, bucket_prefix, dryrun=True):
    '''
    Delete s3 bucket with name matching the following pattern:
      <bucket_prefix>-<account.id>-<region>

    Usage:
      orgcrawler -r ReadWriteRole orgcrawler.payload.s3.delete_bucket orgcrawler-testbucket
      orgcrawler -r ReadWriteRole orgcrawler.payload.s3.delete_bucket orgcrawler-testbucket dryrun=False
    '''
    client = boto3.client('s3', region_name=region, **account.credentials)
    bucket_name = '-'.join([bucket_prefix, account.id, region])
    if dryrun is False:
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
    else:
        return dict(Dryrun='would have created bucket {}'.format(bucket_name))


def list_buckets(region, account):
    '''
    List s3 buckets in account.

    Usage:
      orgcrawler -r ReadOnlyRole orgcrawler.payload.s3.list_buckets
    '''
    client = boto3.client('s3', region_name=region, **account.credentials)
    response = client.list_buckets()
    return dict(Buckets=[b['Name'] for b in response['Buckets']])

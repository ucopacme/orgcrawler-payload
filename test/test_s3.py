import boto3
from moto import (
    mock_organizations,
    mock_sts,
    mock_s3,
)

from orgcrawler.payload import s3
from orgcrawler.utils import yamlfmt
from orgcrawler.cli.utils import setup_crawler
from .utils import (
    ORG_ACCESS_ROLE,
    SIMPLE_ORG_SPEC,
    build_mock_org,
)

@mock_sts
@mock_organizations
@mock_s3
def test_create_list_delete_buckets():
    org_id, root_id = build_mock_org(SIMPLE_ORG_SPEC)
    crawler = setup_crawler(ORG_ACCESS_ROLE)
    account = crawler.accounts[0]
    region = crawler.regions[0]

    # test create and list
    response = s3.create_bucket(region, account, 'test_bucket')
    print(response)
    assert response['CreateBucketOperation']['BucketName'] == '-'.join(['test_bucket', account.id, region])
    assert response['CreateBucketOperation']['Succeeded'] == True
    assert response['CreateBucketOperation']['HTTPStatusCode'] == 200
    response = s3.list_buckets(region, account)
    print(response)
    assert response['Buckets'][0] == '-'.join(['test_bucket', account.id, region])

    # test error conditions
    response = s3.create_bucket(region, account, 'test_bucket')
    print(response)
    assert response['CreateBucketOperation']['BucketName'] == '-'.join(['test_bucket', account.id, region])
    assert response['CreateBucketOperation']['Succeeded'] == False
    assert response['CreateBucketOperation']['ErrorCode'] == 'BucketAlreadyExists'
    response = s3.delete_bucket(region, account, 'test_bucket')
    print(response)
    assert response['DeleteBucketOperation']['BucketName'] == '-'.join(['test_bucket', account.id, region])
    assert response['DeleteBucketOperation']['Succeeded'] == True
    assert response['DeleteBucketOperation']['HTTPStatusCode'] == 204
    response = s3.delete_bucket(region, account, 'test_bucket')
    print(response)
    assert response['DeleteBucketOperation']['BucketName'] == '-'.join(['test_bucket', account.id, region])
    assert response['DeleteBucketOperation']['Succeeded'] == False
    assert response['DeleteBucketOperation']['ErrorCode'] == 'NoSuchBucket'

    # test edge case for location constraint
    region = 'us-east-1'
    response = s3.create_bucket(region, account, 'test_bucket')
    print(response)
    assert response['CreateBucketOperation']['Succeeded'] == True
    response = s3.list_buckets(region, account)
    print(response)
    assert response['Buckets'][0] == '-'.join(['test_bucket', account.id, region])

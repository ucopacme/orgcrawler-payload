from moto import (
    mock_organizations,
    mock_sts,
    mock_s3,
)

from orgcrawler.cli.utils import setup_crawler
from orgcrawler.mock.org import (
    MockOrganization,
    ORG_ACCESS_ROLE,
)
from orgcrawler.payload import s3


@mock_sts
@mock_organizations
@mock_s3
def test_create_list_delete_buckets():
    MockOrganization().simple()
    crawler = setup_crawler(ORG_ACCESS_ROLE)
    account = crawler.accounts[0]
    region = crawler.regions[0]
    bucket_name = '-'.join(['test_bucket', account.id, region])

    # test create and list
    response = s3.create_bucket(region, account, 'test_bucket')
    assert 'Dryrun' in response
    response = s3.create_bucket(region, account, 'test_bucket', dryrun=False)
    assert response['CreateBucketOperation']['BucketName'] == bucket_name
    assert response['CreateBucketOperation']['Succeeded'] is True
    assert response['CreateBucketOperation']['HTTPStatusCode'] == 200
    response = s3.list_buckets(region, account)
    assert response['Buckets'][0] == bucket_name

    # test delete bucket
    response = s3.delete_bucket(region, account, 'test_bucket')
    assert 'Dryrun' in response
    response = s3.delete_bucket(region, account, 'test_bucket', dryrun=False)
    assert response['DeleteBucketOperation']['BucketName'] == bucket_name
    assert response['DeleteBucketOperation']['Succeeded'] is True
    assert response['DeleteBucketOperation']['HTTPStatusCode'] == 204

    # test edge case for location constraint
    response = s3.create_bucket('us-east-1', account, 'test_bucket', dryrun=False)
    assert response['CreateBucketOperation']['Succeeded'] is True

    # test error cases
    response = s3.create_bucket(region, account, 'test_bucket', dryrun=False)
    response = s3.create_bucket(region, account, 'test_bucket', dryrun=False)
    assert response['CreateBucketOperation']['Succeeded'] is False
    assert response['CreateBucketOperation']['ErrorCode'] == 'BucketAlreadyExists'
    response = s3.delete_bucket(region, account, 'test_bucket', dryrun=False)
    response = s3.delete_bucket(region, account, 'test_bucket', dryrun=False)
    assert response['DeleteBucketOperation']['Succeeded'] is False
    assert response['DeleteBucketOperation']['ErrorCode'] == 'NoSuchBucket'

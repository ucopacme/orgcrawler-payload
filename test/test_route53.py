import boto3
from moto import (
    mock_organizations,
    mock_sts,
    mock_route53,
)

from orgcrawler.cli.utils import setup_crawler
from orgcrawler.mock.org import (
    MockOrganization,
    ORG_ACCESS_ROLE,
)
from orgcrawler.payload import route53


@mock_sts
@mock_organizations
@mock_route53
def test_list_hosted_zones():
    MockOrganization().simple()
    crawler = setup_crawler(ORG_ACCESS_ROLE)
    account = crawler.accounts[0]
    region = crawler.regions[0]
    client = boto3.client('route53', region_name=region, **account.credentials)
    client.create_hosted_zone(
        Name='test_zone.example.com',
        CallerReference='a_unique_string'
    )
    response = route53.list_hosted_zones(region, account)
    assert response['HostedZones'][0]['Name'] == 'test_zone.example.com.'

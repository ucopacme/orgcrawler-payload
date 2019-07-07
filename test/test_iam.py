import boto3
from moto import (
    mock_organizations,
    mock_sts,
    mock_iam,
)

from orgcrawler.cli.utils import setup_crawler
from orgcrawler.mock.org import (
    MockOrganization,
    ORG_ACCESS_ROLE,
)
from orgcrawler.payload import iam


@mock_sts
@mock_organizations
@mock_iam
def test_list_users():
    MockOrganization().simple()
    crawler = setup_crawler(ORG_ACCESS_ROLE)
    account = crawler.accounts[0]
    region = crawler.regions[0]
    client = boto3.client('iam', region_name=region, **account.credentials)
    client.create_user(UserName='test_user')
    response = iam.list_users(region, account)
    assert response['Users'][0]['UserName'] == 'test_user'


@mock_sts
@mock_organizations
@mock_iam
def test_get_set_account_aliases():
    MockOrganization().simple()
    crawler = setup_crawler(ORG_ACCESS_ROLE)
    account = crawler.accounts[0]
    region = crawler.regions[0]
    response = iam.set_account_alias(region, account)
    assert 'Dryrun' in response
    response = iam.get_account_alias(region, account)
    assert response['Alias'] == ''
    response = iam.set_account_alias(region, account, dryrun=False)
    assert response['HTTPStatusCode'] == 200
    response = iam.get_account_alias(region, account)
    assert response['Alias'] == account.name
    response = iam.set_account_alias(region, account, dryrun=False, alias='fluffy')
    assert response['HTTPStatusCode'] == 200
    response = iam.get_account_alias(region, account)
    assert response['Alias'] == 'fluffy'

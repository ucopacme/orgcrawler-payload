import boto3
from moto import (
    mock_organizations,
    mock_sts,
    mock_iam,
)

from orgcrawler import payloads
from orgcrawler.utils import yamlfmt
from orgcrawler.cli.utils import setup_crawler
from .utils import (
    ORG_ACCESS_ROLE,
    SIMPLE_ORG_SPEC,
    build_mock_org,
)


@mock_sts
@mock_organizations
@mock_iam
def test_iam_list_users():
    org_id, root_id = build_mock_org(SIMPLE_ORG_SPEC)
    crawler = setup_crawler(ORG_ACCESS_ROLE)
    account = crawler.accounts[0]
    region = crawler.regions[0]
    client = boto3.client('iam', region_name=region, **account.credentials)
    client.create_user(UserName='test_user')
    response = payloads.iam_list_users(region, account)
    assert response['Users'][0]['UserName'] == 'test_user'


@mock_sts
@mock_organizations
@mock_iam
def test_get_set_account_aliases():
    org_id, root_id = build_mock_org(SIMPLE_ORG_SPEC)
    crawler = setup_crawler(ORG_ACCESS_ROLE)
    account = crawler.accounts[0]
    region = crawler.regions[0]
    response = payloads.set_account_alias(region, account)
    response = payloads.get_account_aliases(region, account)
    assert response['Aliases'] == account.name
    response = payloads.set_account_alias(region, account, alias='test_alias')
    response = payloads.get_account_aliases(region, account)
 

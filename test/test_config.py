import boto3
from moto import (
    mock_organizations,
    mock_sts,
    mock_config,
)

from orgcrawler.payload import config
from orgcrawler.utils import yamlfmt
from orgcrawler.cli.utils import setup_crawler
from .utils import (
    ORG_ACCESS_ROLE,
    SIMPLE_ORG_SPEC,
    build_mock_org,
)



@mock_sts
@mock_organizations
@mock_config
def test_resource_counts():
    pass
    #NotImplementedError: The get_discovered_resource_counts action has not been implemented
    #response = config.resource_counts(region, account)


@mock_sts
@mock_organizations
@mock_config
def test_config_describe_rules():
    pass
    #NotImplementedError: The describe_config_rules action has not been implemented
    #response = config.describe_rules(region, account)


@mock_sts
@mock_organizations
@mock_config
def test_describe_recorder_status():
    org_id, root_id = build_mock_org(SIMPLE_ORG_SPEC)
    crawler = setup_crawler(ORG_ACCESS_ROLE)
    account = crawler.accounts[0]
    region = crawler.regions[0]
    client = boto3.client('config', region_name=region, **account.credentials)
    client.put_configuration_recorder(ConfigurationRecorder={
        'name': 'config_test',
        'roleARN': 'config_test',
    })
    response = config.describe_recorder_status(region, account)
    assert response['ConfigurationRecordersStatus'][0]['name'] == 'config_test'


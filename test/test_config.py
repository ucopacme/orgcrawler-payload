import boto3
from moto import (
    mock_organizations,
    mock_sts,
    mock_config,
)

from orgcrawler.cli.utils import setup_crawler
from orgcrawler.mock.org import (
    MockOrganization,
    ORG_ACCESS_ROLE,
)
from orgcrawler.payload import config


@mock_sts
@mock_organizations
@mock_config
def test_describe_recorder_status():
    MockOrganization().simple()
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

import boto3


def describe_recorder_status(region, account):
    '''
    Returns the ConfiguratiionRecorder status.

    Usage:
      orgcrawler -r ReadOnlyRole orgcrawler.payload.config.describe_recorder_status

    '''
    client = boto3.client('config', region_name=region, **account.credentials)
    response = client.describe_configuration_recorder_status()
    response.pop('ResponseMetadata')
    return response

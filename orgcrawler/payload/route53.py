import boto3


def list_hosted_zones(region, account):
    '''
    Returns listing of Route53 HostedZones together with
    all configure ResourceRecord sets.

    Usage:
      orgcrawler -r ReadOnlyRole --service route53 orgcrawler.payload.route53.list_hosted_zones
    '''
    client = boto3.client('route53', region_name=region, **account.credentials)
    response = client.list_hosted_zones()
    hosted_zones = []
    for zone in response['HostedZones']:
        response = client.list_resource_record_sets(HostedZoneId=zone['Id'])
        hosted_zones.append(dict(
            Name=zone['Name'],
            Id=zone['Id'],
            RecordSets=response['ResourceRecordSets'],
        ))
    return dict(HostedZones=hosted_zones)

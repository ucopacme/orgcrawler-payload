import boto3
def list_tags(region, account):
    '''
    usage example:
      orgcrawler -r awsauth/OrgAdmin --regions us-west-2 orgcrawler.untested_payload.costexplorer.list_tags
    '''
    ce_client = boto3.client('ce', region_name=region, **account.credentials)
    response = ce_client.get_tags(TimePeriod={
        'Start': '2020-01-01' , 
        'End': '2020-01-23'})
    tags = response['Tags']
    while 'NextToken' in response:
        response = ce_client.get_tags(NextToken=response['NextToken'])
        #tags += response['TagKey']
        tags += response['Tags']
    #return dict(TagKey=tags)
    return dict(Tags=response)

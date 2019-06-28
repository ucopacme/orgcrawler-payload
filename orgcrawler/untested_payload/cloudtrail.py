import re
import boto3


def check_status(region, account):
    client = boto3.client('cloudtrail', region_name=region, **account.credentials)
    response = client.describe_trails()
    trail_accounts = []
    for trail in response['trailList']:
        x = re.findall(r"\BloudTrail", trail["Name"])
        if x:
            trail_accounts.append(dict(
                Name=trail['Name'],
                status="enabled",
            ))
    return dict(TrailAccounts=trail_accounts)

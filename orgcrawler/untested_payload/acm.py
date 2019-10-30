'''
check for:

    unused certs
    expired certs
    email validation
    dns validation
    RenewalEligibility


'''


import boto3


def paginate(client, method, **kwargs):
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result

def get_cert_descriptions(client):
    acm_generator = paginate(client, client.list_certificates)
    cert_descriptions = [client.describe_certificate(CertificateArn=acm['CertificateArn']) for acm in acm_generator]
    return cert_descriptions

def list_ineligible_renewal_certs(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_ineligible_renewal_certs
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client)
    renewal_ineligible = [acm['Certificate'] for acm in cert_descriptions if acm['Certificate']['RenewalEligibility'] == 'INELIGIBLE']
    return dict(Certificates=renewal_ineligible)




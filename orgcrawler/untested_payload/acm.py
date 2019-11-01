'''
check for:

    unused certs
    expired certs
    email validation
    dns validation
    RenewalEligibility


'''

keys = [
    'CertificateArn',
    'DomainName',
    'Issuer',
    'Type',
    'Status',
    'CreatedAt',
    'IssuedAt',
    'NotBefore',
    'NotAfter',
    'InUseBy',
    'RenewalEligibility',
]

import boto3
import datetime


def paginate(client, method, **kwargs):
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result

def get_cert_descriptions(client):
    acm_generator = paginate(client, client.list_certificates)
    cert_descriptions = [client.describe_certificate(CertificateArn=acm['CertificateArn']) for acm in acm_generator]
    return cert_descriptions


def format_cert(cert, keys):
    formated = {}
    for k in keys:
        formated[k] = cert.get(k)
    return formated


def list_certs(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_certs
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    return dict(Certificates=get_cert_descriptions(client))


def list_ineligible_renewal_certs(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_ineligible_renewal_certs
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client)
    renewal_ineligible = [acm['Certificate'] for acm in cert_descriptions if acm['Certificate']['RenewalEligibility'] == 'INELIGIBLE']
    return dict(Certificates=renewal_ineligible)


def list_unused_certs(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_unused_certs
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_unused_certs --regions us-east-1,us-west-2  | jq -r '.[].Regions[].Output.Certificates[].CertificateArn'
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client)
    unused = [format_cert(acm['Certificate'], keys) for acm in cert_descriptions if not acm['Certificate']['InUseBy']]
    #unused = [acm['Certificate' for acm in cert_descriptions if not acm['Certificate']['InUseBy']]
    return dict(Certificates=unused)


def is_expired(cert):
    expire_date = cert.get('NotAfter')
    if expire_date:
        return expire_date < datetime.datetime.now(datetime.timezone.utc)
    return True


def list_expired_certs(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_expired_certs
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client)
    expired = [format_cert(acm['Certificate'], keys) for acm in cert_descriptions if is_expired(acm['Certificate'])]
    return dict(Certificates=expired)




'''
check for:

    unused certs
    expired certs
    email validation
    dns validation
    RenewalEligibility


'''

import boto3
import datetime


MINIMAL = [
    'DomainName',
    'CertificateArn',
    'Status'
]

BASIC = [
    'Account',
    'Region',
    'DomainName',
    'CertificateArn',
    'Issuer',
    'Type',
    'Status',
    'CreatedAt',
    'IssuedAt',
    'NotBefore',
    'NotAfter',
    'ValidationDomain',
    'ValidationStatus',
    'ValidationMethod',
    'RenewalEligibility',
    'RenewalStatus',
    'InUseBy'

]

KEY_PATTERNS = {
    'basic': BASIC,
    'mimimal': MINIMAL,
    'verbose': None,
}


def format_cert(cert, keys):
    if isinstance(keys, str):
        if keys in KEY_PATTERNS:
            keys = KEY_PATTERNS[keys]
        else:
            keys = keys.split(',')
    if keys is None:
        return cert
    cert.update(get_validation_options(cert))
    cert.update(get_renewal_status(cert))
    formated = {}
    for k in keys:
        if k in cert and cert[k] is not None:
            formated[k] = cert[k]
    return formated


def paginate(client, method, **kwargs):
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result

def get_cert_descriptions(client, account=None, region=None):
    acm_generator = paginate(client, client.list_certificates)
    cert_descriptions = [client.describe_certificate(CertificateArn=acm['CertificateArn'])['Certificate'] for acm in acm_generator]
    extras = dict()
    if account is not None:
        extras['Account'] = account.name
    if region is not None:
        extras['Region'] = region
    [cert.update(extras) for cert in cert_descriptions]
    return cert_descriptions


def is_expired(cert):
    expire_date = cert.get('NotAfter')
    if expire_date:
        return expire_date < datetime.datetime.now(datetime.timezone.utc)
    return False


def get_renewal_status(cert):
    if 'RenewalSummary' in cert:
        return dict(RenewalStatus=cert['RenewalSummary']['RenewalStatus'])
    return dict(RenewalStatus=None)


def get_validation_options(cert):
    options = next((opt for opt in cert['DomainValidationOptions'] if opt['DomainName'] == cert['DomainName']), None)
    return {
        'ValidationDomain': options.get('ValidationDomain'),
        'ValidationStatus': options.get('ValidationStatus'),
        'ValidationMethod': options.get('ValidationMethod'),
    }


'''
Payload Functions
'''

def list_certs(region, account, keys='verbose'):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_certs
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_certs DomainName,CertificateArn --accounts was-build --regions us-west-2,us-east-1
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    return dict(Certificates=[format_cert(cert, keys) for cert in get_cert_descriptions(client, account, region)])


def list_unused(region, account, keys='basic'):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_unused
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_unused --regions us-east-1,us-west-2  | jq -r '.[].Regions[].Output.Certificates[].CertificateArn'
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client, account, region)
    unused = [format_cert(acm, keys) for acm in cert_descriptions if not acm['InUseBy']]
    return dict(Certificates=unused)


def list_expired(region, account, keys='basic'):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_expired
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client, account, region)
    expired = [format_cert(acm, keys) for acm in cert_descriptions if is_expired(acm)]
    return dict(Certificates=expired)


def list_renewal_failed(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_renewal_failed
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client)
    failed_renewal = [acm for acm in cert_descriptions if 'RenewalSummary' in acm and acm['RenewalSummary']['RenewalStatus'] == 'FAILED']
    return dict(Certificates=failed_renewal)


def list_renewal_pending(region, account):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_renewal_pending
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client)
    failed_renewal = [acm for acm in cert_descriptions if 'RenewalSummary' in acm and acm['RenewalSummary']['RenewalStatus'].startswith('PENDING')]
    return dict(Certificates=failed_renewal)


'''
the function below can be duplicated easily with jq:

    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_certs basic > acm_certs.basic
    cat acm_certs.basic  | jq -r '.[].Regions[].Output.Certificates[] | select(.RenewalEligibility != "INELIGIBLE") | .'
    cat acm_certs.basic  | jq -r '.[].Regions[].Output.Certificates[] | select(.Status == "VALIDATION_TIMED_OUT") | .'
    cat acm_certs.basic  | jq -r '.[].Regions[].Output.Certificates[] | select(.Type == "IMPORTED") | .'

some other fun queries:
    cat acm_certs.basic  | jq -r '.[].Regions[].Output.Certificates[] | select(.Status != "ISSUED") | .'
    cat acm_certs.basic  | jq -r '.[].Regions[].Output.Certificates[] | select(.ValidationMethod != "EMAIL") | .'
'''


def list_renewal_ineligible(region, account, keys='basic'):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_renewal_ineligible
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client, account, region)
    renewal_ineligible = [format_cert(acm, keys) for acm in cert_descriptions if acm['RenewalEligibility'] == 'INELIGIBLE']
    return dict(Certificates=renewal_ineligible)


def list_validation_timed_out(region, account, keys='basic'):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_validation_timed_out
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_validation_timed_out verbose
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_validation_timed_out minimal
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client, account, region)
    return dict(Certificates=[format_cert(acm, keys) for acm in cert_descriptions if acm['Status'] == 'VALIDATION_TIMED_OUT'])


def list_imported(region, account, keys='basic'):
    '''
    orgcrawler -r OrganizationAccountAccessRole orgcrawler.untested_payload.acm.list_imported
    '''
    client = boto3.client('acm', region_name=region, **account.credentials)
    cert_descriptions = get_cert_descriptions(client, account, region)
    return dict(Certificates=[format_cert(acm, keys) for acm in cert_descriptions if acm['Type'] == 'IMPORTED'])

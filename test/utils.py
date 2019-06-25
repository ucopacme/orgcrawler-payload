import os
import re
import time
import json
import pickle
import shutil

import yaml
import botocore
import boto3
import pytest
import moto
from moto import mock_organizations, mock_sts

from orgcrawler import utils, orgs, crawlers

ORG_ACCESS_ROLE='myrole'
MASTER_ACCOUNT_ID='123456789012'

SIMPLE_ORG_SPEC="""
root:
  - name: root
    policies:
    - policy01
    accounts:
    - name: account01
      policies:
      - policy02
    - name: account02
    - name: account03
    child_ou:
      - name: ou01
        policies:
        - policy03
        child_ou:
          - name: ou01-sub0
      - name: ou02
        child_ou:
          - name: ou02-sub0
      - name: ou03
        child_ou:
          - name: ou03-sub0
"""

COMPLEX_ORG_SPEC="""
root:
  - name: root
    accounts:
    - name: account01
    - name: account02
    - name: account03
    policies:
    - policy01
    - policy02
    child_ou:
      - name: ou01
        accounts:
        - name: account04
          policies:
          - policy01
          - policy03
          - policy04
        - name: account05
        child_ou:
          - name: ou01-1
            accounts:
            - name: account08
          - name: ou01-2
            accounts:
            - name: account09
            - name: account10
            policies:
            - policy01
            - policy05
            - policy06
      - name: ou02
        accounts:
        - name: account06
        - name: account07
          policies:
          - policy01
          - policy05
          - policy06
        child_ou:
          - name: ou02-1
            accounts:
            - name: account11
          - name: ou02-2
            accounts:
            - name: account12
            - name: account13
              policies:
              - policy03
              - policy04
"""

POLICY_DOC = dict(
    Version='2012-10-17',
    Statement=[dict(
        Sid='MockPolicyStatement',
        Effect='Allow',
        Action='s3:*',
        Resource='*',
    )]
)

def mock_org_from_spec(client, root_id, parent_id, spec, policy_list):
    for ou in spec:
        if ou['name'] == 'root':
            ou_id = root_id
        else:
            ou_id = client.create_organizational_unit(
                ParentId=parent_id, 
                Name=ou['name'],
            )['OrganizationalUnit']['Id']
        if 'accounts' in ou:
            for account in ou['accounts']:
                account_id = client.create_account(
                    AccountName=account['name'],
                    Email=account['name'] + '@example.com',
                )['CreateAccountStatus']['AccountId']
                client.move_account(
                    AccountId=account_id,
                    SourceParentId=root_id,
                    DestinationParentId=ou_id,
                )
                if 'policies' in account:
                    for policy_name in account['policies']:
                        policy = next((
                            p for p in policy_list if p['Name'] == policy_name
                        ), None)
                        if policy is None:
                            policy = client.create_policy(
                                Name=policy_name,
                                Type='SERVICE_CONTROL_POLICY',
                                Content=json.dumps(POLICY_DOC),
                                Description='Mock service control policy',
                            )['Policy']['PolicySummary']
                            policy_list.append(policy)
                        client.attach_policy(
                            PolicyId=policy['Id'],
                            TargetId=account_id,
                        )
        if 'policies' in ou:
            for policy_name in ou['policies']:
                policy = next((
                    p for p in policy_list if p['Name'] == policy_name
                ), None)
                if policy is None:
                    policy = client.create_policy(
                        Name=policy_name,
                        Type='SERVICE_CONTROL_POLICY',
                        Content=json.dumps(POLICY_DOC),
                        Description='Mock service control policy',
                    )['Policy']['PolicySummary']
                    policy_list.append(policy)
                client.attach_policy(
                    PolicyId=policy['Id'],
                    TargetId=ou_id,
                )
        if 'child_ou' in ou:
            mock_org_from_spec(client, root_id, ou_id, ou['child_ou'], policy_list)


def build_mock_org(spec):
    org = orgs.Org(MASTER_ACCOUNT_ID, ORG_ACCESS_ROLE)
    client = org._get_org_client()
    client.create_organization(FeatureSet='ALL')
    org_id = client.describe_organization()['Organization']['Id']
    root_id = client.list_roots()['Roots'][0]['Id']
    mock_org_from_spec(client, root_id, root_id, yaml.load(spec)['root'], list())
    return (org_id, root_id)

def clean_up(org=None):
    if org is None:
        org = orgs.Org(MASTER_ACCOUNT_ID, ORG_ACCESS_ROLE)
    if os.path.isdir(org._cache_dir):
        shutil.rmtree(org._cache_dir)



OrgCrawler Payloads
===================

A library of curated OrgCrawler payload functions.

orgcrawler-payload is a sub-package within the OrgCrawler_ name space.  See
the `Orgcrawler Readthedocs`_ page for full documentation of the OrgCrawler
suite of tools.


Installation
------------

::

  pip install orgcrawler-payload


Package Organization
--------------------

**orgcrawler.payload**
  The modules in ``orgcrawler.payload`` contain fully tested and supported
  payload functions divided according to AWS service.

  ::
  
    orgcrawler/payload/
                      /iam.py
                      /route53.py
                      /s3.py
                      /config.py

**orgcrawler.untested_payload**
  The modules in ``orgcrawler.untested_payload`` contain untested or
  experimental payload functions.  Many of these functions lack unit tests only
  because the `Moto`_ library we use to mock AWS Services does not yet
  support a particular AWS API.  In time we expect to migrate them into the 
  ``orgcrawler.payload`` collection.

  **WARNING!!** Functions in ``orgcrawler.untested_payload`` are **NOT**
  supported.  Use at your own risk.
  
  ::

    orgcrawler/untested_payload/
                               /iam.py
                               /cloudtrail.py
                               /securityhub.py
                               /cloudformation.py
                               /ec2.py
                               /config.py


.. _OrgCrawler: https://github.com/ucopacme/orgcrawler
.. _`OrgCrawler Readthedocs`: https://orgcrawler.readthedocs.io/en/latest/
.. _Moto: https://github.com/spulec/moto


Calling OrgCrawler payload functions
------------------------------------

For general usage of OrgCrawler payload functions in python modules or with the
``orgcrawler`` CLI tool, see the `OrgCrawler Readthedocs`_ page.

Supported payload functions under ``orgcrawler.payload`` each contain function
specific usage information in the function doc string.  This is accessible from
the python ``help()`` system::

  >>> import orgcrawler.payload.iam
  >>> help(orgcrawler.payload.iam)
  Help on module orgcrawler.payload.iam in orgcrawler.payload:
  
  NAME
      orgcrawler.payload.iam
  
  DESCRIPTION
      IAM is a global service.  For all iam payload functions, be sure to use the
      option "--service iam" in orgcrawler calls.  This limits the actions to a
      single region "us-east-1".
  
  FUNCTIONS
      get_account_alias(region, account)
          Returns the IAM account alias.
          
          Usage:
            orgcrawler -r ReadOnlyRole --service iam orgcrawler.payload.iam.get_account_alias
      
      list_users(region, account)
          List IAM User resources.
          
          Usage:
            orgcrawler -r ReadOnlyRole --service iam orgcrawler.payload.iam.list_users
      
      set_account_alias(region, account, dryrun=True, alias=None)
          Set IAM account alias to `alias`.  If `alias` is unset,
          set alias to the account name.
          
          Usage:
            orgcrawler -r ReadWriteRole --service iam orgcrawler.payload.iam.set_account_alias dryrun=False
            orgcrawler -r ReadWriteRole --service iam orgcrawler.payload.iam.set_account_alias dryrun=False alias=fluffy



Structure of OrgCrawler payload functions
-----------------------------------------

An OrgCrawler payload function is essentially a wrapper allowing us to run
arbitrary boto3 AWS-SDK python code (the payload) across multiple accounts and
regions.

A payload function has two essential components:

**function definition**
  The ``orgcrawler.crawlers.Crawler.execute`` method passes the following 
  parameters to payload functions::
 
    region (str):        an AWS region
    account (object):    an orgcrawler.orgs.OrgAccount object
    *args:               any positional args
    **qwargs:            any keyword args

  The payload function definition must include positional parameters
  ``(region, account)``.  Additional arguments specific to the payload code
  itself can follow as required.

**boto3 client definition**
  The payload function must create its own boto3 client for whatever services
  it will use by calling ``boto3.client()`` with the service, region and STS
  assume-role credentials.  The STS credentials are extracted from the ``account`` parameter as
  ``**account.credentials``.
 
Format
******

::

  def my_function(region, account [arg1, arg2, ..., kwarg1=val1, kwarg2=val2, ...]):
      client = boto3.client('<service-name>', region_name=region, **account.credentials)
      <your code here>

Examples::

  def list_iam_users(region, account):
      client = boto3.client('iam', region_name=region, **account.credentials)

  def create_bucket(region, account, bucket_prefix, dryrun=True):
      client = boto3.client('s3', region_name=region, **account.credentials)

  def update_account_password_policy(region, account, dryrun=True, policy_attributes=None):
      client = boto3.client('iam', region_name=region, **account.credentials)


Writing unit tests for OrgCrawler payload functions
--------------------------------------------------

This package uses the Pytest_ and Moto_ for running unit tests in a mock AWS
environment.  Each test file imports some form or the following to provide this
environment.  In this example we are testing IAM payloads::

  # moto decorators for mocking AWS service APIs
  import boto3
  from moto import (
      mock_organizations,
      mock_sts,
      mock_iam,
  )
  
  # orgcrawler utilities for building a mock AWS Organization
  from orgcrawler.cli.utils import setup_crawler 
  from orgcrawler.mock.org import (
      MockOrganization,
      ORG_ACCESS_ROLE,
  )

  # payload module we are testing
  from orgcrawler.payload import iam


Test functions are prefixed with moto decorators, so that they run mock AWS
environment.  Each function sets up a mock organization and Crawler instance.
The payload function itself only needs to be tested in as single account and
region.  We extract the ``region`` and ``account`` parameters from the Crawler
instance and pass them to the payload function::
  
  # moto decorators
  @mock_sts
  @mock_organizations
  @mock_iam
  def test_get_set_account_aliases():

      # mock organization and Crawler instance
      MockOrganization().simple()
      crawler = setup_crawler(ORG_ACCESS_ROLE)

      # call payload in a single region and account
      account = crawler.accounts[0]
      region = crawler.regions[0]
      response = iam.set_account_alias(region, account)


.. _Pytest: https://docs.pytest.org/en/latest/

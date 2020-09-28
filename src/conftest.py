import pytest
from datetime import datetime

from moto import mock_s3
import boto3
import os
from datetime import datetime
from results import SizeFormat, BucketInfo, ResultHandler, display_file_size, display_last_mod
from access import explore_bucket, AccessHandler

BUCKET1 = 'BUCKET1'
CREATION_OF_BUCKET1 = datetime(2020,9,25)
DEFAULT_PROFILE = 'default'
DEFAULT_DATE_FORMAT = '%Y_%m_%d'
EXAMPLE_CREDS_FILE = 'installation_support/cred_EXAMPLE.json'

@pytest.fixture
def bucket_name():
    return BUCKET1


@pytest.fixture
def created_date():
    return CREATION_OF_BUCKET1


@pytest.fixture
def mock_bucket_info():
    return BucketInfo(BUCKET1, CREATION_OF_BUCKET1)


@pytest.fixture  # (autouse=True)
@mock_s3
def s3_client():
    sess = boto3.Session(
        aws_access_key_id= "AKIAIOSFODNN7EXAMPLE",
        aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    )
    _s3_conn = sess.client('s3')
    return _s3_conn


@pytest.fixture
def result_handler():
    return ResultHandler(date_display_format=DEFAULT_DATE_FORMAT,
                         size_display_format=SizeFormat.MB,
                         profile_name=DEFAULT_PROFILE)


@pytest.fixture
def access_handler():
    return AccessHandler(profile_name=DEFAULT_PROFILE,
                         cred_path=EXAMPLE_CREDS_FILE)


@pytest.fixture
def profile_name():
    return DEFAULT_PROFILE


@pytest.fixture
def example_creds_path():
    return EXAMPLE_CREDS_FILE


@pytest.fixture
def mock_s3_credentials():
    return dict(
        aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
        aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    )

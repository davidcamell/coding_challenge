from moto import mock_s3
from access import explore_bucket
import tempfile
import os


@mock_s3
def test_explore_bucket(mock_bucket_info, s3_client, bucket_name):
    """
    Create a bucket using mock S3, add three fake files
    of escalating sizes 1024, 2048, and 3072.
    Can pass in parameters, or just use pytest fixtures.

    :param mock_bucket_info: BucketInfo object before Bucket exploration.
    :param s3_client: boto3 s3 client object to use in test.
    :param bucket_name: String name expected of bucket,
    expected to be same as mock_bucket_info
    """

    s3_client.create_bucket(Bucket=bucket_name)

    with tempfile.TemporaryDirectory() as temp_dir:
        for n in range(1, 4):
            tf_path = os.path.join(temp_dir, 'temp_file{}'.format(n))
            with open(tf_path, 'w') as fw:
                fw.truncate(n*1024)

            s3_client.upload_file(tf_path, bucket_name, 'dir_a/file_{}.txt'.format(n))

    test_info = explore_bucket(mock_bucket_info, s3_client)
    assert test_info.name == bucket_name
    assert test_info.file_count == 3
    assert test_info.cumulative_size == 6*1024


def test_asset_handler_types(access_handler):
    """
    Basic test that asset_handler is passing back expected object types.
    :param access_handler: AccessHandler object to be tested; can just use pytest fixture.
    """
    # Using type & str conversion here because isinstance does not work for these objects
    assert str(type(access_handler.s3_client)) == "<class 'botocore.client.S3'>"
    assert str(type(access_handler.s3_resource)) == "<class 'boto3.resources.factory.s3.ServiceResource'>"


def test_asset_handler_creds(access_handler, mock_s3_credentials, profile_name, example_creds_path):
    """

    :param access_handler: AccessHandler object to be tested; can just use pytest fixture.
    :param mock_s3_credentials: Expected output to compare against. Pytest fixture is fake AWS creds of correct format.
    :param profile_name: Specific set of credentials to be extracted.
    :param example_creds_path: Path for cred file to be tested. By default, just pointing to original example included.
    """
    assert access_handler._fetch_creds(profile_name, example_creds_path) == mock_s3_credentials

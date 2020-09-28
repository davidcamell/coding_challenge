import os
import json
import boto3


APP_HOME = os.environ['S3X_PATH']

CONTENTS = 'Contents'
KEY = 'Key'
SIZE = 'Size'
LAST_MODIFIED = 'LastModified'
IS_TRUNCATED = 'IsTruncated'
NEXT_CONTINUATION_TOKEN = 'NextContinuationToken'


def explore_bucket(my_info, s3_client):
    """
    This is the 'star of the show', which does one of the two main jobs,
    in this case traversing the bucket and gathering desired information.

    :param my_info: An initiated BucketInfo object not yet containing detailed file info.
    :type my_info: BucketInfo
    :param s3_client: The client that will be used to gain access to AWS.
    :type s3_client: boto3.s3.client
    :return: Returns the BucketInfo data structure now filled in with results
    :rtype: BucketInfo
    """

    keep_fetching = True
    cont_token = None
    search_params = dict(Bucket=my_info.name)
    while keep_fetching:
        keep_fetching = False
        if cont_token is not None:
            search_params.update(dict(ContinuationToken=cont_token))

        resp = s3_client.list_objects_v2(**search_params)

        if CONTENTS in resp:
            for obj in resp[CONTENTS]:
                if not obj[KEY].endswith('/'):
                    my_info.add_file(obj[SIZE], obj[LAST_MODIFIED])
        if IS_TRUNCATED in resp:
            keep_fetching = resp[IS_TRUNCATED]
        if keep_fetching:
            cont_token = resp[NEXT_CONTINUATION_TOKEN]
    return my_info


class AccessHandler:
    """
    This encapsulates the initiation of an s3 client, depending on
    whether the user has AWS CLI installed and will use pre-exisitng
    credentials, or they will edit the app-specific .cred.json
    """
    CREDENTIALS_PATH = 'data/.cred.json'
    AWS_PROFILES = 'aws_profiles'

    def __init__(
            self,
            profile_name,
            use_aws_cli_profiles=False,
            cred_path=CREDENTIALS_PATH
    ):
        if use_aws_cli_profiles:
            # This simply preps a parameter that boto3 will ingest
            creds = dict(profile_name=profile_name)
        else:
            # Here we will use the custom json stored credentials
            # in the absense of AWS CLI profiles
            creds = self._fetch_creds(profile_name,
                                      os.path.join(APP_HOME, cred_path))
        self._session = boto3.Session(**creds)
        self.s3_client = self._session.client('s3')
        self.s3_resource = self._session.resource('s3')

    @staticmethod
    def _fetch_creds(
            profile_name,
            cred_path,
            profiles_key=AWS_PROFILES
    ):
        # First just load the entire file
        with open(cred_path, 'r') as fp:
            data_load = json.load(fp)

        # There is a nested dict here in case future expansion of
        # useful information we may want to include in the json
        # In addition, it is a good way to guarantee we are looking
        # at the expected file format so there is no confusion.
        if (isinstance(data_load, dict)) and (profiles_key in data_load):
            dict_creds = data_load[profiles_key]
        else:
            ValueError('File "{}" is not in the correct format for credential storage.'.format(cred_path))

        # Does profile information exist? We are more confident this is
        # at least the right format file because of the above check,
        # so here we can be clear that if the key for the corresponding
        # profile is missing, it is specifically because the profile is not found
        # and (probably) not because we are looking at a random file.
        if profile_name in dict_creds:
            return dict_creds[profile_name]
        else:
            raise ValueError('Profile "{}" is not found.'.format(profile_name))

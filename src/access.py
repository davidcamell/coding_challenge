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


class AccessHandler():

    CREDENTIALS_PATH = 'data/.cred.json'
    AWS_PROFILES = 'aws_profiles'

    def __init__(
            self,
            profile_name,
            use_aws_cli_profiles=False,
            cred_path=CREDENTIALS_PATH
    ):
        if use_aws_cli_profiles:
            creds = dict(profile_name=profile_name)
        else:
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
        with open(cred_path, 'r') as fp:
            data_load = json.load(fp)

        if (isinstance(data_load, dict)) and (profiles_key in data_load):
            dict_creds = data_load[profiles_key]
        else:
            ValueError('File "{}" is not in the correct format for credential storage.'.format(cred_path))

        if profile_name in dict_creds:
            return dict_creds[profile_name]
        else:
            raise ValueError('Profile "{}" is not found.'.format(profile_name))

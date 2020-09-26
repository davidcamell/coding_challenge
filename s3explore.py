import boto3
from typing import NamedTuple
import json
import logging
# import pandas as pd
from datetime import datetime

CONTENTS = 'Contents'
SIZE = 'Size'
LAST_MODIFIED = 'LastModified'
IS_TRUNCATED = 'IsTruncated'
NEXT_CONTINUATION_TOKEN = 'NextContinuationToken'


class AccessHandler():

    CREDENTIALS_PATH = 'cred.json'
    DEFAULT = 'default'
    AWS_PROFILES = 'aws_profiles'

    def __init__(
            self,
            profile_name=DEFAULT
    ):
        creds = self.fetch_creds(profile_name)
        # self.session = self.initiate_s3(**creds)
        self._session = boto3.Session(**creds)
        self.s3_client = self._session.client('s3')
        self.s3_resource = self._session.resource('s3')

    @staticmethod
    def fetch_creds(
            profile_name,
            cred_path=CREDENTIALS_PATH,
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

    # @staticmethod
    # def initiate_s3(
    #         aws_profile=None,
    #         aws_access_key_id=None,
    #         aws_secret_access_key=None
    # ):
    #     if aws_profile is None:
    #         session = boto3.Session(
    #             aws_access_key_id=aws_access_key_id,
    #             aws_secret_access_key=aws_secret_access_key
    #         )
    #     else:
    #         session = boto3.Session(
    #             aws_profile=aws_profile
    #         )
    #     return session


def explore_bucket(bucket, s3_handler):
    # logger = logging.getLogger(__name__)

    cumulative_size = 0
    file_count = 0
    most_recent_mod = None
    keep_fetching = True
    cont_token = None
    search_params = dict(Bucket=bucket.name)

    while keep_fetching:
        keep_fetching = False
        if cont_token is None:
            search_params.update(dict(ContinuationToken=cont_token))

        resp = s3_handler.s3_client.list_objects_v2(Bucket=bucket.name)

        if CONTENTS in resp:
            for obj in resp[CONTENTS]:
                if not obj['Key'].endswith('/'):
                    file_count += 1
                    cumulative_size += obj[SIZE]
                    if (most_recent_mod is None) or (most_recent_mod < obj[LAST_MODIFIED]):
                        most_recent_mod = obj[LAST_MODIFIED]
        if IS_TRUNCATED in resp:
            keep_fetching = resp[IS_TRUNCATED]
        if keep_fetching:
            cont_token = resp[NEXT_CONTINUATION_TOKEN]

    return dict(
        name=bucket.name,
        created=bucket.creation_date,
        file_count=file_count,
        cumulative_size=cumulative_size,
        most_recent_mod=most_recent_mod
    )


if __name__ == '__main__':

    # Basic functionality
    # TODO add 'display' function to handle command line display of each
    # TODO what if network issue in middle of script run?
    # TODO make script with arg handling
    # TODO pass profile name as script arg
    # TODO pass size display format (kB, MB, etc) as script arg

    # Code Hygene
    # TODO what logging is necessary
    # TODO refactor pass at end to break up better for testing
    # TODO add tests
    # TODO make sure comments & docstrings are included where needed
    # TODO complete README

    # Value adds - standardization & expanded functionality
    # TODO _maybe_ validate functions for certain dict types? bucket_info, creds
    # TODO _maybe_ add support for using AWS cli profiles
    # TODO _maybe_ add skipContents to explore_bucket
    # TODO _maybe_ add functionality to handle logging of bucket_info dicts

    runtime_timestamp_start = datetime.now()
    access_handler = AccessHandler()
    bucket_info_collector = []
    for bucket in access_handler.s3_resource.buckets.all():
        bucket_info = explore_bucket(bucket, access_handler)
        print(bucket_info)
        bucket_info_collector.append(bucket_info)
    runtime_timestamp_completed = datetime.now()

    # all_info = pd.DataFrame(bucket_info_collector)
    # all_info['query_initiated'] = runtime_timestamp_start
    # all_info['query_completed'] = runtime_timestamp_completed
    # all_info['query_time_taken'] = runtime_timestamp_completed - runtime_timestamp_start
    # all_info.to_csv('all_info_{}'.format(runtime_timestamp_start))
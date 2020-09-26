import boto3
from typing import NamedTuple
import json
import logging
import pandas as pd
from datetime import datetime
import os

APP_HOME = os.environ['S3X_PATH']

CONTENTS = 'Contents'
KEY = 'Key'
SIZE = 'Size'
LAST_MODIFIED = 'LastModified'
IS_TRUNCATED = 'IsTruncated'
NEXT_CONTINUATION_TOKEN = 'NextContinuationToken'

DEFAULT_PROFILE_NAME = 'default'
DEFAULT_DATE_FORMAT = "%Y_%m_%d"

class AccessHandler():

    CREDENTIALS_PATH = 'data/.cred.json'
    AWS_PROFILES = 'aws_profiles'

    def __init__(
            self,
            profile_name,
            cred_path=CREDENTIALS_PATH
    ):
        self.cred_storage = os.path.join(APP_HOME, cred_path)
        creds = self.fetch_creds(profile_name, self.cred_storage)
        # self.session = self.initiate_s3(**creds)
        self._session = boto3.Session(**creds)
        self.s3_client = self._session.client('s3')
        self.s3_resource = self._session.resource('s3')

    @staticmethod
    def fetch_creds(
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


class BucketInfo:
    def __init__(
            self,
            name: str,
            created: datetime
    ):
        self.name = name
        self.created = created

        self.file_count = 0
        self.cumulative_size = 0
        self.most_recent_mod = None

    def add_file(self, size, last_modified):
        self.file_count += 1
        self.cumulative_size += size
        if (self.most_recent_mod is None) or \
                (self.most_recent_mod < last_modified):
            self.most_recent_mod = last_modified

    # def to_dict(self):
    #     return dict(
    #         name=self.name,
    #         created=self.created,
    #         file_count=self.file_count,
    #         cumulative_size=self.cumulative_size,
    #         most_recent_mod=self.most_recent_mod
    #     )


class ResultHandler:
    LOG_FILE_LOCATION = "data/result_logs"

    def __init__(self, date_format, sizeformat):
        self._initated = datetime.now()
        self._date_format = date_format
        self._sizeformat = sizeformat
        self._logfile = self._logfile_location()
        self._results = []
        pass

    def version_name(self):
        return self._initated.strftime(self._date_format)

    def update_results(self, bucket_info: BucketInfo):
        self._results.append(bucket_info)
        self._console_display(bucket_info)
        self._update_logfile()

    def _update_logfile(self):
        pd.DataFrame(self._results).to_csv(self._logfile)

    def _logfile_location(self):
        return os.path.join(APP_HOME, self.LOG_FILE_LOCATION, self.version_name(), '.csv')

    @staticmethod
    def _console_display(bucket_info: BucketInfo):
        print(bucket_info.__dict__)


def initiate_bucket_info(input_bucket):
    # TODO refactor to 'from_bucket' function in BucketInfo?
    return BucketInfo(
        name=input_bucket.name,
        created=input_bucket.creation_date
    )


def explore_bucket(target_bucket, s3_handler):
    logger = logging.getLogger(__name__)

    my_info = initiate_bucket_info(target_bucket)

    keep_fetching = True
    cont_token = None
    search_params = dict(Bucket=my_info.name)
    while keep_fetching:
        keep_fetching = False
        if cont_token is not None:
            search_params.update(dict(ContinuationToken=cont_token))

        resp = s3_handler.s3_client.list_objects_v2(**search_params)

        if CONTENTS in resp:
            for obj in resp[CONTENTS]:
                if not obj[KEY].endswith('/'):
                    my_info.add_file(obj[SIZE], obj[LAST_MODIFIED])
        if IS_TRUNCATED in resp:
            keep_fetching = resp[IS_TRUNCATED]
        if keep_fetching:
            cont_token = resp[NEXT_CONTINUATION_TOKEN]
    return my_info


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
    # TODO _maybe_ split out install config params to separate file

    # runtime_timestamp_start = datetime.now()
    access_handler = AccessHandler(profile_name=DEFAULT_PROFILE_NAME)
    result_handler = ResultHandler(date_format=DEFAULT_DATE_FORMAT, sizeformat=None)
    # bucket_info_collector = []
    for bucket in access_handler.s3_resource.buckets.all():
        result_handler.update_results(explore_bucket(bucket, access_handler))

        # result_handler.update_results(bucket_info)
        # print(bucket_info.to_dict())
        # bucket_info_collector.append(bucket_info)
    # runtime_timestamp_completed = datetime.now()

    # all_info = pd.DataFrame(bucket_info_collector)
    # all_info['query_initiated'] = runtime_timestamp_start
    # all_info['query_completed'] = runtime_timestamp_completed
    # all_info['query_time_taken'] = runtime_timestamp_completed - runtime_timestamp_start
    # all_info.to_csv('all_info_{}'.format(runtime_timestamp_start))
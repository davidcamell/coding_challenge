import boto3
from typing import NamedTuple
import json
import logging
import pandas as pd
from datetime import datetime
import os
from enum import Enum

APP_HOME = os.environ['S3X_PATH']

CONTENTS = 'Contents'
KEY = 'Key'
SIZE = 'Size'
LAST_MODIFIED = 'LastModified'
IS_TRUNCATED = 'IsTruncated'
NEXT_CONTINUATION_TOKEN = 'NextContinuationToken'

DEFAULT_PROFILE_NAME = 'default'
DEFAULT_DATE_FORMAT = "%Y_%m_%d"


class SIZE_FORMAT(Enum):
    BYTES = 1
    KB = 1024
    MB = KB**2
    GB = KB**3
    TB = KB**4

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



class ResultHandler:
    LOG_FILE_LOCATION = 'data/result_logs'
    LOG_TIMESTAMP_FORMAT = '%Y_%m%d_%H%M'

    def __init__(self, date_display_format, size_disaplay_format, profile_name):
        self.profile = profile_name
        self._initated = datetime.now()
        self._date_display_format = date_format
        self._size_disaplay_format = size_disaplay_format
        self._validate_location()
        self._results = []
        pass

    def version_name(self):
        return self._initated.strftime(self.LOG_TIMESTAMP_FORMAT)

    def update_results(self, bucket_info: BucketInfo):
        self._results.append(bucket_info)
        self._console_display(bucket_info)
        self._update_logfile()

    def _validate_location(self):
        subdir, filename = os.path.split(self._logfile_location())
        if not os.path.exists(subdir):
            os.makedirs(subdir)

    def _update_logfile(self):
        pd.DataFrame(self._results).to_csv(self._logfile_location())

    def _logfile_location(self):
        return os.path.join(APP_HOME, self.LOG_FILE_LOCATION, self._profile, '{}.csv'.format(self.version_name()))

    @staticmethod
    def display_size(file_size: int, size_format: SIZE_FORMAT):
        return '{:.1f} {}'.format(file_size/size_format.value, size_format.name)

    def _console_display(self, bucket_info: BucketInfo):
        print('Bucket "{}", created {}\n Contains {} files, most recently updated {}\n Total size: {}'.format(
            bucket_info.name,
            bucket_info.created.strftime(self._date_display_format)),
            bucket_info.file_count,
            bucket_info.most_recent_mod.strftime(self._date_display_format),
            self.display_size(bucket_info.cumulative_size, self._size_disaplay_format)
        )


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

    access_handler = AccessHandler(profile_name=DEFAULT_PROFILE_NAME)
    result_handler = ResultHandler(date_format=DEFAULT_DATE_FORMAT, sizeformat=SIZE_FORMAT.KB)
    for bucket in access_handler.s3_resource.buckets.all():
        result_handler.update_results(explore_bucket(bucket, access_handler))

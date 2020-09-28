import pandas as pd
from datetime import datetime
import os
from enum import Enum

APP_HOME = os.environ['S3X_PATH']


class SizeFormat(Enum):
    BYTES = 1
    KB = 1024
    MB = KB**2
    GB = KB**3
    TB = KB**4


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


def display_file_size(file_size: int, size_format: SizeFormat):
    return '{:.1f} {}'.format(file_size/size_format.value, size_format.name)


def display_last_mod(last_mod, date_display_format):
    if last_mod is None:
        return "n/a"
    elif isinstance(last_mod, datetime):
        return last_mod.strftime(date_display_format)
    else:
        return last_mod


class ResultHandler:
    LOG_FILE_LOCATION = 'data/result_logs'
    LOG_TIMESTAMP_FORMAT = '%Y_%m%d_%H%M'

    def __init__(self, date_display_format, size_display_format, profile_name):
        self._profile = profile_name
        self._initated = datetime.now()
        self._date_display_format = date_display_format
        self._size_disaplay_format = size_display_format
        self._validate_location()
        self._results = []
        pass

    def version_name(self):
        return self._initated.strftime(self.LOG_TIMESTAMP_FORMAT)

    def update_results(self, bucket_info: BucketInfo):
        self._results.append(bucket_info)
        print(self._console_display(bucket_info))
        self._update_logfile()

    def _validate_location(self):
        subdir, filename = os.path.split(self._logfile_location())
        if not os.path.exists(subdir):
            os.makedirs(subdir)

    def _update_logfile(self):
        res_dict = [x.__dict__ for x in self._results]
        pd.DataFrame(res_dict).set_index('name').to_csv(self._logfile_location())

    def _logfile_location(self):
        return os.path.join(APP_HOME, self.LOG_FILE_LOCATION, self._profile, '{}.csv'.format(self.version_name()))

    def _console_display(self, bucket_info: BucketInfo):
        return (
            '\nBucket "{}", created {}\n Contains {} files\n Most recently updated {}\n Total size: {}'.format(
                bucket_info.name,
                bucket_info.created.strftime(self._date_display_format),
                bucket_info.file_count,
                display_last_mod(bucket_info.most_recent_mod,
                                      self._date_display_format),
                display_file_size(bucket_info.cumulative_size,
                                  self._size_disaplay_format)
            )
        )


def initiate_bucket_info(input_bucket):
    return BucketInfo(
        name=input_bucket.name,
        created=input_bucket.creation_date
    )

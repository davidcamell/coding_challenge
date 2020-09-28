import pandas as pd
from datetime import datetime
import os
from enum import Enum

APP_HOME = os.environ['S3X_PATH']


class SizeFormat(Enum):
    """
    A concise way to store different file size display options.
    """
    BYTES = 1
    KB = 1024
    MB = KB**2
    GB = KB**3
    TB = KB**4


class BucketInfo:
    """
    Because we'll want to gather and read information about the bucket in different places,
    having a unified data structure that can be passed around seemed useful.
    """
    def __init__(
            self,
            name: str,
            created: datetime
    ):
        """
        Intiate the bucket information. In our use case,
        we already have name and date created.

        :param name: The name of the bucket.
        :type name: str
        :param created: When the bucket was created.
        :type created: datetime
        """
        self.name = name
        self.created = created

        # We will update as we find each file.
        self.file_count = 0
        self.cumulative_size = 0
        self.most_recent_mod = None

    def add_file(self, size:int , last_modified: datetime):
        """
        As the bucket is explored, we will use this object as a
        kind of virtual clipboard, updating running totals.

        :param size: File size of each file we find.
        :type size: int
        :param last_modified: When was the file last modified.
        :type last_modified: datetime
        """
        self.file_count += 1
        self.cumulative_size += size
        if (self.most_recent_mod is None) or \
                (self.most_recent_mod < last_modified):
            self.most_recent_mod = last_modified


def display_file_size(file_size: int, size_format: SizeFormat):
    """
    This will handle converting the raw size number into
    the right unit and display format.

    :param file_size: The raw numeric information.
    :type file_size: int
    :param size_format: An enum that ties together unit conversion values
    :type size_format: SizeFormat
    :return: A string that is human readable: "1.0 MB" for example
    :rtype: str
    """
    return '{:.1f} {}'.format(file_size/size_format.value, size_format.name)


def display_last_mod(last_mod: [None or datetime], date_display_format: str):
    """
    This will handle converting the raw datetime into
    the right display format.

    :param last_mod: When was a file / bucket last modified.
    :type last_mod: datetime or None
    :param date_display_format: Use python's formatting language:
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    :type date_display_format: str
    :return: String to display, for example "2020_09_25", "09/25/2020", or "25/09/2020"
    :rtype: str
    """
    if last_mod is None:
        return "n/a"
    elif isinstance(last_mod, datetime):
        return last_mod.strftime(date_display_format)
    else:
        raise ValueError("Expecting either datetime or None type input for 'last_mod' parameter.")


class ResultHandler:
    """
    An object to hold together display configuration and information
    as each bucket is explored. Main advantage of a collector like
    this (as opposed to just writing out info as we discover it)
    is a more organized way to create a log as everything is updated.
    """
    LOG_FILE_LOCATION = 'data/result_logs'
    LOG_TIMESTAMP_FORMAT = '%Y_%m%d_%H%M'

    def __init__(self, date_display_format, size_display_format, profile_name):
        """
        Establish how we will display results and information that
        will be used to structure the logging written out to the 'data' directory.

        :param date_display_format: Use python's formatting language:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        :type date_display_format: str
        :param size_display_format: Display in bytes, kilobytes, megabytes, etc.
        :type size_display_format: SizeFormat
        :param profile_name: When results are written out, this helps partition
        one set of credentials / data source from the next.
        :type profile_name: str
        """
        self._profile = profile_name
        self._initated = datetime.now()
        self._date_display_format = date_display_format
        self._size_disaplay_format = size_display_format
        self._validate_location()
        self._results = []
        pass

    def version_name(self):
        """
        :return: Cleans up raw datetime info to a consistent runtime string
        :rtype: str
        """
        return self._initated.strftime(self.LOG_TIMESTAMP_FORMAT)

    def update_results(self, bucket_info: BucketInfo):
        """
        As each bucket is completed, pass the results here to keep track of them.
        :param bucket_info: Completed bucket analysis.
        :type bucket_info: BucketInfo
        """
        self._results.append(bucket_info)
        print(self._console_display(bucket_info))
        self._update_logfile()

    def _validate_location(self):
        """
        Handles making sure a place for writing out files exists.
        """
        subdir, filename = os.path.split(self._logfile_location())
        if not os.path.exists(subdir):
            os.makedirs(subdir)

    def _update_logfile(self):
        """
        Writes a table as the results are updated. Could write out line by line,
        but this sacrifices a minor amount of processing and memory
        to keep code cleaner and less error prone.
        """
        res_dict = [x.__dict__ for x in self._results]
        pd.DataFrame(res_dict).set_index('name').to_csv(self._logfile_location())

    def _logfile_location(self):
        """
        A consistent way to point back to the logfile.

        :return: Filepath to dedicated log file.
        :rtype: str
        """
        return os.path.join(
            APP_HOME,
            self.LOG_FILE_LOCATION,
            self._profile, '{}.csv'.format(self.version_name())
        )

    def _console_display(self, bucket_info: BucketInfo):
        """
        Encapsulates a consistent method of printing out information. Handle
        string value here, but defer to calling function to either print out
        or assess in some other way (also makes it easier for automated testing).

        :param bucket_info: Completed tally of a bucket's contents.
        :type bucket_info: BucketInfo
        :return: A formatted string for display.
        :rtype: str
        """
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
    """
    Helper function for extracting preliminary information from a bucket.

    :param input_bucket: An S3 bucket object passed back from resource handler.
    :type input_bucket: S3 bucket
    :return: Data structure ready to start collecting file inforation
    :rtype: BucketInfo
    """
    return BucketInfo(
        name=input_bucket.name,
        created=input_bucket.creation_date
    )

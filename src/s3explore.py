import argparse
from access import AccessHandler, explore_bucket
from datetime import datetime
from results import ResultHandler, SizeFormat, initiate_bucket_info

DEFAULT_PROFILE_NAME = 'default'
DEFAULT_DATE_FORMAT = 'month_first'
DEFAULT_SIZE_FORMAT = 'mb'

if __name__ == '__main__':
    # TODO complete README

    # This dict sets certain date display options; the underlying
    # object, ResultHandler, can take any string written in python's
    # date formatting mini language,
    # (https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes),
    # but for out users, we want to keep this easy to use, so we narrow
    # down to some often used formats
    date_display_mapping = dict(
        month_first='%m/%d/%Y',
        year_first='%Y_%m_%d',
        day_first='%d/%m/%Y',
    )

    # This is an extra bit of clarity for th user regarding date formats;
    # It creates a list of today's dte in each of the formats above,
    # then resolves that to a string to include in the --help information
    date_format_example_list = [datetime.now().strftime(
        date_display_mapping[dtf]
    ) for dtf in date_display_mapping]
    date_format_example_list[-1] = 'or {}'.format(date_format_example_list[-1])
    date_format_example = ', '.join(date_format_example_list)

    # Define and manage the various possible arguments for this script
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-p', '--profile', type=str, default=DEFAULT_PROFILE_NAME,
                        help="Provide profile name (will use {} if not supplied).".format(
                            DEFAULT_PROFILE_NAME))
    parser.add_argument('-s', '--size_format', type=str, default=DEFAULT_SIZE_FORMAT,
                        choices=[x.name.lower() for x in SizeFormat],
                        help='Choose unit to display total bucket size.')
    parser.add_argument('-d', '--date_format', type=str, default=DEFAULT_DATE_FORMAT,
                        choices=list(date_display_mapping.keys()),
                        help='Choose unit to display last modified date for bucket files, for example {}'.format(
                            date_format_example
                        ))
    parser.add_argument('-a', '--use_aws_cli_creds', default=False, action='store_true',
                        help="Use AWS profiles instead of credentials stored by this app.")
    parser.add_argument('-t', '--show_time_modified', default=False, action='store_true',
                        help='Include the time of day for last modified file; for example "... 13:01:20".')
    parser.add_argument('-w', '--write_results_to_disk', default=False, action='store_true',
                        help='After displaying in command line; also write to a log file in "data" directory.')
    args = parser.parse_args()

    # Resolve actual date format codes, and append time code
    # if user has opted for that level of detail
    use_date_format = date_display_mapping[args.date_format]
    if args.show_time_modified:
        use_date_format = '{} %H:%M:%S'.format(use_date_format)

    # Initiate the main handler objects that will be our workers
    access_handler = AccessHandler(profile_name=args.profile,
                                   use_aws_cli_profiles=args.use_aws_cli_creds)
    result_handler = ResultHandler(date_display_format=use_date_format,
                                   size_display_format=SizeFormat[args.size_format.upper()],
                                   profile_name=args.profile,
                                   write_results_to_disk=args.write_results_to_disk)

    # Cycle through the buckets...
    for bucket in access_handler.s3_resource.buckets.all():
        # Grab the top level bucket info and fill in "top of form"
        # for the BucketInfo object...
        bucket_info = initiate_bucket_info(bucket)

        # Now send the BucketInfo object to get populated with
        # detailed information about the files within
        bucket_info = explore_bucket(bucket_info, access_handler.s3_client)

        # Once completed, hand off to ResultHandler for display and/or logging to disk
        result_handler.update_results(bucket_info)

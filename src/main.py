from access import AccessHandler, explore_bucket
from results import ResultHandler, SizeFormat, initiate_bucket_info
import argparse
from datetime import datetime

DEFAULT_PROFILE_NAME = 'default'
DEFAULT_DATE_FORMAT = 'month_first'
DEFAULT_SIZE_FORMAT = 'mb'

if __name__ == '__main__':

    # Basic functionality
    # TODO what if network issue in middle of script run?

    # Code Hygene
    # TODO what logging is necessary
    # TODO refactor pass at end to break up better for testing
    # TODO add MORE tests
    # TODO include mock & conftest in tests, including mocking up s3 connection
    # TODO make sure comments & docstrings are included where needed
    # TODO complete README

    # Value adds - standardization & expanded functionality
    # TODO _maybe_ validate functions for certain dict types? bucket_info, creds
    # TODO _maybe_ add skipContents to explore_bucket???
    # TODO _maybe_ split out install config params to separate file

    size_display_mapping = dict(
        b = ('byte', SizeFormat.BYTES),
        kb = ('kilobyte', SizeFormat.KB),
        mb = ('megabyte', SizeFormat.MB),
        gb = ('gigabyte', SizeFormat.GB),
        tb = ('terabyte', SizeFormat.TB),
    )

    date_display_mapping = dict(
        month_first = '%m/%d/%Y',
        year_first = '%Y_%m_%d',
        day_first = '%d/%m/%Y'
    )

    date_format_example_list = [datetime.now().strftime(date_display_mapping[dtf]) for dtf in date_display_mapping]
    date_format_example_list[-1] = 'or {}'.format(date_format_example_list[-1])
    date_format_example = ', '.join(date_format_example_list)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=str, default=DEFAULT_PROFILE_NAME,
                        help="Provide profile name (will use {} if not supplied).".format(DEFAULT_PROFILE_NAME))
    parser.add_argument('--use_aws_cli_creds', default=False, action='store_true',
                        help="Use AWS profiles instead of credentials stored by this app.")
    parser.add_argument('--size_format', type=str, default=DEFAULT_SIZE_FORMAT,
                        choices=list(size_display_mapping.keys()),
                        help='Choose unit to display total bucket size.')
    parser.add_argument('--date_format', type=str, default=DEFAULT_DATE_FORMAT,
                        choices=list(date_display_mapping.keys()),
                        help='Choose unit to display last modified date for bucket files, for example {}'.format(
                            date_format_example
                        ))
    args = parser.parse_args()

    descriptive_name, use_size_format = size_display_mapping[args.size_format]
    use_date_format = date_display_mapping[args.date_format]

    access_handler = AccessHandler(profile_name=args.profile,
                                   use_aws_cli_profiles=args.use_aws_cli_creds)
    result_handler = ResultHandler(date_display_format=use_date_format,
                                   size_display_format=use_size_format,
                                   profile_name=args.profile)
    for bucket in access_handler.s3_resource.buckets.all():
        bucket_info = initiate_bucket_info(bucket)
        result_handler.update_results(explore_bucket(bucket_info, access_handler.s3_client))

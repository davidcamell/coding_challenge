import pytest
from results import SizeFormat, display_file_size, display_last_mod
from datetime import datetime


@pytest.mark.parametrize("file_size, size_format, expected_output",
                         ((1024, SizeFormat.KB, '1.0 KB'),
                          (1024**2, SizeFormat.MB, '1.0 MB'),
                          (1024**3, SizeFormat.GB, '1.0 GB'),))
def test_display_file_size(file_size, size_format, expected_output):
    assert display_file_size(file_size, size_format) == expected_output


@pytest.mark.parametrize("last_mod, date_display_format, expected_output",
                         ((datetime(2020, 9, 25), '%Y_%m_%d', '2020_09_25'),
                          (datetime(2020, 9, 25), '%m/%d/%Y', '09/25/2020'),))
def test_display_last_mod(last_mod, date_display_format, expected_output):
    assert display_last_mod(last_mod, date_display_format) == expected_output


def test_bucket_info(mock_bucket_info,
                     bucket_name,
                     created_date):
    """
    Test that BucketInfo object is updating correctly as it receives results.
    :param mock_bucket_info: Starting BucketInfo, expected to be empty of results, default is to use pytest fixture.
    :param bucket_name: String name of bucket, expected to correspond to same in mock_bucket_info.
    :param created_date: Date of creation for bucket, expected to correspond to same in mock_bucket_info.
    """
    mock_bucket_info.add_file(100, datetime(2020, 1, 1))
    assert mock_bucket_info.name == bucket_name
    assert mock_bucket_info.created == created_date
    assert mock_bucket_info.file_count == 1
    assert mock_bucket_info.cumulative_size == 100
    assert mock_bucket_info.most_recent_mod == datetime(2020, 1, 1)

    mock_bucket_info.add_file(200, datetime(2019, 1, 1))
    assert mock_bucket_info.name == bucket_name
    assert mock_bucket_info.created == created_date
    assert mock_bucket_info.file_count == 2
    assert mock_bucket_info.cumulative_size == 300
    assert mock_bucket_info.most_recent_mod == datetime(2020, 1, 1)

    mock_bucket_info.add_file(300, datetime(2020, 1, 10))
    assert mock_bucket_info.name == bucket_name
    assert mock_bucket_info.created == created_date
    assert mock_bucket_info.file_count == 3
    assert mock_bucket_info.cumulative_size == 600
    assert mock_bucket_info.most_recent_mod == datetime(2020, 1, 10)


def test_result_handler(mock_bucket_info, result_handler):
    """

    :param mock_bucket_info: Starting BucketInfo, expected to be empty of results, default is to use pytest fixture.
    :param result_handler: ResultHandler to be tested, default is to just use pytest fixture from conftest.py.
    """
    mock_bucket_info.add_file(1024*1024, datetime(2020, 1, 1))
    display_out = result_handler._console_display(mock_bucket_info)

    # Look at multiline output line by line
    lines = display_out.split('\n')
    assert lines[1] == 'Bucket "BUCKET1", created 2020_09_25' # starting on item 1, because output starts with \n
    assert lines[2] == ' Contains 1 files'
    assert lines[3] == ' Most recently updated 2020_01_01'
    assert lines[4] == ' Total size: 1.0 MB'

    mock_bucket_info.add_file(2*1024*1024, datetime(2019, 1, 1))
    display_out = result_handler._console_display(mock_bucket_info)
    lines = display_out.split('\n')
    assert lines[1] == 'Bucket "BUCKET1", created 2020_09_25'
    assert lines[2] == ' Contains 2 files'
    assert lines[3] == ' Most recently updated 2020_01_01'
    assert lines[4] == ' Total size: 3.0 MB'

    mock_bucket_info.add_file(3*1024*1024, datetime(2020, 1, 10))
    display_out = result_handler._console_display(mock_bucket_info)
    lines = display_out.split('\n')
    assert lines[1] == 'Bucket "BUCKET1", created 2020_09_25'
    assert lines[2] == ' Contains 3 files'
    assert lines[3] == ' Most recently updated 2020_01_10'
    assert lines[4] == ' Total size: 6.0 MB'

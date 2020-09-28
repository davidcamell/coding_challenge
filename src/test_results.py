import pytest
from results import SizeFormat, BucketInfo, ResultHandler, display_size, display_last_mod
from datetime import datetime


@pytest.mark.parametrize("file_size, size_format, expected_output",
                         ((1024, SizeFormat.KB, '1.0 KB'),
                          (1024*1024, SizeFormat.MB, '1.0 MB'),
                          (1024**3, SizeFormat.GB, '1.0 GB'),))
def test_display_size(file_size, size_format, expected_output):
    assert display_size(file_size, size_format) == expected_output


@pytest.mark.parametrize("last_mod, date_display_format, expected_output",
                         ((datetime(2020, 9, 25), '%Y_%m_%d', '2020_09_25'),
                          (datetime(2020, 9, 25), '%m/%d/%Y', '09/25/2020'),))
def test_display_last_mod(last_mod, date_display_format, expected_output):
    assert display_last_mod(last_mod, date_display_format) == expected_output


def test_BucketInfo(bucket_name = 'fake_bucket', created_date = datetime(2020,9,25)):
    my_BI = BucketInfo(bucket_name, created_date)

    my_BI.add_file(100, datetime(2020, 1, 1))
    assert my_BI.name == bucket_name
    assert my_BI.created == created_date
    assert my_BI.file_count == 1
    assert my_BI.cumulative_size == 100
    assert my_BI.most_recent_mod == datetime(2020, 1, 1)

    my_BI.add_file(200, datetime(2019, 1, 1))
    assert my_BI.name == bucket_name
    assert my_BI.created == created_date
    assert my_BI.file_count == 2
    assert my_BI.cumulative_size == 300
    assert my_BI.most_recent_mod == datetime(2020, 1, 1)

    my_BI.add_file(300, datetime(2020, 1, 10))
    assert my_BI.name == bucket_name
    assert my_BI.created == created_date
    assert my_BI.file_count == 3
    assert my_BI.cumulative_size == 600
    assert my_BI.most_recent_mod == datetime(2020, 1, 10)
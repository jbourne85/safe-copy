from safe_copy.managed_directory import (FileStats, ManagedDirectory)
from collections import namedtuple
import pathlib
import pytest
import tempfile
from unittest import mock


FileStatsTest = namedtuple(
    "FileStatsTest",
    (
        'path',
        'checksum'
    )
)


def mock_file_stat(filename, checksum):
    return FileStatsTest(pathlib.Path(filename), checksum)


def test_file_stats():
    # Due to the checksum of the file being important, perform a more indepth test that creates a file of a known
    # content. Rather than mocking the hashing lib

    # Create a file larger than the block size (4k)
    data = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore\n",
        "magna aliqua.Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo\n",
        "consequat.Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla\n",
        "pariatur.Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est\n",
        "laborum."
    ]
    temp_filename = tempfile.NamedTemporaryFile().name

    # Create an approx 100MB file
    with open(temp_filename, 'w') as test_file:
        for i in range(250000):
            test_file.writelines(data)

    sut = FileStats(temp_filename)

    assert sut.path == temp_filename
    assert sut.checksum_method == 'md5'
    # Check the checksum is only calculated when it is required
    assert sut._checksum is None
    assert sut.checksum == '94a3d4bf17e438258768d3b708e606f1'
    assert sut._checksum == '94a3d4bf17e438258768d3b708e606f1'


@mock.patch('safe_copy.managed_directory.FileStats', autospec=True)
def test_managed_directory_constructor(mock_filestats):
    with mock.patch('os.walk') as mock_directory_contents:
        mock_directory_contents.return_value = [
            ('/root_dir/sub_dir1/', ('sub_dir2',), ('filename1',)),
            ('/root_dir/sub_dir1/sub_dir2', (), ('filename2', 'filename3')),
        ]
        sut = ManagedDirectory('/root_dir/sub_dir1/')

        assert len(sut.directory_stats) == 3
        mock_filestats.assert_has_calls([
            mock.call(pathlib.PosixPath('/root_dir/sub_dir1/filename1')),
            mock.call(pathlib.PosixPath('/root_dir/sub_dir1/sub_dir2/filename2')),
            mock.call(pathlib.PosixPath('/root_dir/sub_dir1/sub_dir2/filename3'))
        ])

@pytest.mark.parametrize(
    ('src_files', 'dst_files', 'failure_count'),
    [
        ([mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], [mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], 0),
        ([mock_file_stat('/tmp/filename1', 'x6qa'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], [mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], 1),
        ([mock_file_stat('/tmp/filename1', 'x6qa'), mock_file_stat('/tmp/filename2', 'fxqa'), mock_file_stat('/tmp/filename3', 'yu1k')], [mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], 2),
        ([mock_file_stat('/tmp/filename1', 'x6qa'), mock_file_stat('/tmp/filename2', 'fxqa'), mock_file_stat('/tmp/filename3', 'yu1a')], [mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], 3),
    ],
    ids=['0 Mismatch', '1 Mismatch', '2 Mismatch', '3 Mismatch']
)
def test_managed_directory_compare(src_files, dst_files, failure_count):
    with mock.patch.object(ManagedDirectory, '_get_directory_stats') as mock_directory_stats:
        mock_directory_stats.return_value = src_files
        source_mock = ManagedDirectory('/tmp/')

        mock_directory_stats.return_value = dst_files
        destination_mock = ManagedDirectory('/tmp/')

    with mock.patch.object(ManagedDirectory, 'relative_path') as mock_relative_path:
        mock_relative_path.side_effect = lambda file: file.path
        assert failure_count == destination_mock.compare(source_mock)


@pytest.mark.parametrize(
    ('directory_files', 'checksum_files'),
    [
        ([mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], [mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')]),
        ([mock_file_stat('/tmp/sum.txt',   'y5q0'), mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], [mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')]),
    ],
    ids=['All Files', 'Exclude sum.txt']
)
@mock.patch('builtins.open', new_callable=mock.mock_open)
def test_write_checksums(mock_checksum_file, directory_files, checksum_files):
    with mock.patch.object(ManagedDirectory, '_get_directory_stats') as mock_directory_stats:
        mock_directory_stats.return_value = directory_files
        sut = ManagedDirectory('/tmp/')

    with mock.patch.object(ManagedDirectory, 'relative_path') as mock_relative_path:
        mock_relative_path.side_effect = lambda file: file.path

        sut.save_checksums()

        assert len(mock_checksum_file.call_args_list) == 1
        assert mock_checksum_file.call_args_list[0] == mock.call(pathlib.PosixPath('/tmp/sum.txt'), 'w')

        handle = mock_checksum_file()
        write_calls = [mock.call(f"{file.checksum}\t{file.path}\n") for file in checksum_files]
        handle.write.assert_has_calls(write_calls)
        assert handle.write.call_count == len(write_calls)

@pytest.mark.parametrize(
    ('directory_files', 'checksum_files', 'failure_count'),
    [
        ([mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], [mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], 0),
        ([mock_file_stat('/tmp/filename1', 'x6qa'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], [mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], 1),
        ([mock_file_stat('/tmp/filename1', 'x6qa'), mock_file_stat('/tmp/filename2', 'fxqa'), mock_file_stat('/tmp/filename3', 'yu1k')], [mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], 2),
        ([mock_file_stat('/tmp/filename1', 'x6qa'), mock_file_stat('/tmp/filename2', 'fxqa'), mock_file_stat('/tmp/filename3', 'yu1a')], [mock_file_stat('/tmp/filename1', 'x6q0'), mock_file_stat('/tmp/filename2', 'fxqb'), mock_file_stat('/tmp/filename3', 'yu1k')], 3),
    ],
    ids=['0 Mismatch', '1 Mismatch', '2 Mismatch', '3 Mismatch']
)
@mock.patch('os.path.exists')
def test_validate_checksums(mock_dir_exists, directory_files, checksum_files, failure_count):
    with mock.patch.object(ManagedDirectory, '_get_directory_stats') as mock_directory_stats:
        mock_directory_stats.return_value = directory_files
        sut = ManagedDirectory('/tmp/')

    checksum_lines = [f"{file.checksum}\t{file.path}\n" for file in checksum_files]
    mock_checksum_file = mock.mock_open(read_data=''.join(checksum_lines))

    mock_dir_exists.return_code = True
    with mock.patch("builtins.open", mock_checksum_file):
        assert failure_count == sut.validate_checksums()
        assert len(mock_checksum_file.call_args_list) == 1
        assert mock_checksum_file.call_args_list[0] == mock.call(pathlib.PosixPath('/tmp/sum.txt'), 'r')

from safe_copy.managed_directories import FileStats
import tempfile


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

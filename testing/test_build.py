import unittest
import subprocess

class TestCSV2Tracks(unittest.TestCase):
    checksum = "3ec9833deef4a63b672df19aa4358b0e"

    def __init__(self, *args, **kwargs):
        super(TestCSV2Tracks, self).__init__(*args, **kwargs)

    def setUp(self):
        print("Running test: {}".format(self._testMethodName))

    def test_build(self):
        # create the destination directory; copy files
        subprocess.check_output('./4DGBWorkflow build 4DGB_Project', stderr=subprocess.STDOUT, shell=True)
        x = subprocess.check_output('checksumdir -a md5 4DGB_Project', stderr=subprocess.STDOUT, shell=True)
        result = x.decode("utf-8")
        result = result.strip()
        self.assertEqual(result, self.checksum )


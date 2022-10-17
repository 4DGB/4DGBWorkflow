import unittest
import subprocess
# import os
# import shutil
# import filecmp

class TestCSV2Tracks(unittest.TestCase):
    checksum = "b49d3a9c1b42d804be553b1537e23a63"

    def __init__(self, *args, **kwargs):
        super(TestCSV2Tracks, self).__init__(*args, **kwargs)

    def setUp(self):
        print("Running test: {}".format(self._testMethodName))

    def test_create(self):
        # create the destination directory; copy files
        subprocess.check_output('./4DGBWorkflow template', stderr=subprocess.STDOUT, shell=True)
        x = subprocess.check_output('checksumdir -a md5 4DGB_Project', stderr=subprocess.STDOUT, shell=True)
        result = x.decode("utf-8")
        result = result.strip()
        self.assertEqual(result, self.checksum )


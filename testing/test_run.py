import unittest
import subprocess
# import os
# import shutil
# import filecmp

class TestCSV2Tracks(unittest.TestCase):
    checksum = "35d51e6b1b4dd243e00f1c535cf3bf97"

    def __init__(self, *args, **kwargs):
        super(TestCSV2Tracks, self).__init__(*args, **kwargs)

    def setUp(self):
        print("Running test: {}".format(self._testMethodName))

    def test_create(self):
        # create the destination directory; copy files
        x = subprocess.check_output('./4DGBWorkflow run 4DGB_Project', stderr=subprocess.STDOUT, shell=True)
        result = x.decode("utf-8")
        result = result.strip()
        print("result = {}".format(result))
        x = subprocess.check_output('checksumdir -a md5 4DGB_Project', stderr=subprocess.STDOUT, shell=True)
        self.assertEqual(result, self.checksum )

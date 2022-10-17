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
        x = subprocess.check_output('./4DGBWorkflow template', stderr=subprocess.STDOUT, shell=True)
        print("result is {}".format(x))
        self.assertEqual(x, self.checksum )


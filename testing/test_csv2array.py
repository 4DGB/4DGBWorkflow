import unittest
import os
# import filecmp
# import shutil

class TestCSV2Arrays(unittest.TestCase):
    data_dir    = "testing/data/csv2arrays"
    gold_dir    = "testing/gold/csv2arrays"
    scratch_dir = "testing/scratch/csv2arrays"

    def __init__(self, *args, **kwargs):
        super(TestCSV2Arrays, self).__init__(*args, **kwargs)

    def setUp(self):
        print("Running test: {}".format(self._testMethodName))

    def test_create(self):
        """Test creating a database when the directory exists
        """
        os.system("./scripts/csv2arrays --workflow testing/data/csv2arrays/workflow.yaml --destination testing/scratch/csv2arrays")

        self.assertTrue(os.path.exists(TestCSV2Arrays.scratch_dir))

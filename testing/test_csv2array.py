import unittest
import os
import numpy
import shutil
# import filecmp

class TestCSV2Arrays(unittest.TestCase):
    data_dir    = "testing/data/csv2arrays"
    gold_dir    = "testing/gold/csv2arrays"
    scratch_dir = "testing/scratch/csv2arrays"
    dest_dir    = "arrays"

    def __init__(self, *args, **kwargs):
        super(TestCSV2Arrays, self).__init__(*args, **kwargs)

    def setUp(self):
        print("Running test: {}".format(self._testMethodName))

    def test_create(self):
        """Test creating array files from csv files 
        """
        # create the destination directory; copy files
        shutil.copytree(TestCSV2Arrays.data_dir, TestCSV2Arrays.scratch_dir)
        os.system("./scripts/csv2arrays --workflow {}/workflow.yaml --destination {}".format(
                        TestCSV2Arrays.scratch_dir, TestCSV2Arrays.dest_dir))

        # load and inspect data
        true_arr  = [0.6, 60.6, 0.6, 60.6, 0.6, 60.6, 0.6, 60.6, 0.6, 60.6]
        # a place we will find this data 
        data = numpy.load(os.path.join(TestCSV2Arrays.scratch_dir, TestCSV2Arrays.dest_dir, "trackname_03/track.npz"))
        numpy.testing.assert_array_equal(data["arr_1"], true_arr)
        # a place we will find this data 
        data = numpy.load(os.path.join(TestCSV2Arrays.scratch_dir, TestCSV2Arrays.dest_dir, "trackname_04/track.npz"))
        numpy.testing.assert_array_equal(data["arr_0"], true_arr)

        true_arr = [0.2, 20.2, 0.2, 20.2, 0.2, 20.2, 0.2, 20.2, 0.2, 20.2]
        # a place we will find this data 
        data = numpy.load(os.path.join(TestCSV2Arrays.scratch_dir, TestCSV2Arrays.dest_dir, "trackname_01/track.npz"))
        numpy.testing.assert_array_equal(data["arr_1"], true_arr)
        # a place we will find this data 
        data = numpy.load(os.path.join(TestCSV2Arrays.scratch_dir, TestCSV2Arrays.dest_dir, "trackname_02/track.npz"))
        numpy.testing.assert_array_equal(data["arr_0"], true_arr)

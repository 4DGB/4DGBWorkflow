import unittest
import os
import numpy
import shutil
# import filecmp

class TestCSV2Tracks(unittest.TestCase):
    data_dir    = "testing/data/csv2tracks"
    gold_dir    = "testing/gold/csv2tracks"
    scratch_dir = "testing/scratch/csv2tracks"
    dest_dir    = "arrays"

    def __init__(self, *args, **kwargs):
        super(TestCSV2Tracks, self).__init__(*args, **kwargs)

    def setUp(self):
        print("Running test: {}".format(self._testMethodName))

    def test_create(self):
        """Test creating array files from csv files 
        """
        # create the destination directory; copy files
        shutil.copytree(TestCSV2Tracks.data_dir, TestCSV2Tracks.scratch_dir)
        os.system("./build_stage/scripts/csv2tracks --workflow {}/workflow.yaml --destination {}".format(
                        TestCSV2Tracks.scratch_dir, TestCSV2Tracks.dest_dir))

        # load and inspect data
            # first two files
        true_arr_2 = [0.2, 20.2, 0.2, 20.2, 0.2, 20.2, 0.2, 20.2, 0.2, 20.2]
        # a place we will find this data 
        data = numpy.load(os.path.join(TestCSV2Tracks.scratch_dir, TestCSV2Tracks.dest_dir, "trackname_01/track.npz"))
        numpy.testing.assert_array_equal(data["arr_1"], true_arr_2)
        # a place we will find this data 
        data = numpy.load(os.path.join(TestCSV2Tracks.scratch_dir, TestCSV2Tracks.dest_dir, "trackname_02/track.npz"))
        numpy.testing.assert_array_equal(data["arr_0"], true_arr_2)

            # second two files 
        true_arr_6  = [0.6, 60.6, 0.6, 60.6, 0.6, 60.6, 0.6, 60.6, 0.6, 60.6]
        # a place we will find this data 
        data = numpy.load(os.path.join(TestCSV2Tracks.scratch_dir, TestCSV2Tracks.dest_dir, "trackname_03/track.npz"))
        numpy.testing.assert_array_equal(data["arr_1"], true_arr_6)
        # a place we will find this data 
        data = numpy.load(os.path.join(TestCSV2Tracks.scratch_dir, TestCSV2Tracks.dest_dir, "trackname_04/track.npz"))
        numpy.testing.assert_array_equal(data["arr_0"], true_arr_6)

            # test: use two different files
        # a place we will find this data 
        data = numpy.load(os.path.join(TestCSV2Tracks.scratch_dir, TestCSV2Tracks.dest_dir, "trackname_05/track.npz"))
        numpy.testing.assert_array_equal(data["arr_1"], true_arr_2)
        # a place we will find this data 
        data = numpy.load(os.path.join(TestCSV2Tracks.scratch_dir, TestCSV2Tracks.dest_dir, "trackname_06/track.npz"))
        numpy.testing.assert_array_equal(data["arr_1"], true_arr_6)

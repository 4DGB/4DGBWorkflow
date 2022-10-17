import unittest
import subprocess

class TestCSV2Tracks(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestCSV2Tracks, self).__init__(*args, **kwargs)

    def setUp(self):
        print("Running test: {}".format(self._testMethodName))

    def test_build(self):
        subprocess.check_output('./4DGBWorkflow template', stderr=subprocess.STDOUT, shell=True)
        subprocess.check_output('./4DGBWorkflow build 4DGB_Project', stderr=subprocess.STDOUT, shell=True)

        x = subprocess.check_output('wc -l 4DGB_Project/.build/lammps_0/structure.csv', stderr=subprocess.STDOUT, shell=True)
        result = x.decode("utf-8")
        result = result.strip()
        result = result.split()
        # did the computation create the expected number of points?
        self.assertEqual(int(result[0]), 255)

        x = subprocess.check_output('wc -l 4DGB_Project/.build/lammps_1/structure.csv', stderr=subprocess.STDOUT, shell=True)
        result = x.decode("utf-8")
        result = result.strip()
        result = result.split()
        # did the computation create the expected number of points?
        self.assertEqual(int(result[0]), 255)

        # check the project file
        tests = { 
                    ["fc81793037c4722d47e2475a3ed597eb", "4DGB_Project/.build/project.json"],
                    ["acc0e566818f2e5479446a0b8d3616ee", "4DGB_Project/.build/source/annotations.csv"],
                    ["acc0e566818f2e5479446a0b8d3616ee", "4DGB_Project/.build/tracks/H3K27ac/track.npz"]
                }

        for test in tests:
            x = subprocess.check_output('md5 -q {}'.filename(test[1]), stderr=subprocess.STDOUT, shell=True)
            result = x.decode("utf-8")
            result = result.strip()
            self.assertEqual(result, test[0])

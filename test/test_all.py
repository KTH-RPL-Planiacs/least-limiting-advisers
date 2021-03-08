import unittest
import os


if __name__ == '__main__':
    """
    This function will run all tests it can find in the directory
    """
    loader = unittest.TestLoader()
    start_dir = os.getcwd()
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)

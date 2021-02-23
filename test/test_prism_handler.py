import unittest
from prismhandler.prism_handler import PrismHandler
from py4j.protocol import Py4JNetworkError


class PrismHandlerTest(unittest.TestCase):

    def setUp(self):
        try:
            self.prism_handler = PrismHandler()
            print('Successfully connected to PRISM java gateway!')
        except Py4JNetworkError as err:
            print('Py4JNetworkError:', err)
            print('It is most likely that you forgot to start the PRISM java gateway. '
                  'Compile and launch prismhandler/PrismEntryPoint.java!')

    def test_check_bool_property(self):
        reach_prop = '<< p1 >> P>=1 [F \"a\"]'
        lasso_prop = '<<p1>>P>=1 [ G (<<p1>>P>=1 [ F \"a\"])]'
        coop_lasso_prop = '<<p1,p2>>P>=1 [ G (<<p1,p2>>P>=1 [ F \"a\"])]'
        self.prism_handler.load_model_file('../test/examples/test-game2.prism')

        result = self.prism_handler.check_bool_property(reach_prop)
        self.assertEqual(len(result), 5)
        self.assertTrue(result[0])
        self.assertFalse(result[4])

        result = self.prism_handler.check_bool_property(lasso_prop)
        self.assertEqual(len(result), 5)
        self.assertFalse(result[0])

        result = self.prism_handler.check_bool_property(coop_lasso_prop)
        self.assertEqual(len(result), 5)
        self.assertTrue(result[0])

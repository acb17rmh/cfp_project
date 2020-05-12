import unittest
import evaluate

class TestEvaluate(unittest.TestCase):

    def setUp(self):
        self.actual_name = "The 5th Annual Conference on Unit Testing"
        self.name_case_1 = "Conference on Unit Testing"
        self.name_case_2 = "2010 Workshop for Partial Matching Evaluation"
        self.name_case_3 = "The 5th Annual Conference on Unit Testing"

        self.locations_example = "Barcelona, New York, London"

    def tearDown(self):
        pass

    def test_name_evaluation(self):
        self.assertEqual(evaluate.eval_names([self.actual_name, self.name_case_1]), 4/7) #test case 1, Table 6.4
        self.assertEqual(evaluate.eval_names([self.actual_name, self.name_case_2]), 0) #test case 2, Table 6.4
        self.assertEqual(evaluate.eval_names([self.actual_name, self.name_case_3]), 1) #test case 3, Table 6.4

if __name__ == '__main__':
    unittest.main()

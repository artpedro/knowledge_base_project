import unittest

def run_all_tests():
    """
    Run Flask and database tests using unittest.
    """
    results = {}

    flask_test_suite = unittest.TestLoader().discover("tests/flask_tests")
    flask_result = unittest.TextTestRunner(verbosity=2).run(flask_test_suite)
    results["flask_tests"] = "Passed" if flask_result.wasSuccessful() else "Failed"

    db_test_suite = unittest.TestLoader().discover("tests/db_tests")
    db_result = unittest.TextTestRunner(verbosity=2).run(db_test_suite)
    results["database_tests"] = "Passed" if db_result.wasSuccessful() else "Failed"

    return results
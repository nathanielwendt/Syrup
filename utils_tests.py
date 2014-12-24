import os,sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from syrup_tests import SyrupTest
from syrup_utils import APIUtils

class TestContractConforms(SyrupTest):
    def setUp(self):
        super(TestContractConforms, self).setUp()
        self.expect_failed = 0
        self.expect_passed = 0

    def verify_true(self, val, message):
        if val:
            self.expect_passed += 1
        else:
            self.expect_failed += 1

    def expect_result(self, failed=None, passed=None):
        if passed is not None:
            self.assertEqual(passed, self.expect_passed)
        if failed is not None:
            self.assertEqual(failed, self.expect_failed)

    def test_required_valid_list_simple(self):
        contract = {
            "a": ["+"]
        }
        data = {
            "a": [10]
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=0, passed=2) #1 for each entry, 1 for the list itself

    def test_required_valid_list_multiple(self):
        contract = {
            "a": ["+"]
        }
        data = {
            "a": [10,20,30]
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=0, passed=4) #3 for each entry, 1 for the list itself

    def test_required_empty_list_optional_simple(self):
        contract = {
            "a": ["+", "*"]
        }
        data = {
            "a": []
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=0, passed=1)

    def test_required_empty_list_required_simple(self):
        contract = {
            "a": ["+", "+"]
        }
        data = {
            "a": []
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=1, passed=0)

    def test_required_partial_missing_list(self):
        contract = {
            "a": ["+"]
        }
        data = {
            "a": [10,None,30]
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=1, passed=3) #3 for each entry, 1 for the list itself

    def test_required_empty_list_optional_complex(self):
        contract = {
            "a": [{
                "x": "+"
            }, "*"]
        }
        data = {
            "a": []
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=0, passed=1)

    def test_required_empty_list_required_complex(self):
        contract = {
            "a": [{
                "x": "+"
            }, "+"]
        }
        data = {
            "a": []
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=1, passed=0)

    def test_required_none_value(self):
        contract = {
            "a": "+"
        }
        data = {
            "a": None
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=1, passed=0)

    def test_required_none_value_str(self):
        contract = {
            "a": "+"
        }
        data = {
            "a": 'None'
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=1, passed=0)

    def test_optional(self):
        contract = {
            "a": "*"
        }
        data = {
            "a": None
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=0, passed=0)

    def test_nested_perfect(self):
        contract = {
            "a": "+",
            "b": {
                "x": "+",
                "y": "+"
            }
        }
        data = {
            "a": 11,
            "b": {
                "x": 10,
                "y": 12
            }
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=0, passed=3)

    def test_nested_partial_fail(self):
        contract = {
            "a": "+",
            "b": {
                "x": "+",
                "y": "+"
            }
        }
        data = {
            "a": 11,
            "b": {
                #"x": 10,
                "y": 12
            }
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=1, passed=2)

    def test_nested_list_perfect(self):
        contract = {
            "a": "+",
            "b": [{
                "x": "+",
                "y": "+"
            }]
        }
        data = {
            "a": 11,
            "b": [
                {
                    "x": 10,
                    "y": 12
                },
                {
                    "x": 20,
                    "y": 22,
                },
                {
                    "x": 40,
                    "y": 42,
                }
            ]
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=0, passed=8) #7 for all the elements and 1 check for empty list

    def test_nested_list_partial_fails(self):
        contract = {
            "a": "+",
            "b": [{
                "x": "+",
                "y": "+"
            }]
        }

        data = {
            "a": 11,
            "b": [
                {
                    "x": 10,
                    "y": 12
                },
                {
                    #"x": 20,
                    "y": 22,
                },
                {
                    #"x": 40,
                    #"y": 42,
                }
            ]
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=3, passed=5)

    def test_exact_value_match(self):
        contract = {
            "a": "exactVal"
        }
        data = {
            "a": "exactVal"
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=0, passed=1)

    def test_exact_value_no_match(self):
        contract = {
            "a": "exactVal"
        }
        data = {
            "a": "NOTexactVal"
        }
        APIUtils.check_contract_conforms(contract, data, self.verify_true)
        self.expect_result(failed=1, passed=0)

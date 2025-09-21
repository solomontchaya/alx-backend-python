#!/usr/bin/env python3
"""
Unit tests for utils.py
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize  # <-- ensure memoize is imported


class TestAccessNestedMap(unittest.TestCase):
    """Tests for the access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns the expected value."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        """Test that KeyError is raised when path is invalid."""
        with self.assertRaises(KeyError) as e:
            access_nested_map(nested_map, path)
        self.assertEqual(str(e.exception), repr(path[-1]))


class TestGetJson(unittest.TestCase):
    """Tests for the get_json function."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """Test that get_json returns the expected payload without real HTTP calls."""
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        with patch("utils.requests.get", return_value=mock_response) as mock_get:
            result = get_json(test_url)
            mock_get.assert_called_once_with(test_url)  # called exactly once with URL
            self.assertEqual(result, test_payload)      # returned payload is correct


class TestMemoize(unittest.TestCase):
    """Tests for the memoize decorator."""

    def test_memoize(self):
        """Test that memoize caches the result of a method."""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        test_obj = TestClass()

        # Patch a_method so we can track how many times it is called
        with patch.object(TestClass, "a_method", return_value=42) as mock_method:
            first_call = test_obj.a_property
            second_call = test_obj.a_property

            # Both calls return the same cached value
            self.assertEqual(first_call, 42)
            self.assertEqual(second_call, 42)

            # a_method should have been called only once because of memoization
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()

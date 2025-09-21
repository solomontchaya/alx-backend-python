#!/usr/bin/env python3
"""Integration tests for GithubOrgClient.public_repos
"""
import unittest
from unittest.mock import patch
from parameterized import parameterized_class

from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos
    (only external requests are mocked)."""

    @classmethod
    def setUpClass(cls):
        """Set up a patcher for requests.get before any tests run."""
        # Patch the external requests.get call
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        # Define side_effect to return different payloads based on the URL
        def side_effect(url):
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                return MockResponse(cls.org_payload)
            if url == cls.org_payload["repos_url"]:
                return MockResponse(cls.repos_payload)
            return MockResponse({})

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher after all tests."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test for public_repos without license filter."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration test for public_repos filtering by 'apache-2.0' license."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


# Helper class to simulate requests.get().json()
class MockResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

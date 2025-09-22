#!/usr/bin/env python3
"""Unit and integration tests for GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from typing import Any, Dict, List

from client import GithubOrgClient
from fixtures import (
    org_payload,
    repos_payload,
    expected_repos,
    apache2_repos,
)


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for the GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json: Any) -> None:
        """
        Test that the .org property returns the correct payload
        and calls get_json exactly once.
        """
        mock_get_json.return_value = {"org": org_name}
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, {"org": org_name})
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self) -> None:
        """
        Unit-test the _public_repos_url property of GithubOrgClient.
        """
        test_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}

        with patch(
            "client.GithubOrgClient.org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, test_payload["repos_url"])
            mock_org.assert_called_once()

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: Any) -> None:
        """
        Unit-test the public_repos method of GithubOrgClient.
        """
        mock_get_json.return_value = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
        ]

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "https://api.github.com/orgs/google/repos"
            client = GithubOrgClient("google")
            self.assertEqual(client.public_repos(), ["repo1", "repo2"])
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/google/repos"
            )

    def test_has_license(self) -> None:
        """
        Unit-test the has_license method of GithubOrgClient.
        """
        client = GithubOrgClient("google")
        repo_apache = {"license": {"key": "apache-2.0"}}
        repo_mit = {"license": {"key": "mit"}}

        self.assertTrue(client.has_license(repo_apache, "apache-2.0"))
        self.assertFalse(client.has_license(repo_mit, "apache-2.0"))


class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos method."""

    @classmethod
    def setUpClass(cls) -> None:
        """Patch requests.get to return fixture payloads for integration tests."""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        def side_effect(url: str) -> Any:
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                return MockResponse(org_payload)
            if url == org_payload["repos_url"]:
                return MockResponse(repos_payload)
            return MockResponse({})

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop patching requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Integration test: public_repos without license filter."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), expected_repos)

    def test_public_repos_with_license(self) -> None:
        """Integration test: public_repos filtered by apache-2.0 license."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos("apache-2.0"), apache2_repos)


class MockResponse:
    """Simple mock class for requests.get().json() calls."""

    def __init__(self, payload: Any) -> None:
        """Initialize the mock with a given payload."""
        self._payload = payload

    def json(self) -> Any:
        """Return the JSON payload."""
        return self._payload

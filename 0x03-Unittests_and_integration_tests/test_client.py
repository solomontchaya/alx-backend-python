#!/usr/bin/env python3
"""Integration & unit tests for GithubOrgClient"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized

from client import GithubOrgClient
from fixtures import (
    org_payload,
    repos_payload,
    expected_repos,
    apache2_repos,
)


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """
        Test that .org returns correct payload
        and calls get_json once
        """
        mock_get_json.return_value = {"org": org_name}
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, {"org": org_name})
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Unit-test GithubOrgClient._public_repos_url"""
        test_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("google")
            self.assertEqual(
                client._public_repos_url,
                test_payload["repos_url"]
            )
            mock_org.assert_called_once()

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Unit-test GithubOrgClient.public_repos"""
        mock_get_json.return_value = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
        ]
        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = (
                "https://api.github.com/orgs/google/repos"
            )
            client = GithubOrgClient("google")
            self.assertEqual(client.public_repos(), ["repo1", "repo2"])
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/google/repos"
            )

    def test_has_license(self):
        """Unit-test GithubOrgClient.has_license"""
        client = GithubOrgClient("google")
        repo_apache = {"license": {"key": "apache-2.0"}}
        repo_mit = {"license": {"key": "mit"}}

        self.assertTrue(client.has_license(repo_apache, "apache-2.0"))
        self.assertFalse(client.has_license(repo_mit, "apache-2.0"))


class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get to return fixture payloads"""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                return MockResponse(org_payload)
            if url == org_payload["repos_url"]:
                return MockResponse(repos_payload)
            return MockResponse({})
        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration: no license filter"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), expected_repos)

    def test_public_repos_with_license(self):
        """Integration: filter by apache-2.0"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos("apache-2.0"),
            apache2_repos
        )


class MockResponse:
    """Simple mock for requests.get().json()"""
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

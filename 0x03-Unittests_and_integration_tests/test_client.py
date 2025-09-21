#!/usr/bin/env python3
"""
Unit tests for client module
"""
import unittest
from unittest.mock import (
    patch, Mock, PropertyMock
)
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test GithubOrgClient.org returns correct value"""
        test_payload = {"org_data": "test_data"}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        result = client.org

        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url returns expected URL"""
        test_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }

        with patch(
            'client.GithubOrgClient.org',
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("testorg")
            result = client._public_repos_url

            self.assertEqual(result, test_payload["repos_url"])
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos returns expected repos"""
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]

        with patch(
            'client.GithubOrgClient._public_repos_url',
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = (
                "https://api.github.com/orgs/testorg/repos"
            )
            mock_get_json.return_value = repos_payload

            client = GithubOrgClient("testorg")
            result = client.public_repos()
            expected_repos = ["repo1", "repo2", "repo3"]

            self.assertEqual(result, expected_repos)
            mock_url.assert_called_once()
            expected_call = (
                "https://api.github.com/orgs/testorg/repos"
            )
            mock_get_json.assert_called_once_with(expected_call)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """Test has_license returns expected result"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


@parameterized_class([
    {
        'org_payload': TEST_PAYLOAD[0][0],
        'repos_payload': TEST_PAYLOAD[0][1],
        'expected_repos': TEST_PAYLOAD[0][2],
        'apache2_repos': TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Set up class method to mock requests.get"""
        cls.get_patcher = patch('client.requests.get')
        cls.mock_get = cls.get_patcher.start()
        cls.addClassCleanup(cls.get_patcher.stop)

        def side_effect(url):
            mock_response = Mock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}
            return mock_response

        cls.mock_get.side_effect = side_effect

    def test_public_repos_integration(self):
        """Integration test for public_repos method"""
        client = GithubOrgClient("google")
        result = client.public_repos()

        self.assertEqual(result, self.expected_repos)
        self.assertEqual(self.mock_get.call_count, 2)

        expected_urls = [
            "https://api.github.com/orgs/google",
            "https://api.github.com/orgs/google/repos",
        ]
        actual_urls = [call_args[0][0] for call_args in self.mock_get.call_args_list]

        for expected_url in expected_urls:
            self.assertIn(expected_url, actual_urls)

    def test_public_repos_with_license(self):
        """Integration test for public_repos with license filter"""
        client = GithubOrgClient("google")
        result = client.public_repos(license="apache-2.0")

        self.assertEqual(result, self.apache2_repos)
        self.assertEqual(self.mock_get.call_count, 2)

        expected_urls = [
            "https://api.github.com/orgs/google",
            "https://api.github.com/orgs/google/repos",
        ]
        actual_urls = [call_args[0][0] for call_args in self.mock_get.call_args_list]

        for expected_url in expected_urls:
            self.assertIn(expected_url, actual_urls)


if __name__ == '__main__':
    unittest.main()

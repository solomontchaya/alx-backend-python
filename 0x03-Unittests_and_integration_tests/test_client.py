#!/usr/bin/env python3
"""
Unit tests for client module
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """
    Test class for GithubOrgClient
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """
        Test that GithubOrgClient.org returns the correct value
        and makes the correct API call
        """
        # Create test payload
        test_payload = {"org_data": "test_data"}
        
        # Configure the mock to return test payload
        mock_get_json.return_value = test_payload
        
        # Create client instance
        client = GithubOrgClient(org_name)
        
        # Call the org property
        result = client.org
        
        # Assert that get_json was called once with the correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        
        # Assert that the result is equal to the test payload
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self):
        """
        Test that GithubOrgClient._public_repos_url returns the expected URL
        """
        # Test payload with known repos_url
        test_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }
        
        # Use patch as context manager to mock the org property
        with patch('client.GithubOrgClient.org', new_callable=PropertyMock) as mock_org:
            # Configure the mock to return our test payload
            mock_org.return_value = test_payload
            
            # Create client instance
            client = GithubOrgClient("testorg")
            
            # Call the _public_repos_url property
            result = client._public_repos_url
            
            # Assert that the result is the expected repos_url from the payload
            self.assertEqual(result, test_payload["repos_url"])
            
            # Verify that the org property was accessed
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Test that GithubOrgClient.public_repos returns the expected list of repos
        """
        # Mock payload for get_json (repos data)
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None}
        ]
        
        # Mock the _public_repos_url property
        with patch('client.GithubOrgClient._public_repos_url', 
                  new_callable=PropertyMock) as mock_public_repos_url:
            
            # Configure the mocks
            mock_public_repos_url.return_value = "https://api.github.com/orgs/testorg/repos"
            mock_get_json.return_value = repos_payload
            
            # Create client instance
            client = GithubOrgClient("testorg")
            
            # Call public_repos method
            result = client.public_repos()
            
            # Expected result: list of repo names
            expected_repos = ["repo1", "repo2", "repo3"]
            
            # Assert that the result matches expected repos
            self.assertEqual(result, expected_repos)
            
            # Verify that _public_repos_url was accessed
            mock_public_repos_url.assert_called_once()
            
            # Verify that get_json was called once with the correct URL
            mock_get_json.assert_called_once_with("https://api.github.com/orgs/testorg/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """
        Test that GithubOrgClient.has_license returns the expected result
        """
        # Call the static method
        result = GithubOrgClient.has_license(repo, license_key)
        
        # Assert that the result matches expected result
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
    """
    Integration test class for GithubOrgClient
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up class method to mock requests.get
        """
        # Create a patcher for requests.get
        cls.get_patcher = patch('client.requests.get')
        
        # Start the patcher and get the mock
        cls.mock_get = cls.get_patcher.start()
        
        # Define side_effect function to return different payloads based on URL
        def side_effect(url):
            mock_response = Mock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}
            return mock_response
        
        # Configure the mock with side_effect
        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """
        Tear down class method to stop the patcher
        """
        cls.get_patcher.stop()

    def test_public_repos_integration(self):
        """
        Integration test for public_repos method
        """
        # Create client instance
        client = GithubOrgClient("google")
        
        # Call public_repos method
        result = client.public_repos()
        
        # Assert that the result matches expected repos
        self.assertEqual(result, self.expected_repos)
        
        # Verify that requests.get was called twice (for org and repos)
        self.assertEqual(self.mock_get.call_count, 2)
        
        # Verify the specific URLs that were called
        calls = [call[0][0] for call in self.mock_get.call_args_list]
        self.assertIn("https://api.github.com/orgs/google", calls)
        self.assertIn("https://api.github.com/orgs/google/repos", calls)


if __name__ == '__main__':
    unittest.main()
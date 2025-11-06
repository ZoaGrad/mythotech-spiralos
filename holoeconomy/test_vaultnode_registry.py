"""
Tests for the VaultNode Registry CLI.
"""

import unittest
import io
from unittest.mock import MagicMock, patch
from holoeconomy import vaultnode_registry

class TestVaultNodeRegistry(unittest.TestCase):
    """Test cases for the VaultNode Registry CLI."""

    def test_list_vaultnodes(self):
        """Test the list_vaultnodes function."""
        # Arrange
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [{'id': '123', 'node_type': 'test'}]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_response

        # Act
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            vaultnode_registry.list_vaultnodes(mock_client)

        # Assert
        output = mock_stdout.getvalue()
        self.assertIn("Listing all VaultNodes...", output)
        self.assertIn("{'id': '123', 'node_type': 'test'}", output)

    def test_get_vaultnode(self):
        """Test the get_vaultnode function."""
        # Arrange
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [{'id': '123', 'node_type': 'test'}]
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        # Act
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            vaultnode_registry.get_vaultnode(mock_client, '123')

        # Assert
        output = mock_stdout.getvalue()
        self.assertIn("Getting VaultNode with ID: 123...", output)
        self.assertIn("{'id': '123', 'node_type': 'test'}", output)

    def test_get_vaultnode_not_found(self):
        """Test the get_vaultnode function when the node is not found."""
        # Arrange
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = []
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        # Act
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            vaultnode_registry.get_vaultnode(mock_client, '456')

        # Assert
        output = mock_stdout.getvalue()
        self.assertIn("VaultNode with ID 456 not found.", output)

    def test_create_vaultnode(self):
        """Test the create_vaultnode function."""
        # Arrange
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [{'id': '123', 'node_type': 'test_ref', 'reference_id': 'ref123'}]
        mock_response.error = None
        mock_client.rpc.return_value.execute.return_value = mock_response

        # Act
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            vaultnode_registry.create_vaultnode(mock_client, 'ref123', 'test_ref')

        # Assert
        output = mock_stdout.getvalue()
        self.assertIn("Creating a new VaultNode...", output)
        self.assertIn("Successfully created VaultNode:", output)
        self.assertIn("{'id': '123', 'node_type': 'test_ref', 'reference_id': 'ref123'}", output)

    def test_create_vaultnode_failed(self):
        """Test the create_vaultnode function when it fails."""
        # Arrange
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = None
        mock_response.error = MagicMock()
        mock_response.error.message = "An error occurred"
        mock_client.rpc.return_value.execute.return_value = mock_response

        # Act
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            vaultnode_registry.create_vaultnode(mock_client, 'ref123', 'test_ref')

        # Assert
        output = mock_stdout.getvalue()
        self.assertIn("Failed to create VaultNode.", output)
        self.assertIn("Error: An error occurred", output)


if __name__ == '__main__':
    unittest.main()

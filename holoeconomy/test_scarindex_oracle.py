"""
Tests for the ScarIndex Oracle FastAPI Service.
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from holoeconomy.scarindex_oracle import app, compute_scarindex_from_new_event
from datetime import datetime, timezone
import uuid

class TestScarIndexOracle(unittest.TestCase):
    """Test cases for the ScarIndex Oracle FastAPI Service."""

    def setUp(self):
        """Set up the test client for each test."""
        self.client = TestClient(app)

    def test_health_check(self):
        """Test the /health endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "OK"})

    @patch('holoeconomy.scarindex_oracle.supabase')
    def test_get_latest_scarindex_success(self, mock_supabase):
        """Test the /scarindex endpoint successfully returns the latest index."""
        # Arrange
        timestamp_obj = datetime.now(timezone.utc)
        # FastAPI/Pydantic serializes datetimes with 'Z' instead of '+00:00'
        timestamp_str_for_mock = timestamp_obj.isoformat()
        expected_timestamp_str = timestamp_obj.isoformat().replace('+00:00', 'Z')

        mock_data = [{'scarindex': 0.75, 'created_at': timestamp_str_for_mock}]

        mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_data

        # Act
        response = self.client.get("/scarindex")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"scarindex": 0.75, "timestamp": expected_timestamp_str})

    @patch('holoeconomy.scarindex_oracle.supabase')
    def test_get_latest_scarindex_not_found(self, mock_supabase):
        """Test the /scarindex endpoint when no data is found."""
        # Arrange
        mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = []

        # Act
        response = self.client.get("/scarindex")

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "No ScarIndex calculation found."})

    @patch('holoeconomy.scarindex_oracle.compute_scarindex_from_new_event')
    def test_trigger_computation_success(self, mock_compute):
        """Test the /compute endpoint successfully triggers a computation."""
        # Arrange
        calc_id = uuid.uuid4()
        event_id = uuid.uuid4()
        mock_compute.return_value = {
            "message": "Success",
            "new_scarindex": 0.8,
            "calculation_id": calc_id,
            "ache_event_id": event_id
        }

        # Act
        response = self.client.post("/compute")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "message": "Success",
            "new_scarindex": 0.8,
            "calculation_id": str(calc_id),
            "ache_event_id": str(event_id)
        })

    @patch('holoeconomy.scarindex_oracle.compute_scarindex_from_new_event')
    def test_trigger_computation_failure(self, mock_compute):
        """Test the /compute endpoint handles computation failures."""
        # Arrange
        mock_compute.side_effect = RuntimeError("RPC call failed")

        # Act
        response = self.client.post("/compute")

        # Assert
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "RPC call failed"})

    @patch('holoeconomy.scarindex_oracle.supabase')
    def test_compute_scarindex_logic_success(self, mock_supabase):
        """Test the core compute_scarindex_from_new_event function's logic."""
        # Arrange
        event_id = uuid.uuid4()
        calc_id = uuid.uuid4()

        # Mock the insert into 'ache_events'
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{'id': str(event_id)}]

        # Mock the rpc call to 'coherence_calculation'
        mock_rpc_response_data = {
            'id': str(calc_id),
            'scarindex': 0.82,
            'ache_event_id': str(event_id)
        }
        mock_supabase.rpc.return_value.execute.return_value.data = mock_rpc_response_data

        # Act
        result = compute_scarindex_from_new_event()

        # Assert
        self.assertEqual(result['new_scarindex'], 0.82)
        self.assertEqual(result['calculation_id'], str(calc_id))
        self.assertEqual(result['ache_event_id'], str(event_id))

        # Verify calls
        mock_supabase.table.assert_called_with('ache_events')
        # The code passes a string UUID to the RPC call
        mock_supabase.rpc.assert_called_with('coherence_calculation', {'event_id': str(event_id)})

    @patch('holoeconomy.scarindex_oracle.supabase')
    def test_compute_scarindex_logic_ache_failure(self, mock_supabase):
        """Test the compute logic when creating an ache event fails."""
        # Arrange
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = []

        # Act & Assert
        with self.assertRaisesRegex(RuntimeError, "Failed to create ache event for computation."):
            compute_scarindex_from_new_event()

    @patch('holoeconomy.scarindex_oracle.supabase')
    def test_compute_scarindex_logic_rpc_failure(self, mock_supabase):
        """Test the compute logic when the RPC call fails."""
        # Arrange
        event_id = uuid.uuid4()
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{'id': str(event_id)}]
        mock_supabase.rpc.return_value.execute.return_value.data = None # Simulate RPC failure

        # Act & Assert
        with self.assertRaisesRegex(RuntimeError, f"RPC call to coherence_calculation failed for event_id: {event_id}"):
            compute_scarindex_from_new_event()

if __name__ == '__main__':
    unittest.main()

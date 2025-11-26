# tests/test_guardian_anomaly.py

import unittest
import os
from spiral_guardian import AnomalyDetector

class TestGuardianAnomaly(unittest.TestCase):

    def setUp(self):
        # Ensure environment variables are set for testing
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("WARNING: python-dotenv not installed. Trying manual parse.")
            try:
                with open(".env", "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            os.environ[key] = value
            except Exception as e:
                print(f"WARNING: Could not load .env file: {e}")

        # Fallback: If SERVICE_ROLE_KEY is missing, try using SUPABASE_KEY (might be the same or have permissions)
        if not os.getenv("SUPABASE_SERVICE_ROLE_KEY") and os.getenv("SUPABASE_KEY"):
            print("WARNING: SUPABASE_SERVICE_ROLE_KEY not found. Defaulting to SUPABASE_KEY.")
            os.environ["SUPABASE_SERVICE_ROLE_KEY"] = os.getenv("SUPABASE_KEY")

        if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
            print("WARNING: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set. Test may fail.")

    def test_anomaly_insertion(self):
        detector = AnomalyDetector()

        # Use a valid bridge_id from the database
        # ID: f8f41ffa-6c2b-4a2a-a3be-32f0236668f4 (guardian-core)
        valid_bridge_id = "f8f41ffa-6c2b-4a2a-a3be-32f0236668f4"

        # Simulated anomaly
        anomaly = {
            "bridge_id": valid_bridge_id,
            "anomaly_type": "TEST_ANOMALY",
            "severity": "LOW",
            "details": {"message": "Test anomaly from unit test."},
        }

        # Insert
        print(f"Reporting anomaly for bridge: {valid_bridge_id}")
        result = detector.report_anomaly(**anomaly)
        
        print(f"Insertion result: {result}")

        # Verify it inserted a row
        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0]['bridge_id'], valid_bridge_id)
        self.assertEqual(result[0]['anomaly_type'], "TEST_ANOMALY")


if __name__ == "__main__":
    unittest.main()

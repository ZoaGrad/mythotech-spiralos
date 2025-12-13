#!/usr/bin/env python3
"""
Sprint 1: Data Ingestion Engine for Antifragile SRE Platform MVP
Fetches historical metric data from Datadog API and stores it in Supabase (PostgreSQL).
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()


class DatadogMetricsFetcher:
    """Handles fetching metrics from Datadog API."""
    
    def __init__(self, api_key: str, app_key: str, site: Optional[str] = None):
        """
        Initialize Datadog API client.
        
        Args:
            api_key: Datadog API key
            app_key: Datadog application key
            site: Datadog site (e.g., 'us5.datadoghq.com', 'datadoghq.eu')
        """
        configuration = Configuration()
        configuration.api_key["apiKeyAuth"] = api_key
        configuration.api_key["appKeyAuth"] = app_key
        
        # Set custom Datadog site if provided
        if site:
            configuration.server_variables["site"] = site
        
        self.api_client = ApiClient(configuration)
        self.metrics_api = MetricsApi(self.api_client)
    
    def fetch_metric(
        self, 
        metric_name: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch metric data from Datadog for the specified time range.
        
        Args:
            metric_name: Name of the metric to fetch (e.g., 'system.cpu.idle')
            start_time: Start of the time range
            end_time: End of the time range
            
        Returns:
            List of metric data points with host, value, and timestamp
        """
        query = f"avg:{metric_name}{{*}} by {{host}}"
        
        try:
            response = self.metrics_api.query_metrics(
                _from=int(start_time.timestamp()),
                to=int(end_time.timestamp()),
                query=query
            )
            
            metrics_data = []
            
            if response.series:
                for series in response.series:
                    # Extract host from scope (e.g., "host:my-server")
                    host = self._extract_host_from_scope(series.scope)
                    
                    # Process each data point
                    if series.pointlist:
                        for point in series.pointlist:
                            timestamp_ms, value = point
                            if value is not None:
                                metrics_data.append({
                                    "host": host,
                                    "metric_name": metric_name,
                                    "value": float(value),
                                    "timestamp": datetime.fromtimestamp(timestamp_ms / 1000).isoformat()
                                })
            
            return metrics_data
        
        except Exception as e:
            print(f"Error fetching metric {metric_name}: {e}", file=sys.stderr)
            return []
    
    @staticmethod
    def _extract_host_from_scope(scope: str) -> str:
        """
        Extract hostname from Datadog scope string.
        
        Args:
            scope: Scope string from Datadog (e.g., "host:my-server")
            
        Returns:
            Hostname or the original scope if parsing fails
        """
        if scope and "host:" in scope:
            parts = scope.split("host:")
            if len(parts) > 1:
                # Handle cases like "host:server1,env:prod"
                host_part = parts[1].split(",")[0]
                return host_part.strip()
        return scope or "unknown"


class SupabaseMetricsStore:
    """Handles storing metrics in Supabase database."""
    
    def __init__(self, url: str, key: str):
        """
        Initialize Supabase client.
        
        Args:
            url: Supabase project URL
            key: Supabase API key (service role or anon key with appropriate permissions)
        """
        self.client: Client = create_client(url, key)
    
    def insert_metrics(self, metrics: List[Dict[str, Any]]) -> bool:
        """
        Insert metric data into Supabase metrics table.
        
        Args:
            metrics: List of metric dictionaries with host, metric_name, value, timestamp
            
        Returns:
            True if insertion was successful, False otherwise
        """
        if not metrics:
            print("No metrics to insert.")
            return True
        
        try:
            # Insert data into the metrics table
            response = self.client.table("metrics").insert(metrics).execute()
            
            print(f"Successfully inserted {len(metrics)} metric data points.")
            return True
        
        except Exception as e:
            print(f"Error inserting metrics into Supabase: {e}", file=sys.stderr)
            return False


def main() -> int:
    """
    Main execution function for the data ingestion pipeline.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Load configuration from environment variables
    datadog_api_key = os.getenv("DATADOG_API_KEY")
    datadog_app_key = os.getenv("DATADOG_APP_KEY")
    datadog_site = os.getenv("DATADOG_SITE")  # Optional: custom Datadog site
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    # Validate required environment variables
    if not all([datadog_api_key, datadog_app_key, supabase_url, supabase_key]):
        print("Error: Missing required environment variables.", file=sys.stderr)
        print("Required: DATADOG_API_KEY, DATADOG_APP_KEY, SUPABASE_URL, SUPABASE_KEY", file=sys.stderr)
        return 1
    
    # Define metrics to fetch
    metrics_to_fetch = [
        "system.cpu.idle",
        "system.load.1"
    ]
    
    # Define time range (last 1 hour)
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    print(f"Fetching metrics from {start_time.isoformat()} to {end_time.isoformat()}")
    
    # Initialize clients
    datadog_fetcher = DatadogMetricsFetcher(datadog_api_key, datadog_app_key, datadog_site)
    supabase_store = SupabaseMetricsStore(supabase_url, supabase_key)
    
    # Fetch and store metrics
    all_metrics = []
    
    for metric_name in metrics_to_fetch:
        print(f"Fetching metric: {metric_name}")
        metric_data = datadog_fetcher.fetch_metric(metric_name, start_time, end_time)
        all_metrics.extend(metric_data)
        print(f"  Retrieved {len(metric_data)} data points")
    
    # Store metrics in Supabase
    if all_metrics:
        success = supabase_store.insert_metrics(all_metrics)
        if success:
            print(f"\nTotal metrics ingested: {len(all_metrics)}")
            return 0
        else:
            print("\nFailed to store metrics in Supabase.", file=sys.stderr)
            return 1
    else:
        print("\nNo metrics retrieved from Datadog.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

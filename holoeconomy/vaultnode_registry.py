"""
VaultNode Registry CLI

A command-line interface to interact with the VaultNode registry in Supabase.
"""

import argparse
import os

from supabase import Client, create_client

# Supabase configuration
# It's recommended to use environment variables for these
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")


def get_supabase_client() -> Client:
    """Creates and returns a Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in environment variables.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def list_vaultnodes(client: Client):
    """Lists all VaultNodes."""
    print("Listing all VaultNodes...")
    response = client.table("vaultnodes").select("*").execute()
    if response.data:
        for node in response.data:
            print(node)
    else:
        print("No VaultNodes found.")


def get_vaultnode(client: Client, node_id: str):
    """Retrieves a specific VaultNode by its ID."""
    print(f"Getting VaultNode with ID: {node_id}...")
    response = client.table("vaultnodes").select("*").eq("id", node_id).execute()
    if response.data:
        print(response.data[0])
    else:
        print(f"VaultNode with ID {node_id} not found.")


def create_vaultnode(client: Client, ref_id: str, ref_type: str, commit_sha: str = None):
    """Creates a new VaultNode."""
    print("Creating a new VaultNode...")
    try:
        # Assuming 'seal_vaultnode' is a function in your Supabase instance
        response = client.rpc(
            "seal_vaultnode", {"ref_id": ref_id, "ref_type": ref_type, "commit_sha": commit_sha}
        ).execute()
        if response.data:
            print("Successfully created VaultNode:")
            print(response.data[0])
        else:
            print("Failed to create VaultNode.")
            if response.error:
                print(f"Error: {response.error.message}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    """Main function to handle CLI arguments."""
    parser = argparse.ArgumentParser(description="VaultNode Registry CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List command
    parser_list = subparsers.add_parser("list", help="List all VaultNodes")
    parser_list.set_defaults(func=list_vaultnodes)

    # Get command
    parser_get = subparsers.add_parser("get", help="Get a specific VaultNode by ID")
    parser_get.add_argument("node_id", type=str, help="The ID of the VaultNode to retrieve")
    parser_get.set_defaults(func=lambda args, client: get_vaultnode(client, args.node_id))

    # Create command
    parser_create = subparsers.add_parser("create", help="Create a new VaultNode")
    parser_create.add_argument("--ref-id", required=True, type=str, help="The reference ID for the new VaultNode")
    parser_create.add_argument("--ref-type", required=True, type=str, help="The reference type for the new VaultNode")
    parser_create.add_argument("--commit-sha", type=str, help="The commit SHA for the new VaultNode")
    parser_create.set_defaults(
        func=lambda args, client: create_vaultnode(client, args.ref_id, args.ref_type, args.commit_sha)
    )

    args = parser.parse_args()

    try:
        client = get_supabase_client()
        if args.command == "list":
            list_vaultnodes(client)
        elif args.command == "get":
            get_vaultnode(client, args.node_id)
        elif args.command == "create":
            create_vaultnode(client, args.ref_id, args.ref_type, args.commit_sha)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

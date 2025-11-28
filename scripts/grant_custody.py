from core.db import db
from core.custody import CustodyRegistry

def main():
    registry = CustodyRegistry(db)
    
    print("Granting permissions to service_role...")
    registry.grant_custody("service_role", {
        "can_resolve_lock": True,
        "can_manage_autopoiesis": True,
        "can_update_constitution_hash": True
    })
    
    print("Granting permissions to guardian_daemon...")
    registry.grant_custody("guardian_daemon", {
        "can_monitor_constitution": True
    })
    
    print("Permissions granted.")

if __name__ == "__main__":
    main()

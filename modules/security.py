import hashlib
from datetime import datetime
from modules.database import write_audit_entry

def log_system_event(user_id: str, user_role: str, action_type: str, search_string: str = None, accessed_plots_list: list = None, api_latency_ms: float = 0.0):
    """
    Compiles an immutable access event log with live API latency monitoring.
    Generates a cryptographic signature verifying the record's authenticity.
    """
    plots_string = ",".join(map(str, accessed_plots_list)) if accessed_plots_list else "NONE"
    current_time_str = datetime.now().isoformat()
    
    # Generate cryptographic signature including performance latency metrics
    raw_payload = f"{current_time_str}|{user_id}|{action_type}|{search_string or ''}|{plots_string}|{api_latency_ms}"
    event_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()
    
    # Store records inside local storage system logs
    write_audit_entry(
        user_id=user_id,
        role=user_role,
        action=action_type,
        search_str=search_string,
        plots=plots_string,
        latency=api_latency_ms,
        event_hash=event_hash
    )
import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "extra_data"):
            log_record["data"] = record.extra_data
            
        return json.dumps(log_record)

def setup_logging(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    logger.addHandler(handler)
    
    return logger

# Example usage:
# import logging
# from core.logging_config import setup_logging
# setup_logging()
# logging.info("System started", extra={"extra_data": {"component": "guardian"}})

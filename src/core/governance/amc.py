import logging
import time
import uuid
from typing import Dict, Optional
from datetime import datetime
from src.core.database import get_db_connection

logger = logging.getLogger(__name__)

class AutonomousMarketController:
    """
    PID-based Autonomous Market Controller (AMC) for SpiralOS.
    Regulates economic parameters (transaction fees) based on volatility.
    """
    
    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.05, setpoint: float = 0.0):
        self.controller_id = str(uuid.uuid4())
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        
        self.prev_error = 0.0
        self.integral = 0.0
        self.last_update_time = time.time()
        
        # Default output limits (transaction fee rate)
        self.output_min = 0.001  # 0.1%
        self.output_max = 0.05   # 5.0%
        
        logger.info(f"AMC Initialized: ID={self.controller_id}, Kp={kp}, Ki={ki}, Kd={kd}")

    def update(self, process_variable: float) -> float:
        """
        Update the PID controller with the current process variable (e.g., volatility).
        Returns the control output (e.g., new transaction fee rate).
        """
        current_time = time.time()
        dt = current_time - self.last_update_time
        if dt <= 0:
            dt = 0.001 # Prevent division by zero
            
        error = self.setpoint - process_variable
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        
        # Clamp output
        output = max(self.output_min, min(self.output_max, output))
        
        # Store state
        self.prev_error = error
        self.last_update_time = current_time
        
        self._log_state(process_variable, error, derivative, output)
        
        return output

    def _log_state(self, pv: float, error: float, derivative: float, output: float):
        """Log the controller state to the database."""
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO autonomous_market_controller_state 
                    (controller_id, kp, ki, kd, setpoint, process_variable, error, integral, derivative, output, volatility, transaction_fee_rate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        self.controller_id, self.kp, self.ki, self.kd, self.setpoint,
                        pv, error, self.integral, derivative, output, pv, output
                    )
                )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log AMC state: {e}")

    def tune(self, kp: float, ki: float, kd: float):
        """Manually tune PID gains."""
        self.kp = kp
        self.ki = ki
        self.kd = kd
        logger.info(f"AMC Tuned: Kp={kp}, Ki={ki}, Kd={kd}")

    def get_status(self) -> Dict:
        return {
            "controller_id": self.controller_id,
            "kp": self.kp,
            "ki": self.ki,
            "kd": self.kd,
            "setpoint": self.setpoint,
            "integral": self.integral,
            "prev_error": self.prev_error
        }

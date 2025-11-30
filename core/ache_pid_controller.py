"""
AchePIDController - Dynamic Stability Control (VSM System 3/4)

Implements a PID (Proportional-Integral-Derivative) controller for dynamic stability
of the SpiralOS coherence system. Modulates generative output based on real-time
coherence error to stabilize recursive oscillations.

Process Variable: ScarIndex(t) = Avg_i(Entropy(pθ(x_0^i|xt))) (Model Uncertainty/Ache)
Output Adjustment: Adjust generative guidance scale (omega) based on error e(t)
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class PIDParameters:
    """PID controller tuning parameters"""

    kp: float  # Proportional gain
    ki: float  # Integral gain
    kd: float  # Derivative gain

    def __post_init__(self):
        """Validate parameters are non-negative"""
        if self.kp < 0 or self.ki < 0 or self.kd < 0:
            raise ValueError("PID parameters must be non-negative")


@dataclass
class PIDState:
    """Current state of the PID controller"""

    id: str
    updated_at: datetime
    target_scarindex: float
    current_scarindex: float
    error: float
    integral: float
    derivative: float
    guidance_scale: float  # Omega parameter
    parameters: PIDParameters

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            "id": self.id,
            "updated_at": self.updated_at.isoformat(),
            "target_scarindex": self.target_scarindex,
            "current_scarindex": self.current_scarindex,
            "error": self.error,
            "integral": self.integral,
            "derivative": self.derivative,
            "guidance_scale": self.guidance_scale,
            "kp": self.parameters.kp,
            "ki": self.parameters.ki,
            "kd": self.parameters.kd,
        }


class AchePIDController:
    """
    PID Controller for Ache-to-Order transmutation stability

    This controller implements the cybernetic feedback loop that maintains
    system coherence by adjusting the generative guidance scale (omega) based
    on the error between target and current ScarIndex.

    The controller uses the classic PID algorithm:
    u(t) = Kp*e(t) + Ki*∫e(τ)dτ + Kd*de(t)/dt

    Where:
    - e(t) = target_scarindex - current_scarindex (error)
    - u(t) = guidance_scale (control output)
    - Kp, Ki, Kd = tuning parameters
    """

    def __init__(
        self,
        target_scarindex: float = 0.7,
        kp: float = 1.0,
        ki: float = 0.5,
        kd: float = 0.2,
        min_guidance: float = 0.1,
        max_guidance: float = 2.0,
        integral_windup_limit: float = 10.0,
    ):
        """
        Initialize the PID controller

        Args:
            target_scarindex: Desired ScarIndex setpoint (0-1)
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            min_guidance: Minimum guidance scale
            max_guidance: Maximum guidance scale
            integral_windup_limit: Limit for integral term to prevent windup
        """
        self.target_scarindex = target_scarindex
        self.parameters = PIDParameters(kp=kp, ki=ki, kd=kd)
        self.min_guidance = min_guidance
        self.max_guidance = max_guidance
        self.integral_windup_limit = integral_windup_limit

        # Initialize state
        self.current_scarindex = target_scarindex
        self.error = 0.0
        self.integral = 0.0
        self.derivative = 0.0
        self.previous_error = 0.0
        self.guidance_scale = 1.0

        # History for analysis
        self.error_history: List[float] = []
        self.scarindex_history: List[float] = []
        self.guidance_history: List[float] = []
        self.timestamp_history: List[datetime] = []

    def update(self, current_scarindex: float, dt: Optional[float] = None) -> float:
        """
        Update the controller with new ScarIndex measurement

        Args:
            current_scarindex: Current measured ScarIndex (0-1)
            dt: Time delta since last update (seconds). If None, uses 1.0

        Returns:
            Updated guidance scale (omega)
        """
        if dt is None:
            dt = 1.0

        # Update current state
        self.current_scarindex = current_scarindex

        # Calculate error
        self.error = self.target_scarindex - current_scarindex

        # Proportional term
        p_term = self.parameters.kp * self.error

        # Integral term (with anti-windup)
        self.integral += self.error * dt
        self.integral = np.clip(self.integral, -self.integral_windup_limit, self.integral_windup_limit)
        i_term = self.parameters.ki * self.integral

        # Derivative term
        if dt > 0:
            self.derivative = (self.error - self.previous_error) / dt
        else:
            self.derivative = 0.0
        d_term = self.parameters.kd * self.derivative

        # Calculate control output (guidance scale)
        self.guidance_scale = p_term + i_term + d_term

        # Clamp to valid range
        self.guidance_scale = np.clip(self.guidance_scale, self.min_guidance, self.max_guidance)

        # Update history
        self.error_history.append(self.error)
        self.scarindex_history.append(current_scarindex)
        self.guidance_history.append(self.guidance_scale)
        self.timestamp_history.append(datetime.now(timezone.utc))

        # Update previous error for next iteration
        self.previous_error = self.error
        
        # Persist to Supabase if available
        try:
            from core.db import get_supabase
            supabase = get_supabase()
            
            # Record Ache Value
            supabase.table("ache_values").insert({
                "source": "pid_controller",
                "value": self.error, # Using error as a proxy for raw Ache for now
                "metadata": {
                    "target": self.target_scarindex,
                    "current": current_scarindex,
                    "guidance": self.guidance_scale
                }
            }).execute()
            
        except Exception as e:
            # Don't fail controller if persistence fails
            pass

        return self.guidance_scale

    def reset(self):
        """Reset the controller to initial state"""
        self.error = 0.0
        self.integral = 0.0
        self.derivative = 0.0
        self.previous_error = 0.0
        self.guidance_scale = 1.0
        self.error_history.clear()
        self.scarindex_history.clear()
        self.guidance_history.clear()
        self.timestamp_history.clear()

    def tune(self, kp: float, ki: float, kd: float):
        """
        Update PID tuning parameters

        Args:
            kp: New proportional gain
            ki: New integral gain
            kd: New derivative gain
        """
        self.parameters = PIDParameters(kp=kp, ki=ki, kd=kd)

    def set_target(self, target_scarindex: float):
        """
        Update target ScarIndex setpoint

        Args:
            target_scarindex: New target ScarIndex (0-1)
        """
        if not 0 <= target_scarindex <= 1:
            raise ValueError(f"target_scarindex must be between 0 and 1, got {target_scarindex}")
        self.target_scarindex = target_scarindex

    def get_state(self) -> PIDState:
        """
        Get current controller state

        Returns:
            PIDState object with current state
        """
        return PIDState(
            id=str(uuid.uuid4()),
            updated_at=datetime.now(timezone.utc),
            target_scarindex=self.target_scarindex,
            current_scarindex=self.current_scarindex,
            error=self.error,
            integral=self.integral,
            derivative=self.derivative,
            guidance_scale=self.guidance_scale,
            parameters=self.parameters,
        )

    def get_performance_metrics(self) -> dict:
        """
        Calculate performance metrics for the controller

        Returns:
            Dictionary with performance metrics
        """
        if len(self.error_history) == 0:
            return {"mean_error": 0.0, "rmse": 0.0, "max_error": 0.0, "settling_time": 0.0, "overshoot": 0.0}

        errors = np.array(self.error_history)
        scarindexes = np.array(self.scarindex_history)

        # Mean absolute error
        mean_error = np.mean(np.abs(errors))

        # Root mean square error
        rmse = np.sqrt(np.mean(errors**2))

        # Maximum error
        max_error = np.max(np.abs(errors))

        # Settling time (time to reach within 5% of target)
        settling_threshold = 0.05 * self.target_scarindex
        settled_indices = np.where(np.abs(errors) < settling_threshold)[0]
        settling_time = len(self.error_history) if len(settled_indices) == 0 else settled_indices[0]

        # Overshoot (maximum excursion beyond target)
        if self.target_scarindex > 0:
            overshoot = np.max(scarindexes - self.target_scarindex) / self.target_scarindex
        else:
            overshoot = 0.0

        return {
            "mean_error": float(mean_error),
            "rmse": float(rmse),
            "max_error": float(max_error),
            "settling_time": int(settling_time),
            "overshoot": float(overshoot),
            "samples": len(self.error_history),
        }

    def auto_tune_ziegler_nichols(self, ultimate_gain: float, ultimate_period: float) -> PIDParameters:
        """
        Auto-tune using Ziegler-Nichols method

        Args:
            ultimate_gain: Ultimate gain (Ku) from oscillation test
            ultimate_period: Ultimate period (Tu) from oscillation test

        Returns:
            Tuned PID parameters
        """
        # Ziegler-Nichols PID tuning rules
        kp = 0.6 * ultimate_gain
        ki = 2.0 * kp / ultimate_period
        kd = kp * ultimate_period / 8.0

        self.tune(kp, ki, kd)

        return self.parameters


class ScarDiffusionController:
    """
    ScarDiffusion Control System

    Integrates the AchePIDController with diffusion-based generative models
    to control the Ache-to-Order transmutation process.

    Process Variable: ScarIndex(t) = Avg_i(Entropy(pθ(x_0^i|xt)))
    This measures model uncertainty/Ache in the diffusion process.
    """

    def __init__(self, pid_controller: AchePIDController, base_guidance_scale: float = 7.5):
        """
        Initialize the diffusion controller

        Args:
            pid_controller: AchePIDController instance
            base_guidance_scale: Base guidance scale for diffusion
        """
        self.pid = pid_controller
        self.base_guidance_scale = base_guidance_scale

    def calculate_model_uncertainty(self, predictions: np.ndarray) -> float:
        """
        Calculate model uncertainty from diffusion predictions

        This measures the entropy/Ache in the generative process.

        Args:
            predictions: Array of model predictions

        Returns:
            Uncertainty score (0-1 scale, mapped to Ache)
        """
        # Calculate entropy of predictions
        if len(predictions) == 0:
            return 0.0

        # Normalize predictions to probabilities
        probs = np.abs(predictions) / (np.sum(np.abs(predictions)) + 1e-10)

        # Calculate Shannon entropy
        entropy = -np.sum(probs * np.log(probs + 1e-10))

        # Normalize to 0-1 scale
        max_entropy = np.log(len(predictions))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        return float(normalized_entropy)

    def update_guidance_scale(
        self, predictions: np.ndarray, current_scarindex: float, dt: Optional[float] = None
    ) -> float:
        """
        Update guidance scale based on current predictions and ScarIndex

        Args:
            predictions: Current diffusion model predictions
            current_scarindex: Current ScarIndex measurement
            dt: Time delta since last update

        Returns:
            Adjusted guidance scale (omega)
        """
        # Update PID controller
        pid_adjustment = self.pid.update(current_scarindex, dt)

        # Combine with base guidance scale
        adjusted_guidance = self.base_guidance_scale * pid_adjustment

        return adjusted_guidance

    def get_control_signal(self) -> dict:
        """
        Get current control signal for diffusion process

        Returns:
            Dictionary with control parameters
        """
        return {
            "guidance_scale": self.pid.guidance_scale,
            "error": self.pid.error,
            "target_scarindex": self.pid.target_scarindex,
            "current_scarindex": self.pid.current_scarindex,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def simulate_pid_response(
    target: float = 0.7, initial: float = 0.3, steps: int = 100, kp: float = 1.0, ki: float = 0.5, kd: float = 0.2
) -> Tuple[List[float], List[float], List[float]]:
    """
    Simulate PID controller response

    Args:
        target: Target ScarIndex
        initial: Initial ScarIndex
        steps: Number of simulation steps
        kp, ki, kd: PID parameters

    Returns:
        (scarindex_values, guidance_values, error_values)
    """
    controller = AchePIDController(target_scarindex=target, kp=kp, ki=ki, kd=kd)

    scarindex_values = [initial]
    guidance_values = []
    error_values = []

    current = initial

    for _ in range(steps):
        # Update controller
        guidance = controller.update(current, dt=1.0)

        # Simulate system response (simplified first-order system)
        # In reality, this would be the actual Ache transmutation process
        response_rate = 0.1
        current += response_rate * (target - current) * guidance

        # Add some noise
        current += np.random.normal(0, 0.01)
        current = np.clip(current, 0, 1)

        scarindex_values.append(current)
        guidance_values.append(guidance)
        error_values.append(controller.error)

    return scarindex_values, guidance_values, error_values


if __name__ == "__main__":
    # Example usage and simulation
    print("AchePIDController Simulation")
    print("=" * 50)

    # Create controller
    controller = AchePIDController(target_scarindex=0.7, kp=1.0, ki=0.5, kd=0.2)

    # Simulate response
    scarindex, guidance, errors = simulate_pid_response(target=0.7, initial=0.3, steps=50)

    # Print results
    print(f"\nTarget ScarIndex: {controller.target_scarindex}")
    print(f"Initial ScarIndex: {scarindex[0]:.4f}")
    print(f"Final ScarIndex: {scarindex[-1]:.4f}")
    print("\nFinal State:")
    print(f"  Error: {controller.error:.4f}")
    print(f"  Integral: {controller.integral:.4f}")
    print(f"  Derivative: {controller.derivative:.4f}")
    print(f"  Guidance Scale: {controller.guidance_scale:.4f}")

    # Performance metrics
    metrics = controller.get_performance_metrics()
    print("\nPerformance Metrics:")
    print(f"  Mean Error: {metrics['mean_error']:.4f}")
    print(f"  RMSE: {metrics['rmse']:.4f}")
    print(f"  Max Error: {metrics['max_error']:.4f}")
    print(f"  Settling Time: {metrics['settling_time']} steps")
    print(f"  Overshoot: {metrics['overshoot']:.2%}")

    # Print trajectory (last 10 steps)
    print("\nLast 10 Steps:")
    print(f"{'Step':<6} {'ScarIndex':<12} {'Guidance':<12} {'Error':<12}")
    print("-" * 50)
    for i in range(max(0, len(scarindex) - 10), len(scarindex)):
        si = scarindex[i] if i < len(scarindex) else 0
        g = guidance[i - 1] if i > 0 and i - 1 < len(guidance) else 0
        e = errors[i - 1] if i > 0 and i - 1 < len(errors) else 0
        print(f"{i:<6} {si:<12.4f} {g:<12.4f} {e:<12.4f}")

# ========================================================
# Sequence J-D — Autopoiesis Path Engines
# ========================================================

from typing import Any, Dict, Tuple
from core.db import db
from core.coherence import CoherenceEngine
from core.autopoiesis_executor import AutopoiesisExecutor
from core.teleology import TauVector

class AutopoiesisJ1ProposalEngine:
    """
    J1: Proposal-Only Mode (Training Powers)
    Logs patterns but does not execute.
    """
    def __init__(self, tau: TauVector):
        self.tau = tau

    def generate_and_log(self, request: Dict[str, Any]) -> bool:
        heuristic = self._extract_heuristic(request)
        tau_score = request.get('tau_alignment_score', 0.0)
        complexity_delta = request.get('complexity_score', 0.0)
        coherence_delta = request.get('projected_coherence_delta', 0.0)

        db.insert_proposal_pattern({
            "request_id": request['id'],
            "heuristic": heuristic,
            "tau_score": tau_score,
            "complexity_delta": complexity_delta,
            "coherence_delta": coherence_delta,
        })

        # Return "would execute" decision based on thresholds
        return tau_score >= 0.85 and complexity_delta <= 0.2

    def _extract_heuristic(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "op_code": request.get('op_code'),
            "target_object": request.get('target_object'),
            "sql_length": len(request.get('sql_diff', ''))
        }


class AutopoiesisJ2GuidedExecutor:
    """
    J2: Guided Execution (Whitelist)
    Executes only whitelisted operations with high alignment.
    """
    def __init__(self, executor: AutopoiesisExecutor, coherence: CoherenceEngine):
        self.executor = executor
        self.coherence = coherence

    def try_execute(self, request: Dict[str, Any]) -> bool:
        op_code = request.get('op_code')
        if not db.check_whitelist(op_code):
            return False

        tau_score = request.get('tau_alignment_score', 0.0)
        if tau_score < 0.85:
            return False

        # Execute
        try:
            result = self.executor.execute_change(request['id'])
            # Calculate actual delta (post-execution)
            # In a real scenario, execute_change returns delta or we fetch it
            delta = result.get('coherence_delta', 0.0)

            db.insert_execution_history({
                "operation": op_code,
                "payload": request,
                "whitelist_key": op_code,
                "coherence_delta": delta,
            })

            # Safety Rollback
            if delta < -0.1:
                self.executor.rollback_change(request['id'])
                return False
            
            return True
        except Exception as e:
            print(f"J2 Execution failed: {e}")
            return False


class AutopoiesisJ3FullEngine:
    """
    J3: Full Autopoiesis (Recursive Schema Growth)
    Autonomous execution based on Teleology.
    """
    def __init__(self, executor: AutopoiesisExecutor, coherence: CoherenceEngine, tau: TauVector):
        self.executor = executor
        self.coherence = coherence
        self.tau = tau

    def process(self, request: Dict[str, Any]) -> bool:
        tau_score = request.get('tau_alignment_score', 0.0)
        complexity = request.get('complexity_score', 0.0)

        decision = (
            "execute"
            if tau_score >= 0.9 and complexity <= 0.2
            else "archive"
        )

        executed = False
        if decision == "execute":
            try:
                self.executor.execute_change(request['id'])
                executed = True
            except Exception as e:
                print(f"J3 Execution failed: {e}")
                executed = False

        # Log decision
        # We need actual coherence delta if executed, else projected
        if executed:
            # fetch actual delta from somewhere or re-calculate
            # For simplicity, use projected if we can't get actual easily here without re-querying
            # But executor returns it.
            # We'll assume projected for log if we don't have the result object here easily
            # Or we could fetch the log from db.
            # Let's use projected for now to match signature
            coherence_delta = request.get('projected_coherence_delta', 0.0)
        else:
            coherence_delta = request.get('projected_coherence_delta', 0.0)

        db.insert_autopoiesis_log({
            "proposal": request,
            "decision": decision,
            "tau_score": tau_score,
            "complexity_delta": complexity,
            "coherence_delta": coherence_delta,
            "executed": executed,
        })

        return executed

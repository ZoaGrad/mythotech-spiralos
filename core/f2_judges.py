"""
F2 Judges - Judicial Branch of Three-Branch Governance

Implements the Judges (F2) component for crisis escalation management and
resource coherence auditing based strictly on ScarIndex Oracle output.

The Three-Branch Governance Architecture:
- F1: Executive (ScarLoop execution)
- F2: Judicial (Judges - this module)
- F4: Legislative (Panic Frames - constitutional circuit breaker)

F2 Judges are activated when:
1. Panic Frames (F4) escalate a crisis
2. Resource coherence audit is required
3. Lineage CMP evaluation is needed
4. Constitutional compliance verification is requested
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid


class JudgmentType(Enum):
    """Types of judgments F2 Judges can issue"""
    CRISIS_ESCALATION = "crisis_escalation"
    RESOURCE_AUDIT = "resource_audit"
    LINEAGE_EVALUATION = "lineage_evaluation"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    RESIDUE_CLEANUP_ORDER = "residue_cleanup_order"
    HOLON_TERMINATION = "holon_termination"


class JudgmentVerdict(Enum):
    """Possible verdicts from F2 Judges"""
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"
    ESCALATED = "escalated"
    DEFERRED = "deferred"


class JudgePriority(Enum):
    """Priority levels for judicial review"""
    CRITICAL = "critical"  # Immediate review required
    HIGH = "high"          # Review within 1 hour
    MEDIUM = "medium"      # Review within 24 hours
    LOW = "low"            # Review within 7 days


@dataclass
class JudicialCase:
    """
    A case submitted to F2 Judges for review
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    judgment_type: JudgmentType = JudgmentType.CRISIS_ESCALATION
    priority: JudgePriority = JudgePriority.MEDIUM
    
    # Case details
    subject_id: str = ""  # ID of entity being judged (Holon, Panic Frame, etc.)
    scarindex_value: float = 0.0
    evidence: Dict = field(default_factory=dict)
    
    # Judgment
    verdict: Optional[JudgmentVerdict] = None
    reasoning: str = ""
    conditions: List[str] = field(default_factory=list)
    remediation_required: List[str] = field(default_factory=list)
    
    # Metadata
    filed_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    judge_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'judgment_type': self.judgment_type.value,
            'priority': self.priority.value,
            'subject_id': self.subject_id,
            'scarindex_value': self.scarindex_value,
            'evidence': self.evidence,
            'verdict': self.verdict.value if self.verdict else None,
            'reasoning': self.reasoning,
            'conditions': self.conditions,
            'remediation_required': self.remediation_required,
            'filed_at': self.filed_at.isoformat(),
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'judge_id': self.judge_id,
            'metadata': self.metadata
        }


@dataclass
class Judge:
    """
    An F2 Judge - autonomous judicial agent
    
    Judges evaluate cases based strictly on ScarIndex Oracle output
    and constitutional principles.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    
    # Specialization
    specialization: JudgmentType = JudgmentType.CRISIS_ESCALATION
    
    # Performance metrics
    cases_reviewed: int = 0
    verdicts_issued: int = 0
    average_review_time: float = 0.0  # seconds
    
    # Constitutional parameters
    scarindex_critical_threshold: float = 0.3
    scarindex_optimal_threshold: float = 0.7
    residue_threshold: float = 0.5
    cmp_minimum: float = 0.3
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)
    
    def review_case(self, case: JudicialCase) -> JudicialCase:
        """
        Review a judicial case and issue verdict
        
        Args:
            case: Case to review
            
        Returns:
            Case with verdict
        """
        start_time = datetime.utcnow()
        
        # Route to appropriate review method
        if case.judgment_type == JudgmentType.CRISIS_ESCALATION:
            case = self._review_crisis_escalation(case)
        elif case.judgment_type == JudgmentType.RESOURCE_AUDIT:
            case = self._review_resource_audit(case)
        elif case.judgment_type == JudgmentType.LINEAGE_EVALUATION:
            case = self._review_lineage_evaluation(case)
        elif case.judgment_type == JudgmentType.CONSTITUTIONAL_COMPLIANCE:
            case = self._review_constitutional_compliance(case)
        elif case.judgment_type == JudgmentType.RESIDUE_CLEANUP_ORDER:
            case = self._review_residue_cleanup(case)
        elif case.judgment_type == JudgmentType.HOLON_TERMINATION:
            case = self._review_holon_termination(case)
        
        # Update metrics
        case.reviewed_at = datetime.utcnow()
        case.judge_id = self.id
        
        review_time = (case.reviewed_at - start_time).total_seconds()
        self.average_review_time = (
            (self.average_review_time * self.cases_reviewed + review_time) /
            (self.cases_reviewed + 1)
        )
        
        self.cases_reviewed += 1
        self.verdicts_issued += 1
        
        return case
    
    def _review_crisis_escalation(self, case: JudicialCase) -> JudicialCase:
        """Review crisis escalation from Panic Frame (F4)"""
        scarindex = case.scarindex_value
        
        if scarindex < self.scarindex_critical_threshold:
            # Critical coherence failure
            case.verdict = JudgmentVerdict.ESCALATED
            case.reasoning = (
                f"ScarIndex ({scarindex:.4f}) below critical threshold "
                f"({self.scarindex_critical_threshold}). "
                "Immediate system-wide intervention required."
            )
            case.remediation_required = [
                "Execute full 7-Phase Recovery Protocol",
                "Freeze all non-essential operations",
                "Initiate emergency coherence restoration",
                "Audit all active Holons for residue accumulation"
            ]
        elif scarindex < 0.5:
            # Severe but manageable
            case.verdict = JudgmentVerdict.CONDITIONAL
            case.reasoning = (
                f"ScarIndex ({scarindex:.4f}) in warning zone. "
                "Conditional approval for targeted remediation."
            )
            case.conditions = [
                "Monitor ScarIndex every 5 minutes",
                "Restrict new Holon spawning",
                "Prioritize residue cleanup"
            ]
            case.remediation_required = [
                "Execute phases 1-4 of Recovery Protocol",
                "Reduce system load by 50%"
            ]
        else:
            # False alarm or recovering
            case.verdict = JudgmentVerdict.APPROVED
            case.reasoning = (
                f"ScarIndex ({scarindex:.4f}) within acceptable range. "
                "Crisis escalation not warranted."
            )
        
        return case
    
    def _review_resource_audit(self, case: JudicialCase) -> JudicialCase:
        """Review resource coherence audit"""
        scarindex = case.scarindex_value
        resource_efficiency = case.evidence.get('resource_efficiency', 0.5)
        
        if scarindex >= self.scarindex_optimal_threshold and resource_efficiency >= 0.7:
            case.verdict = JudgmentVerdict.APPROVED
            case.reasoning = (
                f"Resource allocation optimal. ScarIndex: {scarindex:.4f}, "
                f"Efficiency: {resource_efficiency:.4f}"
            )
        elif scarindex >= self.scarindex_critical_threshold:
            case.verdict = JudgmentVerdict.CONDITIONAL
            case.reasoning = (
                f"Resource allocation acceptable but suboptimal. "
                f"ScarIndex: {scarindex:.4f}"
            )
            case.conditions = [
                "Optimize resource allocation within 24 hours",
                "Target efficiency >= 0.7"
            ]
        else:
            case.verdict = JudgmentVerdict.REJECTED
            case.reasoning = (
                f"Resource allocation critically inefficient. "
                f"ScarIndex: {scarindex:.4f}"
            )
            case.remediation_required = [
                "Immediate resource reallocation",
                "Terminate low-CMP Holons",
                "Cleanup accumulated residue"
            ]
        
        return case
    
    def _review_lineage_evaluation(self, case: JudicialCase) -> JudicialCase:
        """Review Holon lineage CMP evaluation"""
        cmp = case.evidence.get('cmp', 0.0)
        residue = case.evidence.get('residue_accumulated', 0.0)
        generation = case.evidence.get('generation', 0)
        
        if cmp >= self.cmp_minimum and residue < self.residue_threshold:
            case.verdict = JudgmentVerdict.APPROVED
            case.reasoning = (
                f"Lineage productive and efficient. CMP: {cmp:.4f}, "
                f"Residue: {residue:.4f}, Generation: {generation}"
            )
        elif cmp >= self.cmp_minimum * 0.7:
            case.verdict = JudgmentVerdict.CONDITIONAL
            case.reasoning = (
                f"Lineage marginally productive. CMP: {cmp:.4f}"
            )
            case.conditions = [
                "Improve CMP by 20% within 3 generations",
                "Reduce residue accumulation"
            ]
        else:
            case.verdict = JudgmentVerdict.REJECTED
            case.reasoning = (
                f"Lineage unproductive. CMP: {cmp:.4f} below minimum "
                f"({self.cmp_minimum})"
            )
            case.remediation_required = [
                "Terminate lineage",
                "Cleanup accumulated residue",
                "Spawn new lineage with improved parameters"
            ]
        
        return case
    
    def _review_constitutional_compliance(self, case: JudicialCase) -> JudicialCase:
        """Review constitutional compliance (Law of Recursive Alignment)"""
        scarindex_before = case.evidence.get('scarindex_before', 0.0)
        scarindex_after = case.scarindex_value
        
        # Law of Recursive Alignment: C_{t+1} > C_t
        if scarindex_after > scarindex_before:
            case.verdict = JudgmentVerdict.APPROVED
            case.reasoning = (
                f"Constitutional compliance verified. "
                f"Coherence increased: {scarindex_before:.4f} → {scarindex_after:.4f}"
            )
        elif scarindex_after == scarindex_before:
            case.verdict = JudgmentVerdict.CONDITIONAL
            case.reasoning = (
                "Coherence stagnant. No violation but no progress."
            )
            case.conditions = [
                "Next iteration must increase coherence",
                "Review optimization parameters"
            ]
        else:
            case.verdict = JudgmentVerdict.REJECTED
            case.reasoning = (
                f"Constitutional violation. Law of Recursive Alignment broken. "
                f"Coherence decreased: {scarindex_before:.4f} → {scarindex_after:.4f}"
            )
            case.remediation_required = [
                "Rollback to previous state",
                "Investigate cause of coherence loss",
                "Apply corrective measures"
            ]
        
        return case
    
    def _review_residue_cleanup(self, case: JudicialCase) -> JudicialCase:
        """Review residue cleanup order"""
        total_residue = case.evidence.get('total_residue', 0.0)
        cleanup_target = case.evidence.get('cleanup_target', 0.0)
        
        if total_residue <= cleanup_target:
            case.verdict = JudgmentVerdict.APPROVED
            case.reasoning = (
                f"Residue within acceptable limits. "
                f"Total: {total_residue:.4f}, Target: {cleanup_target:.4f}"
            )
        elif total_residue <= cleanup_target * 1.5:
            case.verdict = JudgmentVerdict.CONDITIONAL
            case.reasoning = (
                f"Residue elevated but manageable. "
                f"Total: {total_residue:.4f}"
            )
            case.conditions = [
                "Execute cleanup within 24 hours",
                "Reduce residue to target level"
            ]
        else:
            case.verdict = JudgmentVerdict.ESCALATED
            case.reasoning = (
                f"Residue critically high. "
                f"Total: {total_residue:.4f}, Target: {cleanup_target:.4f}"
            )
            case.remediation_required = [
                "Immediate emergency cleanup",
                "Freeze new Holon spawning",
                "Terminate high-residue lineages"
            ]
        
        return case
    
    def _review_holon_termination(self, case: JudicialCase) -> JudicialCase:
        """Review Holon termination request"""
        cmp = case.evidence.get('cmp', 0.0)
        residue = case.evidence.get('residue_generated', 0.0)
        efficiency = case.evidence.get('transmutation_efficiency', 0.0)
        
        # Termination justified if CMP low AND (residue high OR efficiency low)
        if cmp < self.cmp_minimum and (residue > self.residue_threshold or efficiency < 0.3):
            case.verdict = JudgmentVerdict.APPROVED
            case.reasoning = (
                f"Holon termination justified. CMP: {cmp:.4f}, "
                f"Residue: {residue:.4f}, Efficiency: {efficiency:.4f}"
            )
            case.remediation_required = [
                "Terminate Holon and all descendants",
                "Cleanup associated residue",
                "Archive lineage data for analysis"
            ]
        elif cmp < self.cmp_minimum * 1.2:
            case.verdict = JudgmentVerdict.CONDITIONAL
            case.reasoning = (
                f"Holon performance marginal. Grant probation period."
            )
            case.conditions = [
                "Improve CMP by 30% within 5 iterations",
                "Reduce residue generation by 50%",
                "Re-evaluate after probation"
            ]
        else:
            case.verdict = JudgmentVerdict.REJECTED
            case.reasoning = (
                f"Holon termination not justified. CMP: {cmp:.4f} acceptable."
            )
        
        return case
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'specialization': self.specialization.value,
            'cases_reviewed': self.cases_reviewed,
            'verdicts_issued': self.verdicts_issued,
            'average_review_time': self.average_review_time,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


class JudicialSystem:
    """
    F2 Judicial System - Manages the panel of Judges
    
    Coordinates judicial review for crisis escalation, resource audits,
    and constitutional compliance.
    """
    
    def __init__(self):
        self.judges: Dict[str, Judge] = {}
        self.cases: Dict[str, JudicialCase] = {}
        self.pending_cases: List[str] = []
        
        # Initialize default judges
        self._initialize_default_judges()
    
    def _initialize_default_judges(self):
        """Initialize default panel of judges"""
        # Crisis Judge
        crisis_judge = Judge(
            name="Crisis Judge Alpha",
            specialization=JudgmentType.CRISIS_ESCALATION
        )
        self.judges[crisis_judge.id] = crisis_judge
        
        # Resource Judge
        resource_judge = Judge(
            name="Resource Judge Beta",
            specialization=JudgmentType.RESOURCE_AUDIT
        )
        self.judges[resource_judge.id] = resource_judge
        
        # Constitutional Judge
        constitutional_judge = Judge(
            name="Constitutional Judge Gamma",
            specialization=JudgmentType.CONSTITUTIONAL_COMPLIANCE
        )
        self.judges[constitutional_judge.id] = constitutional_judge
    
    def file_case(
        self,
        judgment_type: JudgmentType,
        subject_id: str,
        scarindex_value: float,
        evidence: Dict,
        priority: JudgePriority = JudgePriority.MEDIUM
    ) -> JudicialCase:
        """
        File a new case for judicial review
        
        Args:
            judgment_type: Type of judgment required
            subject_id: ID of entity being judged
            scarindex_value: Current ScarIndex value
            evidence: Supporting evidence
            priority: Case priority
            
        Returns:
            Filed case
        """
        case = JudicialCase(
            judgment_type=judgment_type,
            subject_id=subject_id,
            scarindex_value=scarindex_value,
            evidence=evidence,
            priority=priority
        )
        
        self.cases[case.id] = case
        self.pending_cases.append(case.id)
        
        return case
    
    def assign_judge(self, case_id: str) -> Optional[Judge]:
        """
        Assign a judge to a case based on specialization
        
        Args:
            case_id: Case ID
            
        Returns:
            Assigned judge or None
        """
        if case_id not in self.cases:
            return None
        
        case = self.cases[case_id]
        
        # Find judge with matching specialization
        for judge in self.judges.values():
            if judge.specialization == case.judgment_type:
                return judge
        
        # Fallback to any available judge
        return list(self.judges.values())[0] if self.judges else None
    
    def review_case(self, case_id: str) -> Optional[JudicialCase]:
        """
        Review a case
        
        Args:
            case_id: Case ID
            
        Returns:
            Reviewed case or None
        """
        if case_id not in self.cases:
            return None
        
        case = self.cases[case_id]
        judge = self.assign_judge(case_id)
        
        if not judge:
            return None
        
        # Judge reviews case
        reviewed_case = judge.review_case(case)
        
        # Update case
        self.cases[case_id] = reviewed_case
        
        # Remove from pending
        if case_id in self.pending_cases:
            self.pending_cases.remove(case_id)
        
        return reviewed_case
    
    def review_all_pending(self) -> List[JudicialCase]:
        """Review all pending cases"""
        reviewed = []
        
        # Sort by priority
        pending_sorted = sorted(
            self.pending_cases,
            key=lambda cid: self.cases[cid].priority.value
        )
        
        for case_id in pending_sorted:
            case = self.review_case(case_id)
            if case:
                reviewed.append(case)
        
        return reviewed
    
    def get_system_status(self) -> Dict:
        """Get judicial system status"""
        total_cases = len(self.cases)
        pending = len(self.pending_cases)
        reviewed = total_cases - pending
        
        verdicts_by_type = {}
        for case in self.cases.values():
            if case.verdict:
                verdict_type = case.verdict.value
                verdicts_by_type[verdict_type] = verdicts_by_type.get(verdict_type, 0) + 1
        
        return {
            'total_judges': len(self.judges),
            'total_cases': total_cases,
            'pending_cases': pending,
            'reviewed_cases': reviewed,
            'verdicts_by_type': verdicts_by_type,
            'timestamp': datetime.utcnow().isoformat()
        }


# Example usage
def example_f2_judges():
    """Example of F2 Judges usage"""
    print("=" * 70)
    print("F2 Judges - Judicial Branch")
    print("=" * 70)
    print()
    
    system = JudicialSystem()
    
    # File crisis escalation case
    case1 = system.file_case(
        judgment_type=JudgmentType.CRISIS_ESCALATION,
        subject_id="panic_frame_001",
        scarindex_value=0.25,
        evidence={'panic_frame_id': 'panic_frame_001'},
        priority=JudgePriority.CRITICAL
    )
    
    print(f"Filed crisis escalation case: {case1.id}")
    print(f"  ScarIndex: {case1.scarindex_value}")
    print(f"  Priority: {case1.priority.value}")
    
    # Review case
    reviewed = system.review_case(case1.id)
    
    print(f"\nCase reviewed:")
    print(f"  Verdict: {reviewed.verdict.value}")
    print(f"  Reasoning: {reviewed.reasoning}")
    print(f"  Remediation required: {len(reviewed.remediation_required)} actions")
    for action in reviewed.remediation_required:
        print(f"    - {action}")
    
    # File lineage evaluation case
    case2 = system.file_case(
        judgment_type=JudgmentType.LINEAGE_EVALUATION,
        subject_id="holon_123",
        scarindex_value=0.7,
        evidence={'cmp': 0.25, 'residue_accumulated': 0.6, 'generation': 3},
        priority=JudgePriority.MEDIUM
    )
    
    print(f"\nFiled lineage evaluation case: {case2.id}")
    
    # Review all pending
    all_reviewed = system.review_all_pending()
    print(f"\nReviewed {len(all_reviewed)} pending cases")
    
    # System status
    status = system.get_system_status()
    print(f"\nJudicial System Status:")
    print(f"  Total Judges: {status['total_judges']}")
    print(f"  Total Cases: {status['total_cases']}")
    print(f"  Reviewed: {status['reviewed_cases']}")
    print(f"  Pending: {status['pending_cases']}")
    print(f"  Verdicts: {status['verdicts_by_type']}")


if __name__ == '__main__':
    example_f2_judges()

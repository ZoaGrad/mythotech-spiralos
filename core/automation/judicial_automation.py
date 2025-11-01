"""Judicial Automation Module.

This module automates the assignment of judges to cases based on:
- Judge availability and schedules
- Case complexity and type
- Workload distribution
- F2 Judge evaluation criteria

Usage:
    python -m core.automation.judicial_automation [--config CONFIG]

Environment Variables:
    SUPABASE_URL: Supabase project URL
    SUPABASE_KEY: Supabase API key
    LOG_LEVEL: Logging level (default: INFO)
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CaseType(Enum):
    """Enumeration of case types."""
    CRIMINAL = "criminal"
    CIVIL = "civil"
    FAMILY = "family"
    COMMERCIAL = "commercial"
    ADMINISTRATIVE = "administrative"


class CaseComplexity(Enum):
    """Enumeration of case complexity levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class JudgeStatus(Enum):
    """Enumeration of judge availability status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ON_LEAVE = "on_leave"
    RETIRED = "retired"


@dataclass
class Judge:
    """Data class representing a judge.
    
    Attributes:
        id: Unique judge identifier
        name: Judge full name
        experience_years: Years of legal experience
        specialties: List of case types the judge specializes in
        status: Current availability status
        workload: Current number of active cases
        max_workload: Maximum cases can handle
        f2_score: F2 Judge evaluation score (0-100)
    """
    id: str
    name: str
    experience_years: int
    specialties: List[str]
    status: JudgeStatus
    workload: int
    max_workload: int
    f2_score: float
    
    def is_available(self) -> bool:
        """Check if judge is available for new cases."""
        return (self.status == JudgeStatus.AVAILABLE and 
                self.workload < self.max_workload)
    
    def get_availability_percentage(self) -> float:
        """Get judge's current availability percentage."""
        if self.max_workload == 0:
            return 0.0
        return ((self.max_workload - self.workload) / self.max_workload) * 100


@dataclass
class Case:
    """Data class representing a case.
    
    Attributes:
        id: Unique case identifier
        case_type: Type of case (CaseType enum)
        complexity: Complexity level (CaseComplexity enum)
        filing_date: Date case was filed
        status: Current case status
        assigned_judge_id: ID of assigned judge (None if unassigned)
    """
    id: str
    case_type: CaseType
    complexity: CaseComplexity
    filing_date: datetime
    status: str
    assigned_judge_id: Optional[str] = None


class JudgeAssignmentEngine:
    """Engine for automated judge assignment to cases."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize the assignment engine.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.judges: List[Judge] = []
        self.cases: List[Case] = []
        logger.info("JudgeAssignmentEngine initialized")
    
    async def load_judges(self) -> List[Judge]:
        """Load judges from Supabase.
        
        Table: judges
        Required columns: id, name, experience_years, specialties, status, 
                         workload, max_workload, f2_score
        
        Returns:
            List of Judge objects
        """
        try:
            logger.info("Loading judges from Supabase...")
            # Placeholder for Supabase query
            # In production, this would query the 'judges' table
            # SELECT * FROM judges WHERE status != 'retired'
            self.judges = []
            logger.info(f"Loaded {len(self.judges)} judges")
            return self.judges
        except Exception as e:
            logger.error(f"Error loading judges: {str(e)}")
            raise
    
    async def load_unassigned_cases(self) -> List[Case]:
        """Load unassigned cases from Supabase.
        
        Table: cases
        Required columns: id, case_type, complexity, filing_date, status, 
                         assigned_judge_id
        
        Returns:
            List of unassigned Case objects
        """
        try:
            logger.info("Loading unassigned cases from Supabase...")
            # Placeholder for Supabase query
            # SELECT * FROM cases WHERE assigned_judge_id IS NULL AND status != 'closed'
            self.cases = []
            logger.info(f"Loaded {len(self.cases)} unassigned cases")
            return self.cases
        except Exception as e:
            logger.error(f"Error loading unassigned cases: {str(e)}")
            raise
    
    def calculate_assignment_score(self, judge: Judge, case: Case) -> float:
        """Calculate score for assigning judge to case.
        
        Score is based on:
        - Judge specialization match (40%)
        - Workload balance (30%)
        - Experience level (20%)
        - F2 Judge score (10%)
        
        Args:
            judge: Judge object
            case: Case object
            
        Returns:
            Assignment score (0-100)
        """
        score = 0.0
        
        # Specialization match (40%)
        specialty_score = 0.0
        if case.case_type.value in judge.specialties:
            specialty_score = 100.0
        elif len(judge.specialties) > 0:
            specialty_score = 50.0  # Partial credit for general experience
        
        score += specialty_score * 0.40
        
        # Workload balance (30%)
        workload_score = judge.get_availability_percentage()
        score += workload_score * 0.30
        
        # Experience level (20%)
        experience_score = min((judge.experience_years / 30) * 100, 100)
        score += experience_score * 0.20
        
        # F2 Judge score (10%)
        score += judge.f2_score * 0.10
        
        return score
    
    def find_best_judge_for_case(self, case: Case) -> Optional[Judge]:
        """Find the best judge for a specific case.
        
        Args:
            case: Case object
            
        Returns:
            Best matching Judge object or None if no suitable judge found
        """
        available_judges = [j for j in self.judges if j.is_available()]
        
        if not available_judges:
            logger.warning(f"No available judges for case {case.id}")
            return None
        
        # Calculate scores for all available judges
        judge_scores = [(judge, self.calculate_assignment_score(judge, case)) 
                       for judge in available_judges]
        
        # Sort by score (descending)
        judge_scores.sort(key=lambda x: x[1], reverse=True)
        
        best_judge = judge_scores[0][0]
        best_score = judge_scores[0][1]
        
        logger.info(f"Best judge for case {case.id}: {best_judge.name} "
                   f"(score: {best_score:.2f})")
        
        return best_judge
    
    async def assign_judges_to_cases(self) -> Dict[str, str]:
        """Assign judges to unassigned cases.
        
        Returns:
            Dictionary mapping case IDs to assigned judge IDs
        """
        logger.info("Starting judicial assignment process...")
        
        await self.load_judges()
        await self.load_unassigned_cases()
        
        assignments = {}
        
        for case in self.cases:
            best_judge = self.find_best_judge_for_case(case)
            
            if best_judge:
                assignments[case.id] = best_judge.id
                # Update judge workload
                best_judge.workload += 1
                logger.info(f"Assigned judge {best_judge.name} to case {case.id}")
            else:
                logger.warning(f"Could not assign judge to case {case.id}")
        
        # Update assignments in Supabase
        await self.update_case_assignments(assignments)
        
        logger.info(f"Assignment process completed. Assigned {len(assignments)} cases.")
        return assignments
    
    async def update_case_assignments(self, assignments: Dict[str, str]) -> bool:
        """Update case assignments in Supabase.
        
        Table: cases
        Updates: assigned_judge_id column for each case
        
        Args:
            assignments: Dictionary mapping case IDs to judge IDs
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            logger.info(f"Updating {len(assignments)} case assignments in Supabase...")
            # Placeholder for Supabase update
            # for case_id, judge_id in assignments.items():
            #     UPDATE cases SET assigned_judge_id = judge_id WHERE id = case_id
            logger.info("Case assignments updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating case assignments: {str(e)}")
            return False
    
    async def generate_assignment_report(self, assignments: Dict[str, str]) -> Dict:
        """Generate a report of the assignment process.
        
        Returns:
            Dictionary containing assignment statistics and details
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_cases_assigned": len(assignments),
            "total_judges": len(self.judges),
            "available_judges": len([j for j in self.judges if j.is_available()]),
            "assignments": assignments,
            "judge_workload_summary": {
                judge.id: {
                    "name": judge.name,
                    "workload": judge.workload,
                    "max_workload": judge.max_workload,
                    "availability_percent": judge.get_availability_percentage()
                }
                for judge in self.judges
            }
        }
        return report


async def main():
    """Main entry point for judicial automation."""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            logger.error("Missing required environment variables: "
                        "SUPABASE_URL, SUPABASE_KEY")
            return False
        
        engine = JudgeAssignmentEngine(supabase_url, supabase_key)
        assignments = await engine.assign_judges_to_cases()
        report = await engine.generate_assignment_report(assignments)
        
        logger.info(f"Judicial automation completed: {json.dumps(report, indent=2)}")
        return True
        
    except Exception as e:
        logger.error(f"Judicial automation failed: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

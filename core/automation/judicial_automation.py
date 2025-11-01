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
from supabase import create_client
import sys

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

class JudgeStatus(Enum):
    """Enumeration of judge availability statuses."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ON_LEAVE = "on_leave"
    RETIRED = "retired"

@dataclass
class Judge:
    """Judge record data class."""
    id: str
    name: str
    status: str
    specialization: List[str]
    current_workload: int
    f2_score: float
    availability_start: Optional[str] = None
    availability_end: Optional[str] = None

@dataclass
class Case:
    """Case record data class."""
    id: str
    case_number: str
    case_type: str
    complexity: int
    filing_date: str
    assigned_judge_id: Optional[str] = None
    status: str = "pending"

class JudicialAutomation:
    """Main judicial automation engine."""

    def __init__(self):
        """Initialize Supabase client and validation."""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            logger.error(
                'SUPABASE_URL and SUPABASE_KEY environment variables are required.'
            )
            sys.exit(1)
        
        try:
            self.supabase = create_client(
                self.supabase_url,
                self.supabase_key
            )
            logger.info('Supabase client initialized successfully')
        except Exception as e:
            logger.error(f'Failed to initialize Supabase client: {e}')
            sys.exit(1)

    async def fetch_available_judges(self) -> List[Judge]:
        """Fetch all available judges from Supabase.
        
        Returns:
            List of Judge objects with available judges
        """
        try:
            response = self.supabase.table('judges').select(
                'id, name, status, specialization, current_workload, f2_score, availability_start, availability_end'
            ).eq('status', 'available').execute()
            
            judges = []
            for judge_data in response.data:
                judge = Judge(
                    id=judge_data['id'],
                    name=judge_data['name'],
                    status=judge_data['status'],
                    specialization=judge_data.get('specialization', []),
                    current_workload=judge_data.get('current_workload', 0),
                    f2_score=judge_data.get('f2_score', 0.0),
                    availability_start=judge_data.get('availability_start'),
                    availability_end=judge_data.get('availability_end')
                )
                judges.append(judge)
            
            logger.info(f'Fetched {len(judges)} available judges')
            return judges
        except Exception as e:
            logger.error(f'Error fetching available judges: {e}')
            return []

    async def fetch_pending_cases(self) -> List[Case]:
        """Fetch all pending cases from Supabase.
        
        Returns:
            List of Case objects with pending cases
        """
        try:
            response = self.supabase.table('cases').select(
                'id, case_number, case_type, complexity, filing_date, assigned_judge_id, status'
            ).eq('status', 'pending').execute()
            
            cases = []
            for case_data in response.data:
                case = Case(
                    id=case_data['id'],
                    case_number=case_data['case_number'],
                    case_type=case_data['case_type'],
                    complexity=case_data.get('complexity', 1),
                    filing_date=case_data['filing_date'],
                    assigned_judge_id=case_data.get('assigned_judge_id'),
                    status=case_data.get('status', 'pending')
                )
                cases.append(case)
            
            logger.info(f'Fetched {len(cases)} pending cases')
            return cases
        except Exception as e:
            logger.error(f'Error fetching pending cases: {e}')
            return []

    def calculate_judge_score(self, judge: Judge, case: Case) -> float:
        """Calculate suitability score for judge-case assignment.
        
        Scoring criteria:
        - F2 Judge score (40%): Inherent judge quality
        - Workload balance (30%): Lower workload is better
        - Specialization match (20%): Match case type to judge specialization
        - Availability (10%): Current availability status
        
        Args:
            judge: Judge object
            case: Case object
            
        Returns:
            Composite suitability score (0-100)
        """
        score = 0.0
        
        # F2 Score component (40%)
        f2_component = (judge.f2_score / 100.0) * 40.0
        score += f2_component
        
        # Workload balance component (30%)
        # Assuming max workload of 20 cases
        workload_ratio = judge.current_workload / 20.0
        workload_component = (1.0 - workload_ratio) * 30.0
        score += max(0, workload_component)
        
        # Specialization match component (20%)
        specialization_match = 0.0
        if case.case_type in judge.specialization:
            specialization_match = 20.0
        elif len(judge.specialization) > 0:
            specialization_match = 10.0  # Partial credit for general judges
        score += specialization_match
        
        # Availability component (10%)
        if judge.status == 'available':
            score += 10.0
        
        return min(score, 100.0)

    async def assign_cases_to_judges(self, judges: List[Judge], cases: List[Case]) -> Dict[str, str]:
        """Assign cases to judges using optimal matching algorithm.
        
        Args:
            judges: List of available judges
            cases: List of pending cases
            
        Returns:
            Dictionary mapping case_id to assigned judge_id
        """
        assignments = {}
        
        if not judges or not cases:
            logger.warning('Insufficient judges or cases for assignment')
            return assignments
        
        # Sort judges by F2 score and workload
        sorted_judges = sorted(
            judges,
            key=lambda j: (-j.f2_score, j.current_workload)
        )
        
        # Sort cases by complexity (harder cases first)
        sorted_cases = sorted(cases, key=lambda c: -c.complexity)
        
        # Assign cases to judges
        for case in sorted_cases:
            best_judge = None
            best_score = -1
            
            for judge in sorted_judges:
                score = self.calculate_judge_score(judge, case)
                if score > best_score:
                    best_score = score
                    best_judge = judge
            
            if best_judge and best_score > 0:
                assignments[case.id] = best_judge.id
                # Update judge's workload
                best_judge.current_workload += 1
                logger.info(
                    f'Assigned case {case.case_number} '
                    f'(complexity: {case.complexity}) '
                    f'to judge {best_judge.name} '
                    f'(score: {best_score:.2f})'
                )
            else:
                logger.warning(f'Could not find suitable judge for case {case.case_number}')
        
        return assignments

    async def persist_assignments(self, assignments: Dict[str, str]) -> bool:
        """Persist judge assignments to Supabase.
        
        Args:
            assignments: Dictionary mapping case_id to judge_id
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for case_id, judge_id in assignments.items():
                # Update case with assigned judge
                self.supabase.table('cases').update({
                    'assigned_judge_id': judge_id,
                    'status': 'assigned',
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', case_id).execute()
                
                # Update judge workload
                judge_response = self.supabase.table('judges').select(
                    'current_workload'
                ).eq('id', judge_id).execute()
                
                if judge_response.data:
                    current_workload = judge_response.data[0]['current_workload']
                    self.supabase.table('judges').update({
                        'current_workload': current_workload + 1,
                        'updated_at': datetime.utcnow().isoformat()
                    }).eq('id', judge_id).execute()
            
            logger.info(f'Persisted {len(assignments)} case assignments')
            return True
        except Exception as e:
            logger.error(f'Error persisting assignments: {e}')
            return False

    async def run(self):
        """Execute the main judicial automation workflow."""
        try:
            logger.info('Starting judicial automation workflow...')
            
            # Fetch available judges and pending cases
            judges = await self.fetch_available_judges()
            cases = await self.fetch_pending_cases()
            
            if not judges:
                logger.warning('No available judges found')
                return
            
            if not cases:
                logger.info('No pending cases found')
                return
            
            # Assign cases to judges
            assignments = await self.assign_cases_to_judges(judges, cases)
            
            # Persist assignments
            if assignments:
                success = await self.persist_assignments(assignments)
                if success:
                    logger.info(
                        f'Successfully completed judicial automation. '
                        f'Assigned {len(assignments)} cases to judges.'
                    )
                else:
                    logger.error('Failed to persist assignments')
            else:
                logger.warning('No assignments generated')
                
        except Exception as e:
            logger.error(f'Error during judicial automation: {e}')
            raise

async def main():
    """Entry point for the judicial automation module."""
    automation = JudicialAutomation()
    await automation.run()

if __name__ == '__main__':
    asyncio.run(main())

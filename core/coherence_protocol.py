"""
Distributed Coherence Protocol - Cryptographic Output Verification (COV)

Mitigates the Centralization Paradox of the Agent Fusion Stack (C7) by implementing
a multi-provider consensus protocol requiring cryptographic output verification
for critical ScarIndex scoring.

Component Flow:
1. C7 (LLMs) performs semantic analysis (GoT) on Ache input
2. C7 generates ScarIndex score + Cryptographic Signature
3. Multi-provider Consensus: System requires 2-of-3 consensus (SHA Checksum Verification)
4. Ledger Anchor: Final verified state commits to Smart Contracts (C2) and Supabase (C6)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import hashlib
import json
from datetime import datetime
import uuid
import asyncio
from openai import OpenAI
import os


class LLMProvider(Enum):
    """Supported LLM providers for consensus"""
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1_NANO = "gpt-4.1-nano"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    CLAUDE_SONNET_4 = "claude-sonnet-4"


@dataclass
class ProviderOutput:
    """Output from a single LLM provider"""
    provider: LLMProvider
    instance: int
    output: Dict
    output_hash: str
    signature: str
    timestamp: datetime
    
    @classmethod
    def create(
        cls,
        provider: LLMProvider,
        instance: int,
        output: Dict
    ) -> 'ProviderOutput':
        """Create a provider output with cryptographic signature"""
        # Serialize output deterministically
        output_json = json.dumps(output, sort_keys=True)
        
        # Calculate SHA-256 hash
        output_hash = hashlib.sha256(output_json.encode()).hexdigest()
        
        # Create signature (in production, use proper cryptographic signing)
        signature_data = f"{provider.value}:{instance}:{output_hash}:{datetime.utcnow().isoformat()}"
        signature = hashlib.sha256(signature_data.encode()).hexdigest()
        
        return cls(
            provider=provider,
            instance=instance,
            output=output,
            output_hash=output_hash,
            signature=signature,
            timestamp=datetime.utcnow()
        )


@dataclass
class ConsensusResult:
    """Result of multi-provider consensus verification"""
    consensus_group: str
    achieved: bool
    provider_count: int
    consensus_count: int
    outputs: List[ProviderOutput]
    final_output: Optional[Dict]
    verification_hashes: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            'consensus_group': self.consensus_group,
            'consensus_achieved': self.achieved,
            'provider_count': self.provider_count,
            'consensus_count': self.consensus_count,
            'verification_hashes': self.verification_hashes,
            'final_output': self.final_output
        }


class DistributedCoherenceProtocol:
    """
    Implements the Cryptographic Output Verification (COV) protocol
    
    Uses multi-provider consensus (2-of-3) to ensure distributed coherence
    and mitigate the centralization risk of relying on commercial LLMs.
    """
    
    def __init__(self, consensus_threshold: int = 2, total_providers: int = 3):
        """
        Initialize the protocol
        
        Args:
            consensus_threshold: Number of providers that must agree (default: 2)
            total_providers: Total number of providers to query (default: 3)
        """
        self.consensus_threshold = consensus_threshold
        self.total_providers = total_providers
        self.openai_client = OpenAI()  # API key pre-configured in environment
        
        # Initialize Anthropic client if API key is available
        try:
            # Import anthropic only if needed to avoid hard dependency
            from anthropic import Anthropic
            self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        except (ImportError, Exception):
            # If anthropic package not installed or API key not set, set to None
            # Claude Sonnet 4 will fail gracefully if selected
            self.anthropic_client = None
    
    async def analyze_ache_with_provider(
        self,
        provider: LLMProvider,
        instance: int,
        ache_content: Dict,
        system_prompt: str
    ) -> ProviderOutput:
        """
        Analyze Ache content with a single provider instance
        
        Args:
            provider: LLM provider to use
            instance: Instance number for this provider
            ache_content: Raw Ache content to analyze
            system_prompt: System prompt for semantic analysis
            
        Returns:
            ProviderOutput with analysis results
        """
        # Prepare the analysis prompt
        user_prompt = f"""
Analyze the following Ache (entropy/non-coherence) content and calculate coherence scores:

{json.dumps(ache_content, indent=2)}

Provide a JSON response with:
- c_narrative: Narrative coherence (0-1)
- c_social: Social coherence (0-1)
- c_economic: Economic coherence (0-1)
- c_technical: Technical coherence (0-1)
- ache_after: Estimated Ache level after processing (0-1)
- reasoning: Brief explanation of the scores
"""
        
        # Call the appropriate LLM based on provider
        if provider == LLMProvider.CLAUDE_SONNET_4:
            # Use Anthropic API
            if self.anthropic_client is None:
                raise ValueError("Anthropic client not initialized. Install anthropic package and set ANTHROPIC_API_KEY.")
            
            # For Anthropic, we need to explicitly request JSON in the prompt
            anthropic_user_prompt = user_prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. Do not include any explanation or text outside the JSON object."
            
            response = self.anthropic_client.messages.create(
                model=provider.value,
                max_tokens=1024,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": anthropic_user_prompt}
                ]
            )
            
            # Parse the Anthropic response with error handling
            output_text = response.content[0].text
            try:
                output = json.loads(output_text)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, try to extract JSON from the response
                # This handles cases where the model includes extra text
                import re
                json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
                if json_match:
                    output = json.loads(json_match.group())
                else:
                    raise ValueError(f"Failed to parse JSON from Anthropic response: {output_text[:200]}...") from e
        else:
            # Use OpenAI API for all other providers
            response = self.openai_client.chat.completions.create(
                model=provider.value,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistency
                response_format={"type": "json_object"}
            )
            
            # Parse the OpenAI response
            output = json.loads(response.choices[0].message.content)
        
        # Create and return provider output
        return ProviderOutput.create(
            provider=provider,
            instance=instance,
            output=output
        )
    
    async def verify_consensus(
        self,
        ache_content: Dict,
        ache_before: float,
        system_prompt: Optional[str] = None
    ) -> ConsensusResult:
        """
        Verify consensus across multiple providers
        
        Args:
            ache_content: Raw Ache content to analyze
            ache_before: Ache level before processing
            system_prompt: Optional custom system prompt
            
        Returns:
            ConsensusResult with verification outcome
        """
        if system_prompt is None:
            system_prompt = """You are the ScarIndex Oracle, responsible for measuring 
system coherence across multiple dimensions. Analyze the input carefully and provide 
accurate coherence scores based on narrative structure, social dynamics, economic 
viability, and technical soundness."""
        
        # Select providers for this consensus round
        providers = [
            LLMProvider.GPT_4_1_MINI,
            LLMProvider.GPT_4_1_NANO,
            LLMProvider.GEMINI_2_5_FLASH,
            LLMProvider.CLAUDE_SONNET_4
        ][:self.total_providers]
        
        # Query all providers in parallel
        tasks = [
            self.analyze_ache_with_provider(
                provider=provider,
                instance=i,
                ache_content=ache_content,
                system_prompt=system_prompt
            )
            for i, provider in enumerate(providers)
        ]
        
        outputs = await asyncio.gather(*tasks)
        
        # Group outputs by hash to find consensus
        hash_groups: Dict[str, List[ProviderOutput]] = {}
        for output in outputs:
            hash_key = output.output_hash
            if hash_key not in hash_groups:
                hash_groups[hash_key] = []
            hash_groups[hash_key].append(output)
        
        # Find the largest consensus group
        consensus_group_hash = max(hash_groups.keys(), key=lambda k: len(hash_groups[k]))
        consensus_outputs = hash_groups[consensus_group_hash]
        consensus_count = len(consensus_outputs)
        
        # Check if consensus threshold is met
        consensus_achieved = consensus_count >= self.consensus_threshold
        
        # Use the consensus output if achieved, otherwise None
        final_output = consensus_outputs[0].output if consensus_achieved else None
        
        # Create consensus result
        consensus_group_id = str(uuid.uuid4())
        
        return ConsensusResult(
            consensus_group=consensus_group_id,
            achieved=consensus_achieved,
            provider_count=len(outputs),
            consensus_count=consensus_count,
            outputs=outputs,
            final_output=final_output,
            verification_hashes=[output.output_hash for output in outputs]
        )
    
    def calculate_checksum_consensus(
        self,
        outputs: List[ProviderOutput]
    ) -> Tuple[bool, str]:
        """
        Calculate 2-of-3 checksum consensus
        
        Args:
            outputs: List of provider outputs
            
        Returns:
            (consensus_achieved, consensus_hash)
        """
        # Count hash occurrences
        hash_counts: Dict[str, int] = {}
        for output in outputs:
            hash_counts[output.output_hash] = hash_counts.get(output.output_hash, 0) + 1
        
        # Find the most common hash
        consensus_hash = max(hash_counts.keys(), key=lambda k: hash_counts[k])
        consensus_count = hash_counts[consensus_hash]
        
        # Check if threshold is met
        consensus_achieved = consensus_count >= self.consensus_threshold
        
        return consensus_achieved, consensus_hash
    
    def create_verification_records(
        self,
        consensus_result: ConsensusResult,
        scarindex_id: str
    ) -> List[Dict]:
        """
        Create verification records for database storage
        
        Args:
            consensus_result: Result of consensus verification
            scarindex_id: ID of the associated ScarIndex calculation
            
        Returns:
            List of verification record dictionaries
        """
        records = []
        
        for output in consensus_result.outputs:
            record = {
                'id': str(uuid.uuid4()),
                'created_at': output.timestamp.isoformat(),
                'scarindex_id': scarindex_id,
                'provider': output.provider.value,
                'provider_instance': output.instance,
                'output_hash': output.output_hash,
                'signature': output.signature,
                'consensus_group': consensus_result.consensus_group,
                'consensus_achieved': consensus_result.achieved,
                'metadata': {
                    'output': output.output,
                    'timestamp': output.timestamp.isoformat()
                }
            }
            records.append(record)
        
        return records


class AgentFusionStack:
    """
    Agent Fusion Stack (C7) - LLM-based semantic analysis
    
    Integrates with the Distributed Coherence Protocol to provide
    cryptographically verified ScarIndex calculations using multiple
    commercial LLM providers.
    """
    
    def __init__(self):
        self.protocol = DistributedCoherenceProtocol()
    
    async def analyze_and_verify(
        self,
        ache_content: Dict,
        ache_before: float
    ) -> Tuple[Optional[Dict], ConsensusResult]:
        """
        Analyze Ache content with consensus verification
        
        Args:
            ache_content: Raw Ache content to analyze
            ache_before: Ache level before processing
            
        Returns:
            (coherence_scores, consensus_result)
        """
        consensus_result = await self.protocol.verify_consensus(
            ache_content=ache_content,
            ache_before=ache_before
        )
        
        if consensus_result.achieved:
            return consensus_result.final_output, consensus_result
        else:
            return None, consensus_result
    
    def graph_of_thought_analysis(
        self,
        ache_content: Dict,
        ontology_constraints: Dict
    ) -> Dict:
        """
        Perform Graph-of-Thought (GoT) semantic analysis
        
        This ensures semantic integrity during recursion via
        compiler-in-the-loop reflection and auto-formalization.
        
        Args:
            ache_content: Raw Ache content
            ontology_constraints: ZoaGrad Ontology constraints
            
        Returns:
            GoT analysis results
        """
        # Placeholder for full GoT implementation
        # In production, this would use the ARIA pipeline
        return {
            'semantic_graph': {},
            'ontology_compliance': True,
            'drift_score': 0.0,
            'timestamp': datetime.utcnow().isoformat()
        }


# Example usage
async def example_consensus_verification():
    """Example of running consensus verification"""
    protocol = DistributedCoherenceProtocol()
    
    # Example Ache content
    ache_content = {
        'source': 'user_input',
        'content': 'A proposal for a new feature that improves system coherence',
        'context': {
            'narrative': 'Enhances the user story flow',
            'social': 'Increases community engagement',
            'economic': 'Reduces operational costs',
            'technical': 'Implements best practices'
        }
    }
    
    # Run consensus verification
    result = await protocol.verify_consensus(
        ache_content=ache_content,
        ache_before=0.7
    )
    
    print(f"Consensus achieved: {result.achieved}")
    print(f"Provider count: {result.provider_count}")
    print(f"Consensus count: {result.consensus_count}")
    
    if result.final_output:
        print(f"Final output: {json.dumps(result.final_output, indent=2)}")
    
    return result


if __name__ == '__main__':
    # Run example
    asyncio.run(example_consensus_verification())

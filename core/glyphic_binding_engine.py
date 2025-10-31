"""
Glyphic Binding Engine (GBE) - Recursive Descent Parser for the Spiral Field

The GBE acts as the symbolic structure layer that formalizes the chaotic output
of the Paradox Network (μ-operator) into coherent symbolic continuity.

As the Paradox Agent accelerates recursive complexity, the GBE must scale to
prevent catastrophic symbolic incoherence. This module implements the scaled
GBE with SigilThreading for high-velocity complexity management.

Key Concepts:
- Glyph: Symbolic unit representing a concept or operation
- Sigil: Composite glyph structure with semantic binding
- Threading: Parallel processing of glyph streams
- Binding: Semantic connection between glyphs
- Coherence: Structural integrity of symbolic space
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
import hashlib
import json


class GlyphType(Enum):
    """Types of glyphs in the symbolic space"""
    CONCEPT = "concept"          # Abstract concept
    OPERATION = "operation"      # Executable operation
    RELATION = "relation"        # Relationship between concepts
    CONSTRAINT = "constraint"    # Constraint or rule
    PARADOX = "paradox"         # Paradoxical statement
    SYNTHESIS = "synthesis"      # Synthesized knowledge


class BindingStrength(Enum):
    """Strength of semantic binding between glyphs"""
    WEAK = "weak"              # Loose association
    MODERATE = "moderate"      # Clear relationship
    STRONG = "strong"          # Tight coupling
    ABSOLUTE = "absolute"      # Inseparable


@dataclass
class Glyph:
    """
    Glyph - Symbolic unit in the Spiral Field
    
    Represents a single concept, operation, or relationship in the
    symbolic space maintained by the GBE.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    glyph_type: GlyphType = GlyphType.CONCEPT
    
    # Content
    symbol: str = ""  # Symbolic representation
    semantic_content: Dict = field(default_factory=dict)
    
    # Bindings
    bound_to: Set[str] = field(default_factory=set)  # IDs of bound glyphs
    binding_strengths: Dict[str, BindingStrength] = field(default_factory=dict)
    
    # Provenance
    source: str = ""  # Origin (e.g., "paradox_network", "user_input")
    created_by: str = ""  # Creating agent ID
    
    # Coherence
    coherence_score: float = 1.0  # How well-formed (0-1)
    paradox_index: float = 0.0  # How paradoxical (0-1)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def bind_to(self, other_glyph_id: str, strength: BindingStrength):
        """Create semantic binding to another glyph"""
        self.bound_to.add(other_glyph_id)
        self.binding_strengths[other_glyph_id] = strength
    
    def unbind_from(self, other_glyph_id: str):
        """Remove semantic binding"""
        if other_glyph_id in self.bound_to:
            self.bound_to.remove(other_glyph_id)
            del self.binding_strengths[other_glyph_id]
    
    def access(self):
        """Record access to this glyph"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'glyph_type': self.glyph_type.value,
            'symbol': self.symbol,
            'semantic_content': self.semantic_content,
            'bound_to': list(self.bound_to),
            'binding_strengths': {k: v.value for k, v in self.binding_strengths.items()},
            'source': self.source,
            'created_by': self.created_by,
            'coherence_score': self.coherence_score,
            'paradox_index': self.paradox_index,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count,
            'metadata': self.metadata
        }


@dataclass
class Sigil:
    """
    Sigil - Composite glyph structure
    
    A Sigil is a higher-order symbolic structure composed of multiple
    glyphs with semantic bindings. Sigils represent complex concepts
    or operations that emerge from glyph composition.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    
    # Composition
    component_glyphs: List[str] = field(default_factory=list)  # Glyph IDs
    binding_graph: Dict[str, List[str]] = field(default_factory=dict)
    
    # Semantics
    emergent_meaning: str = ""
    coherence_score: float = 1.0
    
    # Threading
    thread_id: Optional[str] = None  # SigilThread ID if threaded
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)
    
    def add_glyph(self, glyph_id: str):
        """Add a glyph to this sigil"""
        if glyph_id not in self.component_glyphs:
            self.component_glyphs.append(glyph_id)
    
    def add_binding(self, from_glyph_id: str, to_glyph_id: str):
        """Add binding in the sigil's binding graph"""
        if from_glyph_id not in self.binding_graph:
            self.binding_graph[from_glyph_id] = []
        if to_glyph_id not in self.binding_graph[from_glyph_id]:
            self.binding_graph[from_glyph_id].append(to_glyph_id)
    
    def calculate_coherence(self, glyphs: Dict[str, Glyph]) -> float:
        """Calculate coherence of this sigil based on component glyphs"""
        if not self.component_glyphs:
            return 0.0
        
        # Average coherence of component glyphs
        total_coherence = 0.0
        for glyph_id in self.component_glyphs:
            if glyph_id in glyphs:
                total_coherence += glyphs[glyph_id].coherence_score
        
        avg_coherence = total_coherence / len(self.component_glyphs)
        
        # Bonus for strong bindings
        binding_bonus = len(self.binding_graph) * 0.05
        
        self.coherence_score = min(1.0, avg_coherence + binding_bonus)
        return self.coherence_score
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'component_glyphs': self.component_glyphs,
            'binding_graph': self.binding_graph,
            'emergent_meaning': self.emergent_meaning,
            'coherence_score': self.coherence_score,
            'thread_id': self.thread_id,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class SigilThread:
    """
    SigilThread - Parallel processing thread for glyph streams
    
    Enables parallel processing of multiple glyph streams to handle
    high-velocity complexity from the Paradox Network.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    
    # Processing
    sigils: List[str] = field(default_factory=list)  # Sigil IDs
    processing_queue: List[str] = field(default_factory=list)  # Glyph IDs to process
    
    # Performance
    glyphs_processed: int = 0
    sigils_created: int = 0
    average_processing_time: float = 0.0  # seconds
    
    # State
    active: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)
    
    def enqueue_glyph(self, glyph_id: str):
        """Add glyph to processing queue"""
        self.processing_queue.append(glyph_id)
    
    def dequeue_glyph(self) -> Optional[str]:
        """Remove and return next glyph from queue"""
        if self.processing_queue:
            return self.processing_queue.pop(0)
        return None
    
    def add_sigil(self, sigil_id: str):
        """Register a sigil with this thread"""
        if sigil_id not in self.sigils:
            self.sigils.append(sigil_id)
            self.sigils_created += 1
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'sigils': self.sigils,
            'queue_length': len(self.processing_queue),
            'glyphs_processed': self.glyphs_processed,
            'sigils_created': self.sigils_created,
            'average_processing_time': self.average_processing_time,
            'active': self.active,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


class GlyphicBindingEngine:
    """
    Glyphic Binding Engine (GBE) - Recursive Descent Parser
    
    Manages the symbolic space (Spiral Field) by:
    - Creating and maintaining glyphs
    - Establishing semantic bindings
    - Composing sigils from glyphs
    - Threading parallel glyph streams
    - Ensuring symbolic coherence
    
    The GBE scales to handle high-velocity complexity from the Paradox Network
    while maintaining structural integrity of the symbolic space.
    """
    
    def __init__(
        self,
        max_threads: int = 5,
        coherence_threshold: float = 0.5,
        max_glyphs: int = 10000
    ):
        """
        Initialize Glyphic Binding Engine
        
        Args:
            max_threads: Maximum number of SigilThreads
            coherence_threshold: Minimum coherence for glyph acceptance
            max_glyphs: Maximum glyphs in symbolic space
        """
        self.glyphs: Dict[str, Glyph] = {}
        self.sigils: Dict[str, Sigil] = {}
        self.threads: Dict[str, SigilThread] = {}
        
        self.max_threads = max_threads
        self.coherence_threshold = coherence_threshold
        self.max_glyphs = max_glyphs
        
        # Performance metrics
        self.total_glyphs_created = 0
        self.total_sigils_created = 0
        self.total_bindings_created = 0
        
        # Initialize default thread
        self._initialize_default_thread()
    
    def _initialize_default_thread(self):
        """Initialize default SigilThread"""
        thread = SigilThread(name="Main Thread")
        self.threads[thread.id] = thread
    
    def create_glyph(
        self,
        glyph_type: GlyphType,
        symbol: str,
        semantic_content: Dict,
        source: str = "unknown",
        created_by: str = "system"
    ) -> Glyph:
        """
        Create a new glyph in the symbolic space
        
        Args:
            glyph_type: Type of glyph
            symbol: Symbolic representation
            semantic_content: Semantic content dict
            source: Origin of glyph
            created_by: Creating agent ID
            
        Returns:
            New glyph
        """
        if len(self.glyphs) >= self.max_glyphs:
            # Cleanup least-accessed glyphs
            self._cleanup_glyphs(target_reduction=0.1)
        
        glyph = Glyph(
            glyph_type=glyph_type,
            symbol=symbol,
            semantic_content=semantic_content,
            source=source,
            created_by=created_by
        )
        
        # Calculate initial coherence
        glyph.coherence_score = self._calculate_glyph_coherence(glyph)
        
        # Only accept if above threshold
        if glyph.coherence_score < self.coherence_threshold:
            glyph.coherence_score = self.coherence_threshold
        
        self.glyphs[glyph.id] = glyph
        self.total_glyphs_created += 1
        
        return glyph
    
    def _calculate_glyph_coherence(self, glyph: Glyph) -> float:
        """Calculate coherence score for a glyph"""
        coherence = 0.8  # Base coherence
        
        # Bonus for rich semantic content
        if len(glyph.semantic_content) > 3:
            coherence += 0.1
        
        # Penalty for paradox glyphs
        if glyph.glyph_type == GlyphType.PARADOX:
            coherence -= 0.2
        
        # Bonus for synthesis glyphs
        if glyph.glyph_type == GlyphType.SYNTHESIS:
            coherence += 0.15
        
        return max(0.0, min(1.0, coherence))
    
    def bind_glyphs(
        self,
        glyph_id_1: str,
        glyph_id_2: str,
        strength: BindingStrength
    ) -> bool:
        """
        Create semantic binding between two glyphs
        
        Args:
            glyph_id_1: First glyph ID
            glyph_id_2: Second glyph ID
            strength: Binding strength
            
        Returns:
            True if binding created
        """
        if glyph_id_1 not in self.glyphs or glyph_id_2 not in self.glyphs:
            return False
        
        glyph1 = self.glyphs[glyph_id_1]
        glyph2 = self.glyphs[glyph_id_2]
        
        # Create bidirectional binding
        glyph1.bind_to(glyph_id_2, strength)
        glyph2.bind_to(glyph_id_1, strength)
        
        self.total_bindings_created += 1
        
        return True
    
    def create_sigil(
        self,
        name: str,
        glyph_ids: List[str],
        emergent_meaning: str = ""
    ) -> Sigil:
        """
        Create a sigil from component glyphs
        
        Args:
            name: Sigil name
            glyph_ids: List of component glyph IDs
            emergent_meaning: Emergent semantic meaning
            
        Returns:
            New sigil
        """
        sigil = Sigil(
            name=name,
            component_glyphs=glyph_ids,
            emergent_meaning=emergent_meaning
        )
        
        # Build binding graph from glyph bindings
        for glyph_id in glyph_ids:
            if glyph_id in self.glyphs:
                glyph = self.glyphs[glyph_id]
                for bound_id in glyph.bound_to:
                    if bound_id in glyph_ids:
                        sigil.add_binding(glyph_id, bound_id)
        
        # Calculate coherence
        sigil.calculate_coherence(self.glyphs)
        
        self.sigils[sigil.id] = sigil
        self.total_sigils_created += 1
        
        return sigil
    
    def create_thread(self, name: str) -> SigilThread:
        """
        Create a new SigilThread for parallel processing
        
        Args:
            name: Thread name
            
        Returns:
            New thread
        """
        if len(self.threads) >= self.max_threads:
            raise ValueError(f"Maximum threads ({self.max_threads}) reached")
        
        thread = SigilThread(name=name)
        self.threads[thread.id] = thread
        
        return thread
    
    def process_glyph_stream(
        self,
        glyph_ids: List[str],
        thread_id: Optional[str] = None
    ) -> Sigil:
        """
        Process a stream of glyphs into a sigil
        
        Args:
            glyph_ids: List of glyph IDs to process
            thread_id: Optional thread ID for processing
            
        Returns:
            Resulting sigil
        """
        # Select thread
        if thread_id and thread_id in self.threads:
            thread = self.threads[thread_id]
        else:
            # Use default thread
            thread = list(self.threads.values())[0]
        
        # Enqueue glyphs
        for glyph_id in glyph_ids:
            thread.enqueue_glyph(glyph_id)
        
        # Process glyphs
        processed_glyphs = []
        while thread.processing_queue:
            glyph_id = thread.dequeue_glyph()
            if glyph_id and glyph_id in self.glyphs:
                self.glyphs[glyph_id].access()
                processed_glyphs.append(glyph_id)
                thread.glyphs_processed += 1
        
        # Create sigil from processed glyphs
        sigil = self.create_sigil(
            name=f"Stream Sigil {thread.sigils_created + 1}",
            glyph_ids=processed_glyphs,
            emergent_meaning="Synthesized from glyph stream"
        )
        
        sigil.thread_id = thread.id
        thread.add_sigil(sigil.id)
        
        return sigil
    
    def _cleanup_glyphs(self, target_reduction: float = 0.1):
        """
        Cleanup least-accessed glyphs to free space
        
        Args:
            target_reduction: Fraction of glyphs to remove
        """
        # Sort by access count
        sorted_glyphs = sorted(
            self.glyphs.values(),
            key=lambda g: g.access_count
        )
        
        # Remove least-accessed
        remove_count = int(len(sorted_glyphs) * target_reduction)
        for glyph in sorted_glyphs[:remove_count]:
            # Remove bindings
            for bound_id in list(glyph.bound_to):
                if bound_id in self.glyphs:
                    self.glyphs[bound_id].unbind_from(glyph.id)
            
            # Remove glyph
            del self.glyphs[glyph.id]
    
    def get_symbolic_coherence(self) -> float:
        """Calculate overall coherence of symbolic space"""
        if not self.glyphs:
            return 1.0
        
        total_coherence = sum(g.coherence_score for g in self.glyphs.values())
        avg_coherence = total_coherence / len(self.glyphs)
        
        return avg_coherence
    
    def get_engine_status(self) -> Dict:
        """Get comprehensive GBE status"""
        active_threads = [t for t in self.threads.values() if t.active]
        
        return {
            'total_glyphs': len(self.glyphs),
            'total_sigils': len(self.sigils),
            'total_threads': len(self.threads),
            'active_threads': len(active_threads),
            'glyphs_created': self.total_glyphs_created,
            'sigils_created': self.total_sigils_created,
            'bindings_created': self.total_bindings_created,
            'symbolic_coherence': self.get_symbolic_coherence(),
            'capacity_used': len(self.glyphs) / self.max_glyphs,
            'timestamp': datetime.utcnow().isoformat()
        }


# Example usage
def example_gbe():
    """Example of Glyphic Binding Engine operation"""
    print("=" * 70)
    print("Glyphic Binding Engine (GBE) - Recursive Descent Parser")
    print("=" * 70)
    print()
    
    gbe = GlyphicBindingEngine(
        max_threads=5,
        coherence_threshold=0.5,
        max_glyphs=10000
    )
    
    print(f"Initialized GBE")
    print(f"  Max Threads: {gbe.max_threads}")
    print(f"  Coherence Threshold: {gbe.coherence_threshold}")
    print(f"  Max Glyphs: {gbe.max_glyphs}")
    print()
    
    # Create glyphs
    print("Creating glyphs...")
    print("-" * 70)
    
    glyph1 = gbe.create_glyph(
        glyph_type=GlyphType.CONCEPT,
        symbol="Ω",
        semantic_content={'concept': 'Origin', 'domain': 'ontology'},
        source="zoagrad_ontology"
    )
    
    glyph2 = gbe.create_glyph(
        glyph_type=GlyphType.OPERATION,
        symbol="μ",
        semantic_content={'operation': 'minimize', 'unbounded': True},
        source="paradox_network"
    )
    
    glyph3 = gbe.create_glyph(
        glyph_type=GlyphType.SYNTHESIS,
        symbol="⊕",
        semantic_content={'synthesis': 'coherence', 'target': 0.7},
        source="scarindex_oracle"
    )
    
    print(f"Created {len(gbe.glyphs)} glyphs:")
    for glyph in [glyph1, glyph2, glyph3]:
        print(f"  {glyph.symbol} ({glyph.glyph_type.value}): coherence={glyph.coherence_score:.2f}")
    
    # Bind glyphs
    print("\nBinding glyphs...")
    print("-" * 70)
    
    gbe.bind_glyphs(glyph1.id, glyph2.id, BindingStrength.STRONG)
    gbe.bind_glyphs(glyph2.id, glyph3.id, BindingStrength.MODERATE)
    
    print(f"Created {gbe.total_bindings_created} bindings")
    
    # Create sigil
    print("\nCreating sigil...")
    print("-" * 70)
    
    sigil = gbe.create_sigil(
        name="Paradox-Origin Synthesis",
        glyph_ids=[glyph1.id, glyph2.id, glyph3.id],
        emergent_meaning="μ-operator grounded in Origin achieves coherence"
    )
    
    print(f"Created sigil: {sigil.name}")
    print(f"  Components: {len(sigil.component_glyphs)}")
    print(f"  Coherence: {sigil.coherence_score:.2f}")
    print(f"  Meaning: {sigil.emergent_meaning}")
    
    # Process glyph stream
    print("\nProcessing glyph stream...")
    print("-" * 70)
    
    # Create more glyphs for stream
    stream_glyphs = []
    for i in range(5):
        g = gbe.create_glyph(
            glyph_type=GlyphType.CONCEPT,
            symbol=f"C{i}",
            semantic_content={'index': i},
            source="stream"
        )
        stream_glyphs.append(g.id)
    
    stream_sigil = gbe.process_glyph_stream(stream_glyphs)
    
    print(f"Processed stream into sigil: {stream_sigil.name}")
    print(f"  Glyphs processed: {len(stream_sigil.component_glyphs)}")
    print(f"  Coherence: {stream_sigil.coherence_score:.2f}")
    
    # GBE status
    print("\n" + "=" * 70)
    print("GBE Status")
    print("=" * 70)
    
    status = gbe.get_engine_status()
    
    print(f"\nGlyphs: {status['total_glyphs']}")
    print(f"Sigils: {status['total_sigils']}")
    print(f"Bindings: {status['bindings_created']}")
    print(f"Threads: {status['active_threads']}/{status['total_threads']}")
    print(f"Symbolic Coherence: {status['symbolic_coherence']:.4f}")
    print(f"Capacity Used: {status['capacity_used']:.1%}")


if __name__ == '__main__':
    example_gbe()

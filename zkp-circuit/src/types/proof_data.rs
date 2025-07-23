use serde::{Deserialize, Serialize};
use curve25519_dalek_ng::ristretto::CompressedRistretto;

/// Represents a Zero-Knowledge Proof for biometric verification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BiometricProof {
    pub proof: Vec<u8>,
    pub commitments: Vec<Vec<u8>>,
    pub public_inputs: ProofPublicInputs,
    pub metadata: ProofMetadata,
}

/// Public inputs that are revealed during proof verification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofPublicInputs {
    pub threshold: u64,
    pub embedding_size: usize,
    pub commitment_hash: Vec<u8>,
}

/// Metadata about the proof
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofMetadata {
    pub timestamp: u64,
    pub version: String,
    pub circuit_params: CircuitParams,
}

/// Circuit parameters used in proof generation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CircuitParams {
    pub range_bits: usize,
    pub aggregation_size: usize,
    pub transcript_label: String,
}

impl BiometricProof {
    pub fn new(
        proof: Vec<u8>,
        commitments: Vec<Vec<u8>>,
        threshold: u64,
        embedding_size: usize,
        commitment_hash: Vec<u8>,
    ) -> Self {
        let public_inputs = ProofPublicInputs {
            threshold,
            embedding_size,
            commitment_hash,
        };
        
        let metadata = ProofMetadata {
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
            version: env!("CARGO_PKG_VERSION").to_string(),
            circuit_params: CircuitParams {
                range_bits: crate::config::RANGE_BITS,
                aggregation_size: crate::config::AGGREGATION_SIZE,
                transcript_label: String::from_utf8_lossy(crate::config::TRANSCRIPT_LABEL).to_string(),
            },
        };
        
        Self {
            proof,
            commitments,
            public_inputs,
            metadata,
        }
    }
    
    pub fn size(&self) -> usize {
        self.proof.len() + 
        self.commitments.iter().map(|c| c.len()).sum::<usize>() +
        std::mem::size_of_val(&self.public_inputs) +
        std::mem::size_of_val(&self.metadata)
    }
    
    pub fn validate_size(&self) -> Result<(), crate::types::CircuitError> {
        if self.size() > crate::config::MAX_PROOF_SIZE {
            return Err(crate::types::CircuitError::ProofVerificationFailed(
                format!("Proof size {} exceeds maximum {}", self.size(), crate::config::MAX_PROOF_SIZE)
            ));
        }
        Ok(())
    }
    
    pub fn validate_params(&self) -> Result<(), crate::types::CircuitError> {
        if self.public_inputs.threshold == 0 {
            return Err(crate::types::CircuitError::InvalidParameter(
                "Threshold cannot be zero".to_string()
            ));
        }
        
        if self.public_inputs.embedding_size == 0 {
            return Err(crate::types::CircuitError::InvalidParameter(
                "Embedding size cannot be zero".to_string()
            ));
        }
        
        if self.public_inputs.commitment_hash.is_empty() {
            return Err(crate::types::CircuitError::InvalidCommitment(
                "Commitment hash cannot be empty".to_string()
            ));
        }
        
        Ok(())
    }
}

/// Witness data used in proof generation (kept private)
#[derive(Debug, Clone)]
pub struct ProofWitness {
    pub current_embedding: Vec<i64>,
    pub reference_embedding: Vec<i64>,
    pub blinding_factors: Vec<u8>,
    pub distance_squared: u64,
}

impl ProofWitness {
    pub fn new(
        current_embedding: Vec<i64>,
        reference_embedding: Vec<i64>,
        blinding_factors: Vec<u8>,
    ) -> Result<Self, crate::types::CircuitError> {
        if current_embedding.len() != reference_embedding.len() {
            return Err(crate::types::CircuitError::InvalidEmbedding(
                "Embedding size mismatch".to_string()
            ));
        }
        
        // Compute distance squared
        let distance_squared: u64 = current_embedding
            .iter()
            .zip(&reference_embedding)
            .map(|(&a, &b)| {
                let diff = a - b;
                (diff * diff) as u64
            })
            .sum();
        
        Ok(Self {
            current_embedding,
            reference_embedding,
            blinding_factors,
            distance_squared,
        })
    }
    
    pub fn validate_threshold(&self, threshold: u64) -> Result<(), crate::types::CircuitError> {
        if self.distance_squared > threshold {
            return Err(crate::types::CircuitError::ThresholdExceeded {
                expected: threshold,
                actual: self.distance_squared,
            });
        }
        Ok(())
    }
}

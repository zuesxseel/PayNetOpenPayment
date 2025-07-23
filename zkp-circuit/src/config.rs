/// Configuration constants for the ZKP circuit
pub const DEFAULT_EMBEDDING_SIZE: usize = 128;
pub const DEFAULT_THRESHOLD: u64 = 1000;
pub const MAX_EMBEDDING_SIZE: usize = 512;
pub const MIN_THRESHOLD: u64 = 100;
pub const MAX_THRESHOLD: u64 = 10000;

/// Security parameters
pub const TRANSCRIPT_LABEL: &[u8] = b"PayNetZKPBiometric";
pub const COMMITMENT_LABEL: &[u8] = b"BiometricCommitment";
pub const PROOF_LABEL: &[u8] = b"BiometricProof";

/// Circuit parameters
pub const RANGE_BITS: usize = 32; // Bit range for values in circuit
pub const AGGREGATION_SIZE: usize = 1; // Number of range proofs to aggregate

/// Hash parameters
pub const HASH_OUTPUT_SIZE: usize = 32; // Blake3 hash output size

/// Error thresholds
pub const MAX_PROOF_SIZE: usize = 5000; // Maximum proof size in bytes
pub const MAX_COMMITMENT_SIZE: usize = 1000; // Maximum commitment size in bytes

#[derive(Debug, Clone)]
pub struct CircuitConfig {
    pub embedding_size: usize,
    pub threshold: u64,
    pub range_bits: usize,
    pub aggregation_size: usize,
}

impl Default for CircuitConfig {
    fn default() -> Self {
        Self {
            embedding_size: DEFAULT_EMBEDDING_SIZE,
            threshold: DEFAULT_THRESHOLD,
            range_bits: RANGE_BITS,
            aggregation_size: AGGREGATION_SIZE,
        }
    }
}

impl CircuitConfig {
    pub fn new(embedding_size: usize, threshold: u64) -> Result<Self, crate::types::CircuitError> {
        if embedding_size > MAX_EMBEDDING_SIZE {
            return Err(crate::types::CircuitError::InvalidParameter(
                format!("Embedding size {} exceeds maximum {}", embedding_size, MAX_EMBEDDING_SIZE)
            ));
        }
        
        if threshold < MIN_THRESHOLD || threshold > MAX_THRESHOLD {
            return Err(crate::types::CircuitError::InvalidParameter(
                format!("Threshold {} must be between {} and {}", threshold, MIN_THRESHOLD, MAX_THRESHOLD)
            ));
        }
        
        Ok(Self {
            embedding_size,
            threshold,
            range_bits: RANGE_BITS,
            aggregation_size: AGGREGATION_SIZE,
        })
    }
    
    pub fn validate(&self) -> Result<(), crate::types::CircuitError> {
        if self.embedding_size == 0 {
            return Err(crate::types::CircuitError::InvalidParameter(
                "Embedding size cannot be zero".to_string()
            ));
        }
        
        if self.threshold == 0 {
            return Err(crate::types::CircuitError::InvalidParameter(
                "Threshold cannot be zero".to_string()
            ));
        }
        
        Ok(())
    }
}

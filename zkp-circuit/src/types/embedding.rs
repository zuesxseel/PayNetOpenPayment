use thiserror::Error;
use serde::{Deserialize, Serialize};

/// Error types for ZKP circuit operations
#[derive(Error, Debug)]
pub enum CircuitError {
    #[error("Invalid parameter: {0}")]
    InvalidParameter(String),
    
    #[error("Proof generation failed: {0}")]
    ProofGenerationFailed(String),
    
    #[error("Proof verification failed: {0}")]
    ProofVerificationFailed(String),
    
    #[error("Serialization error: {0}")]
    SerializationError(String),
    
    #[error("Cryptographic error: {0}")]
    CryptographicError(String),
    
    #[error("Invalid commitment: {0}")]
    InvalidCommitment(String),
    
    #[error("Invalid embedding data: {0}")]
    InvalidEmbedding(String),
    
    #[error("Threshold exceeded: expected {expected}, got {actual}")]
    ThresholdExceeded { expected: u64, actual: u64 },
}

/// Result type for ZKP operations
pub type CircuitResult<T> = Result<T, CircuitError>;

/// Represents a biometric embedding vector
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BiometricEmbedding {
    pub data: Vec<i64>,
    pub size: usize,
    pub normalized: bool,
}

impl BiometricEmbedding {
    pub fn new(data: Vec<i64>) -> CircuitResult<Self> {
        if data.is_empty() {
            return Err(CircuitError::InvalidEmbedding(
                "Embedding data cannot be empty".to_string()
            ));
        }
        
        let size = data.len();
        if size > crate::config::MAX_EMBEDDING_SIZE {
            return Err(CircuitError::InvalidEmbedding(
                format!("Embedding size {} exceeds maximum {}", size, crate::config::MAX_EMBEDDING_SIZE)
            ));
        }
        
        Ok(Self {
            data,
            size,
            normalized: false,
        })
    }
    
    pub fn from_floats(floats: Vec<f64>, scale_factor: i64) -> CircuitResult<Self> {
        let data: Vec<i64> = floats
            .into_iter()
            .map(|f| (f * scale_factor as f64) as i64)
            .collect();
        
        Self::new(data)
    }
    
    pub fn normalize(&mut self) -> CircuitResult<()> {
        if self.data.is_empty() {
            return Err(CircuitError::InvalidEmbedding(
                "Cannot normalize empty embedding".to_string()
            ));
        }
        
        // Compute L2 norm
        let norm_squared: i64 = self.data.iter().map(|&x| x * x).sum();
        let norm = (norm_squared as f64).sqrt() as i64;
        
        if norm == 0 {
            return Err(CircuitError::InvalidEmbedding(
                "Cannot normalize zero vector".to_string()
            ));
        }
        
        // Normalize each component
        for value in &mut self.data {
            *value = (*value * 1000) / norm; // Scale by 1000 to maintain precision
        }
        
        self.normalized = true;
        Ok(())
    }
    
    pub fn compute_distance_squared(&self, other: &Self) -> CircuitResult<u64> {
        if self.size != other.size {
            return Err(CircuitError::InvalidEmbedding(
                format!("Embedding size mismatch: {} vs {}", self.size, other.size)
            ));
        }
        
        let distance_squared: i64 = self.data
            .iter()
            .zip(&other.data)
            .map(|(&a, &b)| {
                let diff = a - b;
                diff * diff
            })
            .sum();
        
        Ok(distance_squared as u64)
    }
}

/// Represents a commitment to biometric data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BiometricCommitment {
    pub commitment: Vec<u8>,
    pub blinding_factor: Vec<u8>,
    pub hash: Vec<u8>,
}

impl BiometricCommitment {
    pub fn new(commitment: Vec<u8>, blinding_factor: Vec<u8>, hash: Vec<u8>) -> Self {
        Self {
            commitment,
            blinding_factor,
            hash,
        }
    }
}

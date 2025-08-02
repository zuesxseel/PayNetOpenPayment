pub mod circuit;
pub mod proof;
pub mod crypto;
pub mod types;
pub mod utils;
pub mod config;

pub use circuit::*;
pub use proof::*;
pub use crypto::*;
pub use types::*;
pub use utils::*;
pub use config::*;

// Re-export commonly used types for convenience
pub use bulletproofs::{BulletproofGens, PedersenGens};
pub use curve25519_dalek_ng::scalar::Scalar;
pub use merlin::Transcript;

/// Main ZKP Circuit Library
/// 
/// This library provides Zero-Knowledge Proof capabilities for biometric authentication
/// using Bulletproofs protocol. It enables privacy-preserving verification of biometric
/// similarity without revealing the actual biometric data.
pub struct ZKPCircuit;

impl ZKPCircuit {
    /// Initialize a new ZKP circuit with default parameters
    pub fn new() -> BiometricCircuit {
        BiometricCircuit::new(128, 1000) // 128-dim embeddings, threshold 1000
    }
    
    /// Initialize a ZKP circuit with custom parameters
    pub fn with_params(embedding_size: usize, threshold: u64) -> BiometricCircuit {
        BiometricCircuit::new(embedding_size, threshold)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_zkp_circuit_creation() {
        let circuit = ZKPCircuit::new();
        assert_eq!(circuit.embedding_size, 128);
        assert_eq!(circuit.threshold, 1000);
    }
}

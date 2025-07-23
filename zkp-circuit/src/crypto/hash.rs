use blake3;
use sha2::{Sha256, Digest};
use crate::types::{CircuitError, CircuitResult};

/// Hash utilities for ZKP circuit
pub struct HashUtils;

impl HashUtils {
    /// Compute Blake3 hash of input data
    pub fn blake3_hash(data: &[u8]) -> Vec<u8> {
        blake3::hash(data).as_bytes().to_vec()
    }
    
    /// Compute SHA256 hash of input data
    pub fn sha256_hash(data: &[u8]) -> Vec<u8> {
        let mut hasher = Sha256::new();
        hasher.update(data);
        hasher.finalize().to_vec()
    }
    
    /// Hash an embedding vector to create a commitment hash
    pub fn hash_embedding(embedding: &[i64]) -> Vec<u8> {
        let mut hasher = blake3::Hasher::new();
        
        // Convert each i64 to bytes and hash
        for &value in embedding {
            hasher.update(&value.to_le_bytes());
        }
        
        hasher.finalize().as_bytes().to_vec()
    }
    
    /// Create a commitment hash from multiple components
    pub fn commitment_hash(components: &[&[u8]]) -> Vec<u8> {
        let mut hasher = blake3::Hasher::new();
        
        for component in components {
            hasher.update(component);
        }
        
        hasher.finalize().as_bytes().to_vec()
    }
    
    /// Verify hash equality with constant-time comparison
    pub fn verify_hash(expected: &[u8], actual: &[u8]) -> bool {
        if expected.len() != actual.len() {
            return false;
        }
        
        // Constant-time comparison to prevent timing attacks
        let mut result = 0u8;
        for (a, b) in expected.iter().zip(actual.iter()) {
            result |= a ^ b;
        }
        
        result == 0
    }
    
    /// Hash multiple embeddings together (for batch operations)
    pub fn hash_embedding_batch(embeddings: &[&[i64]]) -> Vec<u8> {
        let mut hasher = blake3::Hasher::new();
        
        for embedding in embeddings {
            for &value in *embedding {
                hasher.update(&value.to_le_bytes());
            }
        }
        
        hasher.finalize().as_bytes().to_vec()
    }
}

/// Poseidon-like hash simulation for circuit compatibility
/// simplified version for demo
pub struct CircuitHash;

impl CircuitHash {
    /// Simulate Poseidon hash using Blake3 (for circuit constraints)
    pub fn poseidon_simulate(inputs: &[u64]) -> CircuitResult<u64> {
        if inputs.is_empty() {
            return Err(CircuitError::InvalidParameter(
                "Cannot hash empty input".to_string()
            ));
        }
        
        let mut hasher = blake3::Hasher::new();
        
        for &input in inputs {
            hasher.update(&input.to_le_bytes());
        }
        
        let hash_bytes = hasher.finalize();
        let hash_slice = &hash_bytes.as_bytes()[0..8];
        let hash_u64 = u64::from_le_bytes(hash_slice.try_into().unwrap());
        
        Ok(hash_u64)
    }
    
    /// Hash two field elements (for circuit merkle tree operations)
    pub fn hash_pair(left: u64, right: u64) -> CircuitResult<u64> {
        Self::poseidon_simulate(&[left, right])
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_blake3_hash() {
        let data = b"test data";
        let hash1 = HashUtils::blake3_hash(data);
        let hash2 = HashUtils::blake3_hash(data);
        
        assert_eq!(hash1, hash2);
        assert_eq!(hash1.len(), 32);
    }
    
    #[test]
    fn test_embedding_hash() {
        let embedding = vec![1, 2, 3, 4, 5];
        let hash1 = HashUtils::hash_embedding(&embedding);
        let hash2 = HashUtils::hash_embedding(&embedding);
        
        assert_eq!(hash1, hash2);
        assert_eq!(hash1.len(), 32);
        
        // Different embedding should produce different hash
        let embedding2 = vec![1, 2, 3, 4, 6];
        let hash3 = HashUtils::hash_embedding(&embedding2);
        assert_ne!(hash1, hash3);
    }
    
    #[test]
    fn test_verify_hash() {
        let data = b"test";
        let hash = HashUtils::blake3_hash(data);
        
        assert!(HashUtils::verify_hash(&hash, &hash));
        
        let wrong_hash = HashUtils::blake3_hash(b"wrong");
        assert!(!HashUtils::verify_hash(&hash, &wrong_hash));
    }
    
    #[test]
    fn test_circuit_hash() {
        let inputs = vec![1, 2, 3, 4];
        let hash1 = CircuitHash::poseidon_simulate(&inputs).unwrap();
        let hash2 = CircuitHash::poseidon_simulate(&inputs).unwrap();
        
        assert_eq!(hash1, hash2);
        
        let different_inputs = vec![1, 2, 3, 5];
        let hash3 = CircuitHash::poseidon_simulate(&different_inputs).unwrap();
        assert_ne!(hash1, hash3);
    }
}

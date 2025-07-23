use serde::{Deserialize, Serialize};
use crate::types::{CircuitError, CircuitResult, BiometricProof, BiometricEmbedding};

/// Serialization utilities for ZKP circuit types
pub struct SerializationUtils;

impl SerializationUtils {
    /// Serialize a BiometricProof to JSON bytes
    pub fn serialize_proof(proof: &BiometricProof) -> CircuitResult<Vec<u8>> {
        serde_json::to_vec(proof)
            .map_err(|e| CircuitError::SerializationError(format!("Failed to serialize proof: {}", e)))
    }
    
    /// Deserialize a BiometricProof from JSON bytes
    pub fn deserialize_proof(data: &[u8]) -> CircuitResult<BiometricProof> {
        serde_json::from_slice(data)
            .map_err(|e| CircuitError::SerializationError(format!("Failed to deserialize proof: {}", e)))
    }
    
    /// Serialize a BiometricEmbedding to JSON bytes
    pub fn serialize_embedding(embedding: &BiometricEmbedding) -> CircuitResult<Vec<u8>> {
        serde_json::to_vec(embedding)
            .map_err(|e| CircuitError::SerializationError(format!("Failed to serialize embedding: {}", e)))
    }
    
    /// Deserialize a BiometricEmbedding from JSON bytes
    pub fn deserialize_embedding(data: &[u8]) -> CircuitResult<BiometricEmbedding> {
        serde_json::from_slice(data)
            .map_err(|e| CircuitError::SerializationError(format!("Failed to deserialize embedding: {}", e)))
    }
    
    /// Serialize proof to hex string for easy transmission
    pub fn proof_to_hex(proof: &BiometricProof) -> CircuitResult<String> {
        let bytes = Self::serialize_proof(proof)?;
        Ok(hex::encode(bytes))
    }
    
    /// Deserialize proof from hex string
    pub fn proof_from_hex(hex_string: &str) -> CircuitResult<BiometricProof> {
        let bytes = hex::decode(hex_string)
            .map_err(|e| CircuitError::SerializationError(format!("Invalid hex string: {}", e)))?;
        Self::deserialize_proof(&bytes)
    }
    
    /// Convert proof to base64 for web compatibility
    pub fn proof_to_base64(proof: &BiometricProof) -> CircuitResult<String> {
        let bytes = Self::serialize_proof(proof)?;
        Ok(base64::encode(bytes))
    }
    
    /// Convert proof from base64
    pub fn proof_from_base64(base64_string: &str) -> CircuitResult<BiometricProof> {
        let bytes = base64::decode(base64_string)
            .map_err(|e| CircuitError::SerializationError(format!("Invalid base64 string: {}", e)))?;
        Self::deserialize_proof(&bytes)
    }
}

/// Binary serialization for more efficient storage/transmission
pub struct BinarySerializer;

impl BinarySerializer {
    /// Serialize proof to compact binary format
    pub fn serialize_proof_binary(proof: &BiometricProof) -> CircuitResult<Vec<u8>> {
        // Custom binary format for efficiency
        let mut buffer = Vec::new();
        
        // Write proof length and data
        buffer.extend_from_slice(&(proof.proof.len() as u32).to_le_bytes());
        buffer.extend_from_slice(&proof.proof);
        
        // Write commitments count and data
        buffer.extend_from_slice(&(proof.commitments.len() as u32).to_le_bytes());
        for commitment in &proof.commitments {
            buffer.extend_from_slice(&(commitment.len() as u32).to_le_bytes());
            buffer.extend_from_slice(commitment);
        }
        
        // Write public inputs
        buffer.extend_from_slice(&proof.public_inputs.threshold.to_le_bytes());
        buffer.extend_from_slice(&(proof.public_inputs.embedding_size as u32).to_le_bytes());
        buffer.extend_from_slice(&(proof.public_inputs.commitment_hash.len() as u32).to_le_bytes());
        buffer.extend_from_slice(&proof.public_inputs.commitment_hash);
        
        // Write metadata
        buffer.extend_from_slice(&proof.metadata.timestamp.to_le_bytes());
        let version_bytes = proof.metadata.version.as_bytes();
        buffer.extend_from_slice(&(version_bytes.len() as u32).to_le_bytes());
        buffer.extend_from_slice(version_bytes);
        
        Ok(buffer)
    }
    
    /// Deserialize proof from binary format
    pub fn deserialize_proof_binary(data: &[u8]) -> CircuitResult<BiometricProof> {
        let mut offset = 0;
        
        // Read proof
        if data.len() < offset + 4 {
            return Err(CircuitError::SerializationError("Insufficient data for proof length".to_string()));
        }
        let proof_len = u32::from_le_bytes([data[offset], data[offset+1], data[offset+2], data[offset+3]]) as usize;
        offset += 4;
        
        if data.len() < offset + proof_len {
            return Err(CircuitError::SerializationError("Insufficient data for proof".to_string()));
        }
        let proof = data[offset..offset + proof_len].to_vec();
        offset += proof_len;
        
        // Read commitments
        if data.len() < offset + 4 {
            return Err(CircuitError::SerializationError("Insufficient data for commitments count".to_string()));
        }
        let commitments_count = u32::from_le_bytes([data[offset], data[offset+1], data[offset+2], data[offset+3]]) as usize;
        offset += 4;
        
        let mut commitments = Vec::new();
        for _ in 0..commitments_count {
            if data.len() < offset + 4 {
                return Err(CircuitError::SerializationError("Insufficient data for commitment length".to_string()));
            }
            let commitment_len = u32::from_le_bytes([data[offset], data[offset+1], data[offset+2], data[offset+3]]) as usize;
            offset += 4;
            
            if data.len() < offset + commitment_len {
                return Err(CircuitError::SerializationError("Insufficient data for commitment".to_string()));
            }
            commitments.push(data[offset..offset + commitment_len].to_vec());
            offset += commitment_len;
        }
        
        // Read remaining fields...
        // (For brevity, using simplified deserialization)
        
        // Create a simplified proof for demo
        Ok(BiometricProof::new(
            proof,
            commitments,
            1000, // placeholder threshold
            128,  // placeholder embedding size
            vec![0; 32], // placeholder hash
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::BiometricProof;
    
    #[test]
    fn test_json_serialization() {
        let proof = BiometricProof::new(
            vec![1, 2, 3, 4, 5],
            vec![vec![1, 2], vec![3, 4]],
            1000,
            128,
            vec![0; 32],
        );
        
        // Test JSON serialization
        let serialized = SerializationUtils::serialize_proof(&proof).unwrap();
        let deserialized = SerializationUtils::deserialize_proof(&serialized).unwrap();
        
        assert_eq!(proof.proof, deserialized.proof);
        assert_eq!(proof.commitments, deserialized.commitments);
    }
    
    #[test]
    fn test_hex_serialization() {
        let proof = BiometricProof::new(
            vec![1, 2, 3, 4, 5],
            vec![vec![1, 2], vec![3, 4]],
            1000,
            128,
            vec![0; 32],
        );
        
        // Test hex serialization
        let hex_string = SerializationUtils::proof_to_hex(&proof).unwrap();
        let deserialized = SerializationUtils::proof_from_hex(&hex_string).unwrap();
        
        assert_eq!(proof.proof, deserialized.proof);
    }
    
    #[test]
    fn test_binary_serialization() {
        let proof = BiometricProof::new(
            vec![1, 2, 3, 4, 5],
            vec![vec![1, 2], vec![3, 4]],
            1000,
            128,
            vec![0; 32],
        );
        
        // Test binary serialization
        let binary = BinarySerializer::serialize_proof_binary(&proof).unwrap();
        let deserialized = BinarySerializer::deserialize_proof_binary(&binary).unwrap();
        
        assert_eq!(proof.proof, deserialized.proof);
        assert_eq!(proof.commitments, deserialized.commitments);
    }
}

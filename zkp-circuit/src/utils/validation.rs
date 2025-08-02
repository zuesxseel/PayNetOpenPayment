use crate::types::{CircuitError, CircuitResult, BiometricEmbedding, BiometricProof};
use crate::config::{MAX_EMBEDDING_SIZE, MIN_THRESHOLD, MAX_THRESHOLD, MAX_PROOF_SIZE};

/// Input validation utilities for ZKP circuit
pub struct ValidationUtils;

impl ValidationUtils {
    /// Validate biometric embedding data
    pub fn validate_embedding(embedding: &BiometricEmbedding) -> CircuitResult<()> {
        // Check size limits
        if embedding.size == 0 {
            return Err(CircuitError::InvalidEmbedding(
                "Embedding cannot be empty".to_string()
            ));
        }
        
        if embedding.size > MAX_EMBEDDING_SIZE {
            return Err(CircuitError::InvalidEmbedding(
                format!("Embedding size {} exceeds maximum {}", embedding.size, MAX_EMBEDDING_SIZE)
            ));
        }
        
        // Check data consistency
        if embedding.data.len() != embedding.size {
            return Err(CircuitError::InvalidEmbedding(
                format!("Data length {} does not match size {}", embedding.data.len(), embedding.size)
            ));
        }
        
        // Check for reasonable value ranges (prevent overflow in calculations)
        for (i, &value) in embedding.data.iter().enumerate() {
            if value.abs() > 1_000_000 {
                return Err(CircuitError::InvalidEmbedding(
                    format!("Embedding value at index {} is too large: {}", i, value)
                ));
            }
        }
        
        Ok(())
    }
    
    /// Validate threshold parameter
    pub fn validate_threshold(threshold: u64) -> CircuitResult<()> {
        if threshold < MIN_THRESHOLD {
            return Err(CircuitError::InvalidParameter(
                format!("Threshold {} is below minimum {}", threshold, MIN_THRESHOLD)
            ));
        }
        
        if threshold > MAX_THRESHOLD {
            return Err(CircuitError::InvalidParameter(
                format!("Threshold {} exceeds maximum {}", threshold, MAX_THRESHOLD)
            ));
        }
        
        Ok(())
    }
    
    /// Validate embedding size parameter
    pub fn validate_embedding_size(size: usize) -> CircuitResult<()> {
        if size == 0 {
            return Err(CircuitError::InvalidParameter(
                "Embedding size cannot be zero".to_string()
            ));
        }
        
        if size > MAX_EMBEDDING_SIZE {
            return Err(CircuitError::InvalidParameter(
                format!("Embedding size {} exceeds maximum {}", size, MAX_EMBEDDING_SIZE)
            ));
        }
        
        // Check if size is a reasonable power of 2 or common size
        if !Self::is_reasonable_embedding_size(size) {
            return Err(CircuitError::InvalidParameter(
                format!("Embedding size {} is not a recommended size", size)
            ));
        }
        
        Ok(())
    }
    
    /// Validate proof structure and size
    pub fn validate_proof(proof: &BiometricProof) -> CircuitResult<()> {
        // Check proof size
        if proof.size() > MAX_PROOF_SIZE {
            return Err(CircuitError::ProofVerificationFailed(
                format!("Proof size {} exceeds maximum {}", proof.size(), MAX_PROOF_SIZE)
            ));
        }
        
        // Check proof is not empty
        if proof.proof.is_empty() {
            return Err(CircuitError::ProofVerificationFailed(
                "Proof data cannot be empty".to_string()
            ));
        }
        
        // Validate public inputs
        Self::validate_threshold(proof.public_inputs.threshold)?;
        Self::validate_embedding_size(proof.public_inputs.embedding_size)?;
        
        // Check commitment hash
        if proof.public_inputs.commitment_hash.is_empty() {
            return Err(CircuitError::InvalidCommitment(
                "Commitment hash cannot be empty".to_string()
            ));
        }
        
        if proof.public_inputs.commitment_hash.len() != 32 {
            return Err(CircuitError::InvalidCommitment(
                format!("Invalid commitment hash length: {}", proof.public_inputs.commitment_hash.len())
            ));
        }
        
        // Validate commitments
        if proof.commitments.is_empty() {
            return Err(CircuitError::InvalidCommitment(
                "Proof must contain commitments".to_string()
            ));
        }
        
        for (i, commitment) in proof.commitments.iter().enumerate() {
            if commitment.is_empty() {
                return Err(CircuitError::InvalidCommitment(
                    format!("Commitment {} is empty", i)
                ));
            }
            
            if commitment.len() != 32 {
                return Err(CircuitError::InvalidCommitment(
                    format!("Invalid commitment {} length: {}", i, commitment.len())
                ));
            }
        }
        
        // Validate metadata
        if proof.metadata.timestamp == 0 {
            return Err(CircuitError::InvalidParameter(
                "Invalid timestamp in proof metadata".to_string()
            ));
        }
        
        if proof.metadata.version.is_empty() {
            return Err(CircuitError::InvalidParameter(
                "Version cannot be empty in proof metadata".to_string()
            ));
        }
        
        Ok(())
    }
    
    /// Check if embedding vectors are compatible for distance computation
    pub fn validate_embedding_compatibility(
        embedding1: &BiometricEmbedding,
        embedding2: &BiometricEmbedding,
    ) -> CircuitResult<()> {
        Self::validate_embedding(embedding1)?;
        Self::validate_embedding(embedding2)?;
        
        if embedding1.size != embedding2.size {
            return Err(CircuitError::InvalidEmbedding(
                format!("Embedding size mismatch: {} vs {}", embedding1.size, embedding2.size)
            ));
        }
        
        Ok(())
    }
    
    /// Validate float array before conversion to embedding
    pub fn validate_float_array(floats: &[f64], scale_factor: i64) -> CircuitResult<()> {
        if floats.is_empty() {
            return Err(CircuitError::InvalidEmbedding(
                "Float array cannot be empty".to_string()
            ));
        }
        
        if floats.len() > MAX_EMBEDDING_SIZE {
            return Err(CircuitError::InvalidEmbedding(
                format!("Float array size {} exceeds maximum {}", floats.len(), MAX_EMBEDDING_SIZE)
            ));
        }
        
        if scale_factor <= 0 {
            return Err(CircuitError::InvalidParameter(
                "Scale factor must be positive".to_string()
            ));
        }
        
        // Check for NaN or infinite values
        for (i, &value) in floats.iter().enumerate() {
            if !value.is_finite() {
                return Err(CircuitError::InvalidEmbedding(
                    format!("Float value at index {} is not finite: {}", i, value)
                ));
            }
            
            // Check if scaled value will be reasonable
            let scaled = (value * scale_factor as f64).abs();
            if scaled > 1_000_000.0 {
                return Err(CircuitError::InvalidEmbedding(
                    format!("Scaled float value at index {} is too large: {}", i, scaled)
                ));
            }
        }
        
        Ok(())
    }
    
    /// Check if the embedding size is reasonable (common sizes used in ML)
    fn is_reasonable_embedding_size(size: usize) -> bool {
        // Common embedding sizes in machine learning
        const COMMON_SIZES: &[usize] = &[
            16, 32, 64, 128, 256, 384, 512, 768, 1024, 1536, 2048
        ];
        
        COMMON_SIZES.contains(&size) || Self::is_power_of_two(size)
    }
    
    /// Check if a number is a power of two
    fn is_power_of_two(n: usize) -> bool {
        n > 0 && (n & (n - 1)) == 0
    }
    
    /// Sanitize embedding data (remove outliers, clamp values)
    pub fn sanitize_embedding(embedding: &mut BiometricEmbedding) -> CircuitResult<()> {
        // Clamp values to reasonable range
        const MAX_ABS_VALUE: i64 = 100_000;
        
        for value in &mut embedding.data {
            *value = (*value).clamp(-MAX_ABS_VALUE, MAX_ABS_VALUE);
        }
        
        // Remove extreme outliers using z-score
        let mean = embedding.data.iter().sum::<i64>() as f64 / embedding.data.len() as f64;
        let variance = embedding.data.iter()
            .map(|&x| {
                let diff = x as f64 - mean;
                diff * diff
            })
            .sum::<f64>() / embedding.data.len() as f64;
        
        let std_dev = variance.sqrt();
        
        if std_dev > 0.0 {
            for value in &mut embedding.data {
                let z_score = (*value as f64 - mean) / std_dev;
                if z_score.abs() > 3.0 {
                    // Replace outliers with clamped values
                    *value = if z_score > 0.0 {
                        (mean + 3.0 * std_dev) as i64
                    } else {
                        (mean - 3.0 * std_dev) as i64
                    };
                }
            }
        }
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_embedding_validation() {
        // Valid embedding
        let embedding = BiometricEmbedding::new(vec![1, 2, 3, 4, 5]).unwrap();
        assert!(ValidationUtils::validate_embedding(&embedding).is_ok());
        
        // Too large values
        let large_embedding = BiometricEmbedding::new(vec![2_000_000]).unwrap();
        assert!(ValidationUtils::validate_embedding(&large_embedding).is_err());
    }
    
    #[test]
    fn test_threshold_validation() {
        assert!(ValidationUtils::validate_threshold(1000).is_ok());
        assert!(ValidationUtils::validate_threshold(50).is_err()); // Below minimum
        assert!(ValidationUtils::validate_threshold(20000).is_err()); // Above maximum
    }
    
    #[test]
    fn test_embedding_size_validation() {
        assert!(ValidationUtils::validate_embedding_size(128).is_ok()); // Common size
        assert!(ValidationUtils::validate_embedding_size(64).is_ok());  // Power of 2
        assert!(ValidationUtils::validate_embedding_size(0).is_err());  // Zero
        assert!(ValidationUtils::validate_embedding_size(1000).is_err()); // Too large
    }
    
    #[test]
    fn test_float_array_validation() {
        let valid_floats = vec![0.1, 0.2, 0.3, 0.4];
        assert!(ValidationUtils::validate_float_array(&valid_floats, 1000).is_ok());
        
        let invalid_floats = vec![f64::NAN, 0.2, 0.3];
        assert!(ValidationUtils::validate_float_array(&invalid_floats, 1000).is_err());
        
        let empty_floats: Vec<f64> = vec![];
        assert!(ValidationUtils::validate_float_array(&empty_floats, 1000).is_err());
    }
    
    #[test]
    fn test_embedding_compatibility() {
        let embedding1 = BiometricEmbedding::new(vec![1, 2, 3]).unwrap();
        let embedding2 = BiometricEmbedding::new(vec![4, 5, 6]).unwrap();
        let embedding3 = BiometricEmbedding::new(vec![7, 8]).unwrap();
        
        // Compatible embeddings
        assert!(ValidationUtils::validate_embedding_compatibility(&embedding1, &embedding2).is_ok());
        
        // Incompatible embeddings (different sizes)
        assert!(ValidationUtils::validate_embedding_compatibility(&embedding1, &embedding3).is_err());
    }
    
    #[test]
    fn test_sanitize_embedding() {
        let mut embedding = BiometricEmbedding::new(vec![1, 2, 200_000, 4, 5]).unwrap();
        ValidationUtils::sanitize_embedding(&mut embedding).unwrap();
        
        // The outlier should be clamped
        assert!(embedding.data.iter().all(|&x| x.abs() <= 100_000));
    }
}

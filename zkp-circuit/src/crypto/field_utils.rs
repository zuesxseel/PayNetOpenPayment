use curve25519_dalek_ng::scalar::Scalar;
use crate::types::{CircuitError, CircuitResult};

/// Field arithmetic utilities for ZKP circuit
pub struct FieldUtils;

impl FieldUtils {
    /// Convert i64 to Scalar (with bounds checking)
    pub fn i64_to_scalar(value: i64) -> CircuitResult<Scalar> {
        if value < 0 {
            // Handle negative values by adding field modulus
            let abs_value = (-value) as u64;
            let scalar = Scalar::from(abs_value);
            Ok(-scalar)
        } else {
            Ok(Scalar::from(value as u64))
        }
    }
    
    /// Convert u64 to Scalar
    pub fn u64_to_scalar(value: u64) -> Scalar {
        Scalar::from(value)
    }
    
    /// Convert Scalar back to u64 (if possible)
    pub fn scalar_to_u64(scalar: &Scalar) -> CircuitResult<u64> {
        let bytes = scalar.as_bytes();
        
        // Check if the scalar fits in u64 (first 24 bytes should be zero)
        for &byte in &bytes[8..] {
            if byte != 0 {
                return Err(CircuitError::CryptographicError(
                    "Scalar too large to convert to u64".to_string()
                ));
            }
        }
        
        let mut u64_bytes = [0u8; 8];
        u64_bytes.copy_from_slice(&bytes[0..8]);
        Ok(u64::from_le_bytes(u64_bytes))
    }
    
    /// Compute scalar from embedding values
    pub fn embedding_to_scalars(embedding: &[i64]) -> CircuitResult<Vec<Scalar>> {
        embedding
            .iter()
            .map(|&value| Self::i64_to_scalar(value))
            .collect()
    }
    
    /// Compute dot product of two scalar vectors
    pub fn scalar_dot_product(a: &[Scalar], b: &[Scalar]) -> CircuitResult<Scalar> {
        if a.len() != b.len() {
            return Err(CircuitError::InvalidParameter(
                "Vector length mismatch for dot product".to_string()
            ));
        }
        
        let mut result = Scalar::zero();
        for (ai, bi) in a.iter().zip(b.iter()) {
            result += ai * bi;
        }
        
        Ok(result)
    }
    
    /// Compute squared euclidean distance between two scalar vectors
    pub fn scalar_distance_squared(a: &[Scalar], b: &[Scalar]) -> CircuitResult<Scalar> {
        if a.len() != b.len() {
            return Err(CircuitError::InvalidParameter(
                "Vector length mismatch for distance calculation".to_string()
            ));
        }
        
        let mut sum = Scalar::zero();
        for (ai, bi) in a.iter().zip(b.iter()) {
            let diff = ai - bi;
            sum += diff * diff;
        }
        
        Ok(sum)
    }
    
    /// Check if scalar is within a given range [0, max_value)
    pub fn is_in_range(scalar: &Scalar, max_value: u64) -> bool {
        match Self::scalar_to_u64(scalar) {
            Ok(value) => value < max_value,
            Err(_) => false,
        }
    }
    
    /// Generate random scalar in range [0, max_value)
    pub fn random_scalar_in_range(max_value: u64) -> Scalar {
        let random_value = rand::random::<u64>() % max_value;
        Scalar::from(random_value)
    }
    
    /// Compute modular inverse of a scalar
    pub fn scalar_inverse(scalar: &Scalar) -> CircuitResult<Scalar> {
        let inverse = scalar.invert();
        // Check if the inverse is valid (non-zero scalar)
        if inverse != Scalar::zero() {
            Ok(inverse)
        } else {
            Err(CircuitError::CryptographicError(
                "Scalar is not invertible".to_string()
            ))
        }
    }
}

/// Batch operations for field elements
pub struct BatchFieldOps;

impl BatchFieldOps {
    /// Sum multiple scalars
    pub fn sum_scalars(scalars: &[Scalar]) -> Scalar {
        scalars.iter().fold(Scalar::zero(), |acc, s| acc + s)
    }
    
    /// Multiply multiple scalars
    pub fn product_scalars(scalars: &[Scalar]) -> Scalar {
        scalars.iter().fold(Scalar::one(), |acc, s| acc * s)
    }
    
    /// Compute linear combination: sum(coeffs[i] * values[i])
    pub fn linear_combination(coeffs: &[Scalar], values: &[Scalar]) -> CircuitResult<Scalar> {
        if coeffs.len() != values.len() {
            return Err(CircuitError::InvalidParameter(
                "Coefficient and value arrays must have same length".to_string()
            ));
        }
        
        let mut result = Scalar::zero();
        for (coeff, value) in coeffs.iter().zip(values.iter()) {
            result += coeff * value;
        }
        
        Ok(result)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_i64_to_scalar_conversion() {
        let positive = 42i64;
        let scalar_pos = FieldUtils::i64_to_scalar(positive).unwrap();
        assert_eq!(FieldUtils::scalar_to_u64(&scalar_pos).unwrap(), 42u64);
        
        let negative = -42i64;
        let scalar_neg = FieldUtils::i64_to_scalar(negative).unwrap();
        assert_ne!(scalar_pos, scalar_neg);
    }
    
    #[test]
    fn test_embedding_to_scalars() {
        let embedding = vec![1, -2, 3, -4, 5];
        let scalars = FieldUtils::embedding_to_scalars(&embedding).unwrap();
        assert_eq!(scalars.len(), 5);
    }
    
    #[test]
    fn test_scalar_distance() {
        let a = vec![Scalar::one(), Scalar::from(2u64), Scalar::from(3u64)];
        let b = vec![Scalar::from(4u64), Scalar::from(5u64), Scalar::from(6u64)];
        
        let distance_sq = FieldUtils::scalar_distance_squared(&a, &b).unwrap();
        
        // Distance should be sqrt((4-1)² + (5-2)² + (6-3)²) = sqrt(9 + 9 + 9) = sqrt(27)
        // So distance² should be 27
        assert_eq!(FieldUtils::scalar_to_u64(&distance_sq).unwrap(), 27);
    }
    
    #[test]
    fn test_batch_operations() {
        let scalars = vec![Scalar::one(), Scalar::from(2u64), Scalar::from(3u64)];
        
        let sum = BatchFieldOps::sum_scalars(&scalars);
        assert_eq!(FieldUtils::scalar_to_u64(&sum).unwrap(), 6);
        
        let product = BatchFieldOps::product_scalars(&scalars);
        assert_eq!(FieldUtils::scalar_to_u64(&product).unwrap(), 6);
    }
}

use curve25519_dalek_ng::{ristretto::RistrettoPoint, scalar::Scalar};
use rand::Rng;

/// Pedersen commitment scheme for hiding values while enabling zero-knowledge proofs
pub struct CommitmentScheme {
    /// Generator point G for value component
    pub g: RistrettoPoint,
    /// Generator point H for blinding factor component
    pub h: RistrettoPoint,
}

impl CommitmentScheme {
    /// Create a new commitment scheme with random generators
    pub fn new() -> Self {
        let mut rng = rand::thread_rng();
        
        // Generate random points for G and H
        // In practice, these should be deterministic "nothing up my sleeve" points
        let g = RistrettoPoint::random(&mut rng);
        let h = RistrettoPoint::random(&mut rng);
        
        Self { g, h }
    }
    
    /// Create a commitment to a value with a blinding factor
    /// Commitment = value * G + blinding * H
    pub fn commit(&self, value: &Scalar, blinding: &Scalar) -> RistrettoPoint {
        value * self.g + blinding * self.h
    }
    
    /// Create a commitment with a random blinding factor
    pub fn commit_with_random_blinding(&self, value: &Scalar) -> (RistrettoPoint, Scalar) {
        let mut rng = rand::thread_rng();
        let blinding = Scalar::random(&mut rng);
        let commitment = self.commit(value, &blinding);
        (commitment, blinding)
    }
    
    /// Verify that a commitment opens to the given value and blinding factor
    pub fn verify(&self, commitment: &RistrettoPoint, value: &Scalar, blinding: &Scalar) -> bool {
        let expected_commitment = self.commit(value, blinding);
        commitment == &expected_commitment
    }
}

impl Default for CommitmentScheme {
    fn default() -> Self {
        Self::new()
    }
}

/// A commitment to a value with its blinding factor
#[derive(Debug, Clone)]
pub struct Commitment {
    pub point: RistrettoPoint,
    pub blinding: Scalar,
}

impl Commitment {
    /// Create a new commitment for a value
    pub fn new(value: &Scalar, scheme: &CommitmentScheme) -> Self {
        let (point, blinding) = scheme.commit_with_random_blinding(value);
        Self { point, blinding }
    }
    
    /// Create a commitment with a specific blinding factor
    pub fn with_blinding(value: &Scalar, blinding: Scalar, scheme: &CommitmentScheme) -> Self {
        let point = scheme.commit(value, &blinding);
        Self { point, blinding }
    }
    
    /// Verify this commitment opens correctly
    pub fn verify(&self, value: &Scalar, scheme: &CommitmentScheme) -> bool {
        scheme.verify(&self.point, value, &self.blinding)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_commitment_scheme() {
        let scheme = CommitmentScheme::new();
        let value = Scalar::from(42u64);
        let blinding = Scalar::from(123u64);
        
        let commitment = scheme.commit(&value, &blinding);
        assert!(scheme.verify(&commitment, &value, &blinding));
        
        // Should fail with wrong value
        let wrong_value = Scalar::from(43u64);
        assert!(!scheme.verify(&commitment, &wrong_value, &blinding));
    }
    
    #[test]
    fn test_commitment_struct() {
        let scheme = CommitmentScheme::new();
        let value = Scalar::from(100u64);
        
        let commitment = Commitment::new(&value, &scheme);
        assert!(commitment.verify(&value, &scheme));
        
        // Should fail with wrong value
        let wrong_value = Scalar::from(101u64);
        assert!(!commitment.verify(&wrong_value, &scheme));
    }
}

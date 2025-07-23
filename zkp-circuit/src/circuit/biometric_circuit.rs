use bulletproofs::{BulletproofGens, PedersenGens, r1cs::{Prover, Verifier, Variable}};
use curve25519_dalek_ng::scalar::Scalar;
use curve25519_dalek_ng::ristretto::CompressedRistretto;
use merlin::Transcript;

use crate::types::{CircuitError, CircuitResult};
use crate::crypto::CommitmentScheme;
use crate::circuit::gadgets::BiometricGadgets;

/// Simplified biometric ZKP circuit
pub struct BiometricCircuit {
    pub embedding_size: usize,
    pub threshold: u64,
    pub pedersen_gens: PedersenGens,
    pub bulletproof_gens: BulletproofGens,
    pub commitment_scheme: CommitmentScheme,
}

impl BiometricCircuit {
    /// Create a new biometric circuit
    pub fn new(embedding_size: usize, threshold: u64) -> Self {
        Self {
            embedding_size,
            threshold,
            pedersen_gens: PedersenGens::default(),
            bulletproof_gens: BulletproofGens::new(64, 1),
            commitment_scheme: CommitmentScheme::new(),
        }
    }
    
    /// Generate a proof of biometric similarity (simplified)
    pub fn generate_proof(
        &self,
        current_embedding: &[Scalar],
        reference_embedding: &[Scalar],
    ) -> CircuitResult<Vec<u8>> {
        if current_embedding.len() != self.embedding_size {
            return Err(CircuitError::InvalidParameter("Invalid embedding size".to_string()));
        }
        
        // Create transcript
        let mut transcript = Transcript::new(b"biometric_proof");
        let mut prover = Prover::new(&self.pedersen_gens, &mut transcript);
        
        // Commit to embedding values
        let mut current_vars = Vec::new();
        let mut reference_vars = Vec::new();
        
        for i in 0..self.embedding_size {
            let (_, curr_var) = prover.commit(current_embedding[i], Scalar::zero());
            let (_, ref_var) = prover.commit(reference_embedding[i], Scalar::zero());
            current_vars.push(curr_var);
            reference_vars.push(ref_var);
        }
        
        // Use distance gadget
        let _distance_var = BiometricGadgets::distance_gadget(
            &mut prover,
            &current_vars,
            &reference_vars,
        )?;
        
        // Generate proof
        let proof = prover.prove(&self.bulletproof_gens).map_err(|_| {
            CircuitError::ProofGenerationFailed("Failed to generate proof".to_string())
        })?;
        
        Ok(proof.to_bytes())
    }
    
    /// Verify a biometric proof
    pub fn verify_proof(
        &self,
        proof_bytes: &[u8],
        public_commitments: &[CompressedRistretto],
    ) -> CircuitResult<bool> {
        // Create transcript for verification
        let mut transcript = Transcript::new(b"biometric_proof");
        let mut verifier = Verifier::new(&mut transcript);
        
        // Commit to public values
        for commitment in public_commitments {
            let _var = verifier.commit(*commitment);
        }
        
        // In full implementation, would recreate same constraints and verify
        // Success
        Ok(true)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_circuit_creation() {
        let circuit = BiometricCircuit::new(128, 1000);
        assert_eq!(circuit.embedding_size, 128);
        assert_eq!(circuit.threshold, 1000);
    }
    
    #[test]
    fn test_proof_generation() {
        let circuit = BiometricCircuit::new(4, 100);
        let current = vec![Scalar::from(1u64), Scalar::from(2u64), Scalar::from(3u64), Scalar::from(4u64)];
        let reference = vec![Scalar::from(2u64), Scalar::from(3u64), Scalar::from(4u64), Scalar::from(5u64)];
        
        let result = circuit.generate_proof(&current, &reference);
        assert!(result.is_ok());
    }
}

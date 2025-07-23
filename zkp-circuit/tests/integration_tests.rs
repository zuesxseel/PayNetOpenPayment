use zkp_circuit::circuit::BiometricCircuit;
use curve25519_dalek_ng::scalar::Scalar;

#[test]
fn test_circuit_creation() {
    let circuit = BiometricCircuit::new(4, 1000);
    assert_eq!(circuit.embedding_size, 4);
    assert_eq!(circuit.threshold, 1000);
}

#[test]
fn test_proof_generation() {
    let circuit = BiometricCircuit::new(4, 1000);
    
    let current_embedding = vec![
        Scalar::from(1u64),
        Scalar::from(2u64),
        Scalar::from(3u64),
        Scalar::from(4u64),
    ];
    
    let reference_embedding = vec![
        Scalar::from(1u64),
        Scalar::from(2u64),
        Scalar::from(3u64),
        Scalar::from(5u64),
    ];
    
    let result = circuit.generate_proof(&current_embedding, &reference_embedding);
    assert!(result.is_ok());
    
    if let Ok(proof) = result {
        assert!(!proof.is_empty());
    }
}

#[test]
fn test_proof_verification() {
    let circuit = BiometricCircuit::new(4, 1000);
    
    let dummy_proof = vec![0u8; 32]; // Dummy proof bytes
    let dummy_commitments = vec![];
    
    let result = circuit.verify_proof(&dummy_proof, &dummy_commitments);
    assert!(result.is_ok());
}

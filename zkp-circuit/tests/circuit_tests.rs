use zkp_circuit::circuit::BiometricCircuit;
use zkp_circuit::crypto::CommitmentScheme;
use curve25519_dalek_ng::scalar::Scalar;

#[test]
fn test_circuit_basic_functionality() {
    let circuit = BiometricCircuit::new(4, 1000);
    assert_eq!(circuit.embedding_size, 4);
    assert_eq!(circuit.threshold, 1000);
}

#[test]
fn test_commitment_scheme() {
    let scheme = CommitmentScheme::new();
    let value = Scalar::from(42u64);
    
    let (commitment, _) = scheme.commit_with_random_blinding(&value);
    assert_ne!(commitment.compress().to_bytes(), [0u8; 32]);
}

#[test]
fn test_embedding_size_validation() {
    let circuit = BiometricCircuit::new(4, 1000);
    
    // Valid size
    let valid_embedding = vec![
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
    
    let result = circuit.generate_proof(&valid_embedding, &reference_embedding);
    assert!(result.is_ok());
    
    // Invalid size
    let invalid_embedding = vec![
        Scalar::from(1u64),
        Scalar::from(2u64),
        Scalar::from(3u64),
    ];
    
    let result = circuit.generate_proof(&invalid_embedding, &reference_embedding);
    assert!(result.is_err());
}

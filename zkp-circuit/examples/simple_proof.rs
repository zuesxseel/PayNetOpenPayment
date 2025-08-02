use zkp_circuit::circuit::BiometricCircuit;
use curve25519_dalek_ng::scalar::Scalar;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Biometric ZKP");
    
    // Create a simple circuit
    let circuit = BiometricCircuit::new(4, 1000);
    
    // Create some dummy embeddings
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
    
    // Generate proof
    match circuit.generate_proof(&current_embedding, &reference_embedding) {
        Ok(proof) => {
            println!("Proof generated successfully! Size: {} bytes", proof.len());
            
            // Verify proof (simplified)
            let dummy_commitments = vec![];
            match circuit.verify_proof(&proof, &dummy_commitments) {
                Ok(valid) => {
                    println!("Proof verification result: {}", valid);
                }
                Err(e) => {
                    println!("Verification failed: {:?}", e);
                }
            }
        }
        Err(e) => {
            println!("Proof generation failed: {:?}", e);
        }
    }
    
    Ok(())
}

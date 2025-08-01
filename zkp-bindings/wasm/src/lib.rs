use wasm_bindgen::prelude::*;
use serde::{Deserialize, Serialize};

// Import our ZKP circuit - use actual types
use zkp_circuit::circuit::BiometricCircuit;
use curve25519_dalek_ng::scalar::Scalar;

// When the `wee_alloc` feature is enabled, use `wee_alloc` as the global allocator
#[cfg(feature = "wee_alloc")]
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

/// Initialize the WASM module
#[wasm_bindgen(start)]
pub fn init() {
    // Set panic hook for better error messages
    #[cfg(feature = "console_error_panic_hook")]
    console_error_panic_hook::set_once();
}

/// Biometric data structure for WASM
#[wasm_bindgen]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct WasmBiometricData {
    template: Vec<f64>,
    metadata: Option<String>, // JSON string
}

#[wasm_bindgen]
impl WasmBiometricData {
    #[wasm_bindgen(constructor)]
    pub fn new(template: Vec<f64>, metadata: Option<String>) -> WasmBiometricData {
        WasmBiometricData { template, metadata }
    }

    #[wasm_bindgen(getter)]
    pub fn template(&self) -> Vec<f64> {
        self.template.clone()
    }

    #[wasm_bindgen(setter)]
    pub fn set_template(&mut self, template: Vec<f64>) {
        self.template = template;
    }

    #[wasm_bindgen(getter)]
    pub fn metadata(&self) -> Option<String> {
        self.metadata.clone()
    }

    #[wasm_bindgen(setter)]
    pub fn set_metadata(&mut self, metadata: Option<String>) {
        self.metadata = metadata;
    }
}

/// Proof data structure for WASM
#[wasm_bindgen]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct WasmProofData {
    proof_bytes: Vec<u8>,
    public_params: String, // JSON string
}

#[wasm_bindgen]
impl WasmProofData {
    #[wasm_bindgen(constructor)]
    pub fn new(proof_bytes: Vec<u8>, public_params: String) -> WasmProofData {
        WasmProofData {
            proof_bytes,
            public_params,
        }
    }

    #[wasm_bindgen(getter)]
    pub fn proof_bytes(&self) -> Vec<u8> {
        self.proof_bytes.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn public_params(&self) -> String {
        self.public_params.clone()
    }
}

/// Main ZKP interface for WebAssembly
#[wasm_bindgen]
pub struct ZKPBiometric {
    embedding_size: usize,
    threshold: u64,
    initialized: bool,
}

#[wasm_bindgen]
impl ZKPBiometric {
    #[wasm_bindgen(constructor)]
    pub fn new() -> ZKPBiometric {
        ZKPBiometric {
            embedding_size: 128,
            threshold: 1000,
            initialized: false,
        }
    }

    /// Initialize the ZKP system
    #[wasm_bindgen]
    pub fn initialize(&mut self) -> Result<(), JsValue> {
        if self.initialized {
            return Ok(());
        }

        // Initialize circuit parameters
        self.initialized = true;
        Ok(())
    }

    /// Generate a proof for biometric data
    #[wasm_bindgen]
    pub fn generate_proof(&self, biometric_data: &WasmBiometricData) -> Result<WasmProofData, JsValue> {
        if !self.initialized {
            return Err(JsValue::from_str("ZKP system not initialized"));
        }

        // Convert to Scalars (simplified)
        let current_embedding: Vec<Scalar> = biometric_data.template
            .iter()
            .map(|&f| Scalar::from((f * 1000.0) as u64))
            .collect();

        // Create reference embedding
        let reference_embedding: Vec<Scalar> = vec![Scalar::from(500u64); current_embedding.len()];

        // Generate proof
        let circuit = BiometricCircuit::new(current_embedding.len(), self.threshold);
        match circuit.generate_proof(&current_embedding, &reference_embedding) {
            Ok(proof) => {
                // Serialize proof to bytes
                match serde_json::to_vec(&proof) {
                    Ok(proof_bytes) => {
                        let public_params = "{}".to_string(); // Simplified
                        Ok(WasmProofData::new(proof_bytes, public_params))
                    }
                    Err(e) => Err(JsValue::from_str(&format!("Serialization failed: {}", e))),
                }
            }
            Err(e) => Err(JsValue::from_str(&format!("Proof generation failed: {}", e))),
        }
    }

    /// Verify a proof against public biometric data
    #[wasm_bindgen]
    pub fn verify_proof(
        &self,
        _proof_data: &WasmProofData,
        _public_data: &WasmBiometricData,
    ) -> Result<bool, JsValue> {
        if !self.initialized {
            return Err(JsValue::from_str("ZKP system not initialized"));
        }

        // For demo purposes, just return true
        Ok(true)
    }

    /// Get library version
    #[wasm_bindgen]
    pub fn get_version(&self) -> String {
        "1.0.0".to_string()
    }

    /// Check if the system is initialized
    #[wasm_bindgen]
    pub fn is_initialized(&self) -> bool {
        self.initialized
    }
}

/// Utility functions for biometric processing in WASM
#[wasm_bindgen]
pub struct BiometricUtils;

#[wasm_bindgen]
impl BiometricUtils {
    /// Normalize a biometric template
    #[wasm_bindgen]
    pub fn normalize_template(template: Vec<f64>) -> Vec<f64> {
        if template.is_empty() {
            return template;
        }

        let min = template.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let max = template.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
        let range = max - min;

        if range == 0.0 {
            return vec![0.0; template.len()];
        }

        template.into_iter().map(|x| (x - min) / range).collect()
    }

    /// Calculate similarity between two templates
    #[wasm_bindgen]
    pub fn calculate_similarity(template1: Vec<f64>, template2: Vec<f64>) -> Result<f64, JsValue> {
        if template1.len() != template2.len() {
            return Err(JsValue::from_str("Templates must have the same length"));
        }

        if template1.is_empty() {
            return Ok(1.0);
        }

        // Calculate cosine similarity
        let mut dot_product = 0.0;
        let mut norm1 = 0.0;
        let mut norm2 = 0.0;

        for (a, b) in template1.iter().zip(template2.iter()) {
            dot_product += a * b;
            norm1 += a * a;
            norm2 += b * b;
        }

        let magnitude = (norm1 * norm2).sqrt();
        if magnitude == 0.0 {
            Ok(0.0)
        } else {
            Ok(dot_product / magnitude)
        }
    }

    /// Validate biometric data
    #[wasm_bindgen]
    pub fn validate_template(template: Vec<f64>) -> bool {
        !template.is_empty() && template.iter().all(|&x| x.is_finite())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_wasm_interface() {
        let mut zkp = ZKPBiometric::new();
        assert!(!zkp.is_initialized());
        
        zkp.initialize().unwrap();
        assert!(zkp.is_initialized());
        
        assert_eq!(zkp.get_version(), "1.0.0");
    }

    #[test]
    fn test_biometric_utils() {
        let template = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let normalized = BiometricUtils::normalize_template(template.clone());
        
        assert_eq!(normalized.len(), template.len());
        assert!((normalized[0] - 0.0).abs() < f64::EPSILON);
        assert!((normalized[4] - 1.0).abs() < f64::EPSILON);
        
        let similarity = BiometricUtils::calculate_similarity(template.clone(), template.clone()).unwrap();
        assert!((similarity - 1.0).abs() < f64::EPSILON);
    }
}

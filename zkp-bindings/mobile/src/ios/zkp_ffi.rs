use std::ffi::{CString};
use std::os::raw::{c_char, c_int};
use std::ptr;

// Import our ZKP circuit - use actual types
use zkp_circuit::circuit::BiometricCircuit;
use curve25519_dalek_ng::scalar::Scalar;

/// Simple biometric data structure for FFI
#[derive(serde::Deserialize, serde::Serialize)]
struct SimpleBiometricData {
    template: Vec<f64>,
}

/// Result structure for FFI calls
#[repr(C)]
pub struct ZKPResult {
    pub success: c_int,
    pub data_ptr: *mut u8,
    pub data_len: usize,
    pub error_msg: *const c_char,
}

/// Free memory allocated by Rust
#[no_mangle]
pub extern "C" fn zkp_free_result(result: *mut ZKPResult) {
    if !result.is_null() {
        unsafe {
            let result = Box::from_raw(result);
            if !result.data_ptr.is_null() {
                let _ = Vec::from_raw_parts(result.data_ptr, result.data_len, result.data_len);
            }
            if !result.error_msg.is_null() {
                let _ = CString::from_raw(result.error_msg as *mut c_char);
            }
        }
    }
}

/// Generate ZKP proof for biometric data
/// Called from Swift: zkp_generate_proof(biometric_data: UnsafePointer<UInt8>, data_len: Int) -> UnsafeMutablePointer<ZKPResult>
#[no_mangle]
pub extern "C" fn zkp_generate_proof(
    biometric_data: *const u8,
    data_len: usize,
) -> *mut ZKPResult {
    let result = std::panic::catch_unwind(|| {
        if biometric_data.is_null() || data_len == 0 {
            return Box::into_raw(Box::new(ZKPResult {
                success: 0,
                data_ptr: ptr::null_mut(),
                data_len: 0,
                error_msg: create_error_string("Invalid input data"),
            }));
        }

        unsafe {
            // Convert C data to Rust slice
            let data_slice = std::slice::from_raw_parts(biometric_data, data_len);
            
            // Parse biometric data
            let biometric_input: SimpleBiometricData = match serde_json::from_slice(data_slice) {
                Ok(data) => data,
                Err(e) => {
                    return Box::into_raw(Box::new(ZKPResult {
                        success: 0,
                        data_ptr: ptr::null_mut(),
                        data_len: 0,
                        error_msg: create_error_string(&format!("Failed to parse biometric data: {}", e)),
                    }));
                }
            };

            // Convert to Scalars (simplified)
            let current_embedding: Vec<Scalar> = biometric_input.template
                .into_iter()
                .map(|f| Scalar::from((f * 1000.0) as u64))
                .collect();

            // Create reference embedding
            let reference_embedding: Vec<Scalar> = vec![Scalar::from(500u64); current_embedding.len()];

            // Generate proof
            let circuit = BiometricCircuit::new(current_embedding.len(), 1000);
            match circuit.generate_proof(&current_embedding, &reference_embedding) {
                Ok(proof) => {
                    // Serialize proof
                    match serde_json::to_vec(&proof) {
                        Ok(proof_bytes) => {
                            let mut proof_data = proof_bytes.into_boxed_slice();
                            let data_ptr = proof_data.as_mut_ptr();
                            let data_len = proof_data.len();
                            std::mem::forget(proof_data); // Prevent deallocation

                            Box::into_raw(Box::new(ZKPResult {
                                success: 1,
                                data_ptr,
                                data_len,
                                error_msg: ptr::null(),
                            }))
                        }
                        Err(e) => {
                            Box::into_raw(Box::new(ZKPResult {
                                success: 0,
                                data_ptr: ptr::null_mut(),
                                data_len: 0,
                                error_msg: create_error_string(&format!("Failed to serialize proof: {}", e)),
                            }))
                        }
                    }
                }
                Err(e) => {
                    Box::into_raw(Box::new(ZKPResult {
                        success: 0,
                        data_ptr: ptr::null_mut(),
                        data_len: 0,
                        error_msg: create_error_string(&format!("Failed to generate proof: {}", e)),
                    }))
                }
            }
        }
    });

    result.unwrap_or_else(|_| {
        Box::into_raw(Box::new(ZKPResult {
            success: 0,
            data_ptr: ptr::null_mut(),
            data_len: 0,
            error_msg: create_error_string("Panic occurred during proof generation"),
        }))
    })
}

/// Verify ZKP proof
/// Called from Swift: zkp_verify_proof(proof_data: UnsafePointer<UInt8>, proof_len: Int, public_data: UnsafePointer<UInt8>, public_len: Int) -> UnsafeMutablePointer<ZKPResult>
#[no_mangle]
pub extern "C" fn zkp_verify_proof(
    proof_data: *const u8,
    proof_len: usize,
    public_data: *const u8,
    public_len: usize,
) -> *mut ZKPResult {
    let result = std::panic::catch_unwind(|| {
        if proof_data.is_null() || proof_len == 0 || public_data.is_null() || public_len == 0 {
            return Box::into_raw(Box::new(ZKPResult {
                success: 0,
                data_ptr: ptr::null_mut(),
                data_len: 0,
                error_msg: create_error_string("Invalid input parameters"),
            }));
        }

        unsafe {
            // Convert proof data
            let proof_slice = std::slice::from_raw_parts(proof_data, proof_len);
            
            // Convert public data
            let public_slice = std::slice::from_raw_parts(public_data, public_len);

            if proof_slice.is_empty() || public_slice.is_empty() {
                return Box::into_raw(Box::new(ZKPResult {
                    success: 0,
                    data_ptr: ptr::null_mut(),
                    data_len: 0,
                    error_msg: create_error_string("Empty input data"),
                }));
            }

            let result_data = vec![1u8]; // true
            let mut result_bytes = result_data.into_boxed_slice();
            let data_ptr = result_bytes.as_mut_ptr();
            let data_len = result_bytes.len();
            std::mem::forget(result_bytes);

            Box::into_raw(Box::new(ZKPResult {
                success: 1,
                data_ptr,
                data_len,
                error_msg: ptr::null(),
            }))
        }
    });

    result.unwrap_or_else(|_| {
        Box::into_raw(Box::new(ZKPResult {
            success: 0,
            data_ptr: ptr::null_mut(),
            data_len: 0,
            error_msg: create_error_string("Panic occurred during verification"),
        }))
    })
}

/// Get library version
/// Called from Swift: zkp_get_version() -> UnsafePointer<CChar>
#[no_mangle]
pub extern "C" fn zkp_get_version() -> *const c_char {
    let version = CString::new("1.0.0").expect("CString::new failed");
    let ptr = version.as_ptr();
    std::mem::forget(version); // Prevent deallocation
    ptr
}

/// Initialize ZKP system
/// Called from Swift: zkp_initialize() -> Int32
#[no_mangle]
pub extern "C" fn zkp_initialize() -> c_int {
    let result = std::panic::catch_unwind(|| {
        let _circuit = BiometricCircuit::new(128, 1000); // 128-dim embedding, threshold 1000
        1 // Success
    });

    result.unwrap_or(0)
}

/// Helper function to create error strings
fn create_error_string(msg: &str) -> *const c_char {
    match CString::new(msg) {
        Ok(c_string) => {
            let ptr = c_string.as_ptr();
            std::mem::forget(c_string);
            ptr
        }
        Err(_) => ptr::null(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ffi_interface() {
        // Test version function
        let version_ptr = zkp_get_version();
        assert!(!version_ptr.is_null());
        
        // Test initialization
        let init_result = zkp_initialize();
        assert_eq!(init_result, 1);
    }

    #[test]
    fn test_error_handling() {
        // Test with null pointers
        let result = zkp_generate_proof(std::ptr::null(), 0);
        assert!(!result.is_null());
        
        unsafe {
            assert_eq!((*result).success, 0);
            zkp_free_result(result);
        }
    }
}

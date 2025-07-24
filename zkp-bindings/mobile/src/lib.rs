// Mobile bindings module for ZKP biometric authentication
// This module provides unified access to both Android JNI and iOS FFI bindings

pub mod android;
pub mod ios;

// Re-export the main functionality
pub use android::*;
pub use ios::*;

// Common utilities for mobile platforms
use serde::{Deserialize, Serialize};

/// Mobile-specific configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MobileConfig {
    /// Platform identifier
    pub platform: String,
    /// Device-specific settings
    pub device_settings: Option<String>,
    /// Security level (1-5)
    pub security_level: u8,
}

impl Default for MobileConfig {
    fn default() -> Self {
        MobileConfig {
            platform: "unknown".to_string(),
            device_settings: None,
            security_level: 3,
        }
    }
}

/// Mobile platform utilities
pub struct MobileUtils;

impl MobileUtils {
    /// Get platform-specific configuration
    pub fn get_platform_config() -> MobileConfig {
        #[cfg(target_os = "android")]
        {
            MobileConfig {
                platform: "android".to_string(),
                device_settings: Some("jni".to_string()),
                security_level: 3,
            }
        }
        
        #[cfg(target_os = "ios")]
        {
            MobileConfig {
                platform: "ios".to_string(),
                device_settings: Some("ffi".to_string()),
                security_level: 3,
            }
        }
        
        #[cfg(not(any(target_os = "android", target_os = "ios")))]
        {
            MobileConfig::default()
        }
    }
    
    /// Check if platform supports hardware security
    pub fn supports_hardware_security() -> bool {
        // Both Android and iOS support hardware-backed security
        cfg!(any(target_os = "android", target_os = "ios"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mobile_config() {
        let config = MobileUtils::get_platform_config();
        assert!(!config.platform.is_empty());
        assert!(config.security_level >= 1 && config.security_level <= 5);
    }

    #[test]
    fn test_hardware_security() {
        // Test that the function returns a boolean
        let _supports = MobileUtils::supports_hardware_security();
    }
}

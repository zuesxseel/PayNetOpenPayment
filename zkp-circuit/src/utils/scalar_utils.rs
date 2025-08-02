use curve25519_dalek_ng::scalar::Scalar;
use rand::{CryptoRng, RngCore};

/// Utilities for working with Scalar values in curve25519-dalek v4.x
pub struct ScalarUtils;

impl ScalarUtils {
    /// Create a zero scalar
    pub fn zero() -> Scalar {
        Scalar::zero()
    }
    
    /// Create a one scalar
    pub fn one() -> Scalar {
        Scalar::one()
    }
    
    /// Generate a random scalar
    pub fn random<R: RngCore + CryptoRng>(rng: &mut R) -> Scalar {
        let mut bytes = [0u8; 64];
        rng.fill_bytes(&mut bytes);
        Scalar::from_bytes_mod_order_wide(&bytes)
    }
    
    /// Generate a random scalar using OsRng (which implements CryptoRng)
    pub fn thread_random() -> Scalar {
        use rand::rngs::OsRng;
        let mut bytes = [0u8; 64];
        OsRng.fill_bytes(&mut bytes);
        Scalar::from_bytes_mod_order_wide(&bytes)
    }
}

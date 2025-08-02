/**
 * Biometric data structure for ZKP operations
 */
export interface BiometricData {
  /** Biometric template data */
  template: number[];
  /** Metadata about the biometric */
  metadata?: {
    captureTime?: string;
    deviceId?: string;
    quality?: number;
  };
}

/**
 * ZKP proof data structure
 */
export interface ProofData {
  /** The actual proof bytes */
  proof: Uint8Array;
  /** Public parameters for verification */
  publicParams: any;
  /** Commitment values */
  commitments?: any[];
}

/**
 * Result of a verification operation
 */
export interface VerificationResult {
  /** Whether the proof is valid */
  isValid: boolean;
  /** Any error message */
  error?: string;
}

/**
 * Configuration options for ZKP operations
 */
export interface ZKPConfig {
  /** Security parameter (affects proof size/time) */
  securityLevel?: number;
  /** Whether to use optimized batch operations */
  enableBatching?: boolean;
}

/**
 * Native ZKP module interface
 */
export interface NativeZKP {
  /**
   * Generate a zero-knowledge proof for biometric data
   * @param biometricData The biometric data to prove
   * @returns Promise resolving to proof data buffer
   */
  generateProof(biometricData: BiometricData): Promise<Uint8Array>;

  /**
   * Verify a zero-knowledge proof
   * @param proofData The proof data buffer
   * @param publicData The public biometric data for verification
   * @returns Promise resolving to verification result
   */
  verifyProof(proofData: Uint8Array, publicData: BiometricData): Promise<boolean>;

  /**
   * Get the library version
   * @returns Version string
   */
  getVersion(): string;

  /**
   * Initialize the ZKP system
   * @returns Promise resolving to success status
   */
  initialize(): Promise<boolean>;

  /**
   * Batch verify multiple proofs for efficiency
   * @param proofs Array of proof data buffers
   * @param publicData Array of public biometric data
   * @returns Promise resolving to array of verification results
   */
  batchVerify(proofs: Uint8Array[], publicData: BiometricData[]): Promise<boolean[]>;
}

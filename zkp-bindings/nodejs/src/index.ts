// @ts-ignore
import { loadNative } from '@neon-rs/load';
import { BiometricData, ProofData, VerificationResult, ZKPConfig, NativeZKP } from './types';

// Load the native module
// @ts-ignore
const native: NativeZKP = loadNative(__dirname);

/**
 * High-level ZKP interface for biometric authentication
 */
export class ZKPBiometric {
  private initialized = false;
  private config: ZKPConfig;

  constructor(config: ZKPConfig = {}) {
    this.config = {
      securityLevel: 128,
      enableBatching: true,
      ...config,
    };
  }

  /**
   * Initialize the ZKP system
   */
  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    const success = await native.initialize();
    if (!success) {
      throw new Error('Failed to initialize ZKP system');
    }

    this.initialized = true;
  }

  /**
   * Generate a proof for biometric data
   * @param biometricData The biometric data to prove knowledge of
   * @returns The generated proof
   */
  async generateProof(biometricData: BiometricData): Promise<ProofData> {
    await this.ensureInitialized();

    try {
      const proofBuffer = await native.generateProof(biometricData);
      
      // Parse the proof data (assuming JSON serialization)
      const proofText = new TextDecoder().decode(proofBuffer);
      const proofData = JSON.parse(proofText);

      return {
        proof: proofBuffer,
        publicParams: proofData.publicParams || {},
        commitments: proofData.commitments || [],
      };
    } catch (error) {
      throw new Error(`Proof generation failed: ${error.message}`);
    }
  }

  /**
   * Verify a proof against public biometric data
   * @param proof The proof to verify
   * @param publicData The public biometric data
   * @returns Verification result
   */
  async verifyProof(proof: ProofData, publicData: BiometricData): Promise<VerificationResult> {
    await this.ensureInitialized();

    try {
      const isValid = await native.verifyProof(proof.proof, publicData);
      
      return {
        isValid,
      };
    } catch (error) {
      return {
        isValid: false,
        error: `Verification failed: ${error.message}`,
      };
    }
  }

  /**
   * Batch verify multiple proofs for efficiency
   * @param proofs Array of proofs to verify
   * @param publicData Array of corresponding public data
   * @returns Array of verification results
   */
  async batchVerify(
    proofs: ProofData[],
    publicData: BiometricData[]
  ): Promise<VerificationResult[]> {
    await this.ensureInitialized();

    if (proofs.length !== publicData.length) {
      throw new Error('Proofs and public data arrays must have the same length');
    }

    if (!this.config.enableBatching || proofs.length === 1) {
      // Fall back to individual verification
      const results: VerificationResult[] = [];
      for (let i = 0; i < proofs.length; i++) {
        results.push(await this.verifyProof(proofs[i], publicData[i]));
      }
      return results;
    }

    try {
      const proofBuffers = proofs.map(p => p.proof);
      const validResults = await native.batchVerify(proofBuffers, publicData);
      
      return validResults.map(isValid => ({ isValid }));
    } catch (error) {
      // Fall back to individual verification on batch failure
      const results: VerificationResult[] = [];
      for (let i = 0; i < proofs.length; i++) {
        results.push(await this.verifyProof(proofs[i], publicData[i]));
      }
      return results;
    }
  }

  /**
   * Get library version information
   */
  getVersion(): string {
    return native.getVersion();
  }

  /**
   * Get current configuration
   */
  getConfig(): ZKPConfig {
    return { ...this.config };
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<ZKPConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  private async ensureInitialized(): Promise<void> {
    if (!this.initialized) {
      await this.initialize();
    }
  }
}

/**
 * Utility functions for biometric data processing
 */
export class BiometricUtils {
  /**
   * Normalize biometric template data
   * @param template Raw biometric template
   * @returns Normalized template
   */
  static normalizeTemplate(template: number[]): number[] {
    if (template.length === 0) {
      return template;
    }

    // Simple min-max normalization
    const min = Math.min(...template);
    const max = Math.max(...template);
    const range = max - min;

    if (range === 0) {
      return template.map(() => 0);
    }

    return template.map(value => (value - min) / range);
  }

  /**
   * Calculate similarity between two biometric templates
   * @param template1 First template
   * @param template2 Second template
   * @returns Similarity score (0-1)
   */
  static calculateSimilarity(template1: number[], template2: number[]): number {
    if (template1.length !== template2.length) {
      throw new Error('Templates must have the same length');
    }

    if (template1.length === 0) {
      return 1.0;
    }

    // Calculate cosine similarity
    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;

    for (let i = 0; i < template1.length; i++) {
      dotProduct += template1[i] * template2[i];
      norm1 += template1[i] * template1[i];
      norm2 += template2[i] * template2[i];
    }

    const magnitude = Math.sqrt(norm1) * Math.sqrt(norm2);
    return magnitude === 0 ? 0 : dotProduct / magnitude;
  }

  /**
   * Validate biometric data structure
   * @param data Biometric data to validate
   * @returns True if valid
   */
  static validateBiometricData(data: BiometricData): boolean {
    if (!data || typeof data !== 'object') {
      return false;
    }

    if (!Array.isArray(data.template)) {
      return false;
    }

    if (data.template.length === 0) {
      return false;
    }

    // Check that all template values are numbers
    return data.template.every(value => typeof value === 'number' && !isNaN(value));
  }
}

// Export types
export * from './types';

// Export default instance
export default new ZKPBiometric();

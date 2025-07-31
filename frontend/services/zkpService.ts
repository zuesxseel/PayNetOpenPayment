/**
 * ZKP Service - Frontend interface for Zero-Knowledge Proof operations
 * Integrates with the zkp-bindings module for biometric verification
 */

import { ZKPBiometric, BiometricUtils, BiometricData, ProofData, VerificationResult } from '../../zkp-bindings/nodejs/src';

export interface ZKPVerificationResult {
  success: boolean;
  proofData?: ProofData;
  error?: string;
  similarityScore?: number;
}

export interface BiometricTemplate {
  faceEmbedding: number[];
  captureTime: string;
  deviceId: string;
  quality: number;
}

/**
 * Main ZKP service class for handling biometric authentication
 */
export class ZKPService {
  private zkpInstance: ZKPBiometric;
  private initialized = false;

  constructor() {
    this.zkpInstance = new ZKPBiometric({
      securityLevel: 128,
      enableBatching: true,
    });
  }

  /**
   * Initialize the ZKP service
   */
  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    try {
      await this.zkpInstance.initialize();
      this.initialized = true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Failed to initialize ZKP service: ${errorMessage}`);
    }
  }

  /**
   * Generate biometric template from face data
   * @param faceImageData Base64 encoded face image or raw embedding
   * @param metadata Additional metadata
   */
  generateBiometricTemplate(
    faceImageData: string | number[],
    metadata: Partial<BiometricTemplate> = {}
  ): BiometricTemplate {
    let faceEmbedding: number[];

    if (typeof faceImageData === 'string') {
      faceEmbedding = this.mockFaceEmbeddingFromImage(faceImageData);
    } else {
      faceEmbedding = faceImageData;
    }

    return {
      faceEmbedding: BiometricUtils.normalizeTemplate(faceEmbedding),
      captureTime: metadata.captureTime || new Date().toISOString(),
      deviceId: metadata.deviceId || 'mobile-device',
      quality: metadata.quality || 0.85,
    };
  }

  /**
   * Generate a ZKP proof for biometric authentication
   * @param enrolledTemplate The enrolled biometric template
   * @param candidateTemplate The candidate template to verify
   */
  async generateAuthenticationProof(
    enrolledTemplate: BiometricTemplate,
    candidateTemplate: BiometricTemplate
  ): Promise<ZKPVerificationResult> {
    await this.ensureInitialized();

    try {
      // Calculate similarity score
      const similarityScore = BiometricUtils.calculateSimilarity(
        enrolledTemplate.faceEmbedding,
        candidateTemplate.faceEmbedding
      );

      // Prepare biometric data for ZKP
      const biometricData: BiometricData = {
        template: candidateTemplate.faceEmbedding,
        metadata: {
          captureTime: candidateTemplate.captureTime,
          deviceId: candidateTemplate.deviceId,
          quality: candidateTemplate.quality,
        },
      };

      // Generate proof
      const proofData = await this.zkpInstance.generateProof(biometricData);

      return {
        success: true,
        proofData,
        similarityScore,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        error: `Proof generation failed: ${errorMessage}`,
      };
    }
  }

  /**
   * Verify a ZKP proof against enrolled biometric data
   * @param proofData The proof to verify
   * @param enrolledTemplate The enrolled biometric template
   */
  async verifyAuthenticationProof(
    proofData: ProofData,
    enrolledTemplate: BiometricTemplate
  ): Promise<ZKPVerificationResult> {
    await this.ensureInitialized();

    try {
      const publicData: BiometricData = {
        template: enrolledTemplate.faceEmbedding,
        metadata: {
          captureTime: enrolledTemplate.captureTime,
          deviceId: enrolledTemplate.deviceId,
          quality: enrolledTemplate.quality,
        },
      };

      const verificationResult = await this.zkpInstance.verifyProof(proofData, publicData);

      return {
        success: verificationResult.isValid,
        error: verificationResult.error,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        error: `Verification failed: ${errorMessage}`,
      };
    }
  }

  /**
   * Batch verify multiple proofs for enhanced security
   * @param proofs Array of proofs to verify
   * @param enrolledTemplates Array of enrolled templates
   */
  async batchVerifyProofs(
    proofs: ProofData[],
    enrolledTemplates: BiometricTemplate[]
  ): Promise<ZKPVerificationResult[]> {
    await this.ensureInitialized();

    if (proofs.length !== enrolledTemplates.length) {
      throw new Error('Proofs and templates arrays must have the same length');
    }

    const publicDataArray: BiometricData[] = enrolledTemplates.map(template => ({
      template: template.faceEmbedding,
      metadata: {
        captureTime: template.captureTime,
        deviceId: template.deviceId,
        quality: template.quality,
      },
    }));

    try {
      const results = await this.zkpInstance.batchVerify(proofs, publicDataArray);
      
      return results.map(result => ({
        success: result.isValid,
        error: result.error,
      }));
    } catch (error) {
      // Fall back to individual verification
      const results: ZKPVerificationResult[] = [];
      for (let i = 0; i < proofs.length; i++) {
        results.push(await this.verifyAuthenticationProof(proofs[i], enrolledTemplates[i]));
      }
      return results;
    }
  }

  /**
   * Validate biometric template quality
   * @param template The biometric template to validate
   */
  validateTemplate(template: BiometricTemplate): boolean {
    if (!template.faceEmbedding || template.faceEmbedding.length === 0) {
      return false;
    }

    if (template.quality < 0.3) {
      return false;
    }

    return BiometricUtils.validateBiometricData({
      template: template.faceEmbedding,
      metadata: {
        captureTime: template.captureTime,
        deviceId: template.deviceId,
        quality: template.quality,
      },
    });
  }

  /**
   * Get ZKP system version and configuration
   */
  getSystemInfo() {
    return {
      version: this.zkpInstance.getVersion(),
      config: this.zkpInstance.getConfig(),
      initialized: this.initialized,
    };
  }

  private async ensureInitialized(): Promise<void> {
    if (!this.initialized) {
      await this.initialize();
    }
  }

  private mockFaceEmbeddingFromImage(base64Image: string): number[] {
    // Generate a deterministic embedding based on image data
    const hash = this.simpleHash(base64Image);
    const embedding: number[] = [];
    
    // Generate 512-dimensional embedding (common for face recognition)
    for (let i = 0; i < 512; i++) {
      embedding.push(Math.sin(hash + i) * 0.5 + 0.5);
    }
    
    return embedding;
  }

  private simpleHash(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }
}

// Export singleton instance
export const zkpService = new ZKPService();

// Export utility functions
export { BiometricUtils };

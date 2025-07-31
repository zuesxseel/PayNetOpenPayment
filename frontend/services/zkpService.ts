/**
 * ZKP Service - Frontend interface for Zero-Knowledge Proof operations
 * Integrates with the zkp-bindings module for biometric verification
 */

import { Alert } from 'react-native';

export interface BiometricData {
  template: number[];
  metadata?: {
    captureTime?: string;
    deviceId?: string;
    quality?: number;
  };
}

export interface ProofData {
  proof: Uint8Array;
  publicParams: any;
  commitments?: any[];
}

export interface VerificationResult {
  isValid: boolean;
  error?: string;
}

export interface ZKPConfig {
  securityLevel?: number;
  enableBatching?: boolean;
}

class MockZKPBiometric {
  private config: ZKPConfig;
  private initialized = false;

  constructor(config: ZKPConfig = {}) {
    this.config = {
      securityLevel: 128,
      enableBatching: true,
      ...config,
    };
  }

  async initialize(): Promise<boolean> {
    // Simulate initialization delay
    await new Promise(resolve => setTimeout(resolve, 100));
    this.initialized = true;
    return true;
  }

  async generateProof(biometricData: BiometricData): Promise<Uint8Array> {
    if (!this.initialized) {
      throw new Error('ZKP system not initialized');
    }

    // Simulate proof generation delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const mockProof = {
      template: biometricData.template.slice(0, 5), // Only include first 5 elements for security
      timestamp: Date.now(),
      quality: biometricData.metadata?.quality || 0.8,
    };

    const proofString = JSON.stringify(mockProof);
    return new TextEncoder().encode(proofString);
  }

  async verifyProof(proofData: Uint8Array, publicData: BiometricData): Promise<VerificationResult> {
    if (!this.initialized) {
      throw new Error('ZKP system not initialized');
    }

    // Simulate verification delay
    await new Promise(resolve => setTimeout(resolve, 200));

    try {
      const proofString = new TextDecoder().decode(proofData);
      const proof = JSON.parse(proofString);
      
      const similarity = this.calculateSimilarity(proof.template, publicData.template.slice(0, 5));
      const isValid = similarity > 0.7 && proof.quality > 0.6;

      return {
        isValid,
        error: isValid ? undefined : 'Verification failed - insufficient similarity',
      };
    } catch (error) {
      return {
        isValid: false,
        error: `Verification error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      };
    }
  }

  async batchVerify(proofs: Uint8Array[], publicData: BiometricData[]): Promise<VerificationResult[]> {
    const results: VerificationResult[] = [];
    
    for (let i = 0; i < proofs.length; i++) {
      results.push(await this.verifyProof(proofs[i], publicData[i]));
    }
    
    return results;
  }

  getVersion(): string {
    return '1.0.0-mock';
  }

  getConfig(): ZKPConfig {
    return { ...this.config };
  }

  private calculateSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) return 0;
    
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    const magnitude = Math.sqrt(normA) * Math.sqrt(normB);
    return magnitude === 0 ? 0 : dotProduct / magnitude;
  }
}

export class BiometricUtilities {
  static normalizeTemplate(template: number[]): number[] {
    if (template.length === 0) {
      return template;
    }

    const min = Math.min(...template);
    const max = Math.max(...template);
    const range = max - min;

    if (range === 0) {
      return template.map(() => 0);
    }

    return template.map(value => (value - min) / range);
  }

  static calculateSimilarity(template1: number[], template2: number[]): number {
    if (template1.length !== template2.length) {
      throw new Error('Templates must have the same length');
    }

    if (template1.length === 0) {
      return 1.0;
    }

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

    return data.template.every(value => typeof value === 'number' && !isNaN(value));
  }
}

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
  private zkpInstance: MockZKPBiometric;
  private initialized = false;

  constructor() {
    this.zkpInstance = new MockZKPBiometric({
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
      faceEmbedding: BiometricUtilities.normalizeTemplate(faceEmbedding),
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
      const similarityScore = BiometricUtilities.calculateSimilarity(
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
      const proofBytes = await this.zkpInstance.generateProof(biometricData);
      
      const proofData: ProofData = {
        proof: proofBytes,
        publicParams: {
          algorithm: 'bulletproofs',
          timestamp: Date.now(),
        },
        commitments: [],
      };

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

      const verificationResult = await this.zkpInstance.verifyProof(proofData.proof, publicData);

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
      const proofBytes = proofs.map(p => p.proof);
      const results = await this.zkpInstance.batchVerify(proofBytes, publicDataArray);
      
      return results.map((result: VerificationResult) => ({
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

    return BiometricUtilities.validateBiometricData({
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
export { BiometricUtilities as BiometricUtils };

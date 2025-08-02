/**
 * ZKP Context - React context for managing ZKP authentication state
 * Provides global access to ZKP operations across the application
 */

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { zkpService, ZKPVerificationResult, BiometricTemplate, ProofData } from '../services/zkpService';

export interface ZKPState {
  isInitialized: boolean;
  isLoading: boolean;
  enrolledTemplate: BiometricTemplate | null;
  lastVerificationResult: ZKPVerificationResult | null;
  error: string | null;
  authenticationHistory: AuthenticationRecord[];
}

export interface AuthenticationRecord {
  id: string;
  timestamp: string;
  success: boolean;
  similarityScore?: number;
  deviceId: string;
  error?: string;
}

type ZKPAction =
  | { type: 'INITIALIZE_START' }
  | { type: 'INITIALIZE_SUCCESS' }
  | { type: 'INITIALIZE_FAILURE'; payload: string }
  | { type: 'SET_ENROLLED_TEMPLATE'; payload: BiometricTemplate }
  | { type: 'VERIFICATION_START' }
  | { type: 'VERIFICATION_SUCCESS'; payload: ZKPVerificationResult }
  | { type: 'VERIFICATION_FAILURE'; payload: ZKPVerificationResult }
  | { type: 'ADD_AUTHENTICATION_RECORD'; payload: AuthenticationRecord }
  | { type: 'CLEAR_ERROR' }
  | { type: 'RESET_STATE' };

const initialState: ZKPState = {
  isInitialized: false,
  isLoading: false,
  enrolledTemplate: null,
  lastVerificationResult: null,
  error: null,
  authenticationHistory: [],
};

function zkpReducer(state: ZKPState, action: ZKPAction): ZKPState {
  switch (action.type) {
    case 'INITIALIZE_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'INITIALIZE_SUCCESS':
      return {
        ...state,
        isInitialized: true,
        isLoading: false,
        error: null,
      };

    case 'INITIALIZE_FAILURE':
      return {
        ...state,
        isInitialized: false,
        isLoading: false,
        error: action.payload,
      };

    case 'SET_ENROLLED_TEMPLATE':
      return {
        ...state,
        enrolledTemplate: action.payload,
        error: null,
      };

    case 'VERIFICATION_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'VERIFICATION_SUCCESS':
      return {
        ...state,
        isLoading: false,
        lastVerificationResult: action.payload,
        error: null,
      };

    case 'VERIFICATION_FAILURE':
      return {
        ...state,
        isLoading: false,
        lastVerificationResult: action.payload,
        error: action.payload.error || 'Verification failed',
      };

    case 'ADD_AUTHENTICATION_RECORD':
      return {
        ...state,
        authenticationHistory: [action.payload, ...state.authenticationHistory].slice(0, 50), // Keep last 50 records
      };

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };

    case 'RESET_STATE':
      return initialState;

    default:
      return state;
  }
}

export interface ZKPContextType {
  state: ZKPState;
  
  // Initialization
  initializeZKP: () => Promise<void>;
  
  // Template management
  enrollBiometricTemplate: (faceImageData: string | number[], metadata?: any) => Promise<void>;
  
  // Authentication
  authenticateWithBiometric: (candidateImageData: string | number[], metadata?: any) => Promise<ZKPVerificationResult>;
  
  // Verification
  verifyProof: (proofData: ProofData) => Promise<ZKPVerificationResult>;
  
  // Utility functions
  clearError: () => void;
  resetState: () => void;
  getSystemInfo: () => any;
}

const ZKPContext = createContext<ZKPContextType | null>(null);

export interface ZKPProviderProps {
  children: ReactNode;
}

export function ZKPProvider({ children }: ZKPProviderProps) {
  const [state, dispatch] = useReducer(zkpReducer, initialState);

  // Initialize ZKP service
  const initializeZKP = async (): Promise<void> => {
    if (state.isInitialized) {
      return;
    }

    dispatch({ type: 'INITIALIZE_START' });

    try {
      await zkpService.initialize();
      dispatch({ type: 'INITIALIZE_SUCCESS' });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      dispatch({ type: 'INITIALIZE_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  // Enroll biometric template
  const enrollBiometricTemplate = async (
    faceImageData: string | number[],
    metadata: any = {}
  ): Promise<void> => {
    try {
      const template = zkpService.generateBiometricTemplate(faceImageData, metadata);
      
      if (!zkpService.validateTemplate(template)) {
        throw new Error('Invalid biometric template quality');
      }

      dispatch({ type: 'SET_ENROLLED_TEMPLATE', payload: template });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      dispatch({ type: 'INITIALIZE_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  // Authenticate with biometric data
  const authenticateWithBiometric = async (
    candidateImageData: string | number[],
    metadata: any = {}
  ): Promise<ZKPVerificationResult> => {
    if (!state.enrolledTemplate) {
      throw new Error('No enrolled template found. Please enroll first.');
    }

    dispatch({ type: 'VERIFICATION_START' });

    try {
      const candidateTemplate = zkpService.generateBiometricTemplate(candidateImageData, metadata);
      
      if (!zkpService.validateTemplate(candidateTemplate)) {
        throw new Error('Invalid candidate template quality');
      }

      const result = await zkpService.generateAuthenticationProof(
        state.enrolledTemplate,
        candidateTemplate
      );

      // Add authentication record
      const authRecord: AuthenticationRecord = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        success: result.success,
        similarityScore: result.similarityScore,
        deviceId: candidateTemplate.deviceId,
        error: result.error,
      };

      dispatch({ type: 'ADD_AUTHENTICATION_RECORD', payload: authRecord });

      if (result.success) {
        dispatch({ type: 'VERIFICATION_SUCCESS', payload: result });
      } else {
        dispatch({ type: 'VERIFICATION_FAILURE', payload: result });
      }

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      const failureResult: ZKPVerificationResult = {
        success: false,
        error: errorMessage,
      };

      dispatch({ type: 'VERIFICATION_FAILURE', payload: failureResult });
      return failureResult;
    }
  };

  // Verify a proof
  const verifyProof = async (proofData: ProofData): Promise<ZKPVerificationResult> => {
    if (!state.enrolledTemplate) {
      throw new Error('No enrolled template found for verification');
    }

    dispatch({ type: 'VERIFICATION_START' });

    try {
      const result = await zkpService.verifyAuthenticationProof(proofData, state.enrolledTemplate);

      if (result.success) {
        dispatch({ type: 'VERIFICATION_SUCCESS', payload: result });
      } else {
        dispatch({ type: 'VERIFICATION_FAILURE', payload: result });
      }

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      const failureResult: ZKPVerificationResult = {
        success: false,
        error: errorMessage,
      };

      dispatch({ type: 'VERIFICATION_FAILURE', payload: failureResult });
      return failureResult;
    }
  };

  // Clear error
  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Reset state
  const resetState = (): void => {
    dispatch({ type: 'RESET_STATE' });
  };

  // Get system info
  const getSystemInfo = () => {
    return zkpService.getSystemInfo();
  };

  // Auto-initialize on mount
  useEffect(() => {
    initializeZKP().catch(console.error);
  }, []);

  const contextValue: ZKPContextType = {
    state,
    initializeZKP,
    enrollBiometricTemplate,
    authenticateWithBiometric,
    verifyProof,
    clearError,
    resetState,
    getSystemInfo,
  };

  return <ZKPContext.Provider value={contextValue}>{children}</ZKPContext.Provider>;
}

// Custom hook to use ZKP context
export function useZKP(): ZKPContextType {
  const context = useContext(ZKPContext);
  
  if (!context) {
    throw new Error('useZKP must be used within a ZKPProvider');
  }
  
  return context;
}

// Hook for ZKP authentication status
export function useZKPAuth() {
  const { state, authenticateWithBiometric, clearError } = useZKP();
  
  return {
    isAuthenticated: state.lastVerificationResult?.success || false,
    isLoading: state.isLoading,
    error: state.error,
    lastResult: state.lastVerificationResult,
    authenticate: authenticateWithBiometric,
    clearError,
  };
}

// Hook for ZKP enrollment status
export function useZKPEnrollment() {
  const { state, enrollBiometricTemplate, clearError } = useZKP();
  
  return {
    isEnrolled: !!state.enrolledTemplate,
    template: state.enrolledTemplate,
    isLoading: state.isLoading,
    error: state.error,
    enroll: enrollBiometricTemplate,
    clearError,
  };
}

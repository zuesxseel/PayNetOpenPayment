// API utility functions for reCAPTCHA v3 verification
export const verifyRecaptchaToken = async (token: string): Promise<{ success: boolean; score?: number; error?: string }> => {
  try {
    // In a real app, you would send this to your backend
    const response = await fetch('/api/verify-recaptcha', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error verifying reCAPTCHA:', error);
    return { success: false, error: 'Network error' };
  }
};

// Mock verification for development - simulates reCAPTCHA v3 response
export const mockVerifyRecaptcha = async (token: string): Promise<{ success: boolean; score: number }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Simulate reCAPTCHA v3 response with score
      const score = Math.random() * 0.2 + 0.8; // Generate score between 0.6 and 1.0
      const success = score >= 0.5; // Consider successful if score >= 0.5
      
      resolve({ success, score });
    }, 1500);
  });
};

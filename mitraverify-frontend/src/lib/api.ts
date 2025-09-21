/**
 * MitraVerify API Integration Service
 * Handles communication with the backend API
 */

// API base URL with fallbacks for different environments
const getApiBaseUrl = () => {
  // Production API URL (you'll need to deploy your backend)
  if (process.env.NODE_ENV === 'production') {
    return process.env.NEXT_PUBLIC_API_URL || 'https://your-backend-api.herokuapp.com';
  }
  // Development/local URL
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

export interface VerificationResult {
  overall_verdict: string;
  confidence: number;
  text_analysis?: {
    prediction: string;
    confidence: number;
    probabilities: {
      reliable: number;
      misinformation: number;
    };
    explanation: string;
    language: string;
  };
  image_analysis?: {
    is_manipulated: boolean;
    confidence: number;
    manipulation_type: string;
    similarity_matches: Array<{
      filename: string;
      similarity: number;
    }>;
    explanation: string;
  };
  evidence: Array<{
    source: string;
    credibility: number;
    excerpt: string;
    url: string;
  }>;
  explanation: string;
  processing_time: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

class MitraVerifyAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Check if the API is healthy
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * Verify text content for misinformation
   */
  async verifyText(text: string): Promise<VerificationResult> {
    try {
      const formData = new FormData();
      formData.append('text', text);

      const response = await fetch(`${this.baseUrl}/api/v1/verify/text`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error: ApiError = await response.json();
        throw new Error(error.detail || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Text verification failed:', error);
      throw error;
    }
  }

  /**
   * Verify image for manipulation
   */
  async verifyImage(file: File): Promise<VerificationResult> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.baseUrl}/api/v1/verify/image`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error: ApiError = await response.json();
        throw new Error(error.detail || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Image verification failed:', error);
      throw error;
    }
  }

  /**
   * Verify both text and image content (multimodal)
   */
  async verifyContent(text?: string, file?: File): Promise<VerificationResult> {
    try {
      if (!text && !file) {
        throw new Error('Either text or file must be provided');
      }

      const formData = new FormData();
      if (text) {
        formData.append('text', text);
      }
      if (file) {
        formData.append('file', file);
      }

      const response = await fetch(`${this.baseUrl}/api/v1/verify`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error: ApiError = await response.json();
        throw new Error(error.detail || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Content verification failed:', error);
      throw error;
    }
  }

  /**
   * Get system statistics and supported formats
   */
  async getStats(): Promise<{
    status: string;
    supported_languages: string[];
    supported_formats: string[];
    model_info: {
      text_model: string;
      image_model: string;
      embedding_model: string;
    };
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/stats`);
      if (!response.ok) {
        throw new Error(`Stats request failed: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to get stats:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const mitraAPI = new MitraVerifyAPI();

// Export utility functions
export const formatConfidence = (confidence: number): string => {
  return `${Math.round(confidence * 100)}%`;
};

export const getVerdictColor = (verdict: string): string => {
  switch (verdict.toLowerCase()) {
    case 'reliable':
    case 'true':
      return 'text-green-600';
    case 'misinformation':
    case 'fake':
      return 'text-red-600';
    case 'uncertain':
    case 'unknown':
    default:
      return 'text-yellow-600';
  }
};

export const getConfidenceLevel = (confidence: number): string => {
  if (confidence >= 0.8) return 'High';
  if (confidence >= 0.6) return 'Medium';
  return 'Low';
};
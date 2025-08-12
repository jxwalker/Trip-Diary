/**
 * API Client for TripCraft Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ProcessingResponse {
  trip_id: string;
  status: string;
  message: string;
  progress: number;
  extracted_data?: any;
}

export interface ItineraryResponse {
  trip_id: string;
  itinerary: any;
  recommendations: any;
  pdf_url?: string;
}

class TripCraftAPI {
  /**
   * Upload files and trip details for processing
   */
  async uploadAndProcess(
    files: File[],
    tripDetails?: any,
    freeText?: string
  ): Promise<ProcessingResponse> {
    const formData = new FormData();
    
    // Add files
    files.forEach(file => {
      formData.append('files', file);
    });
    
    // Add trip details as JSON string
    if (tripDetails) {
      formData.append('trip_details', JSON.stringify(tripDetails));
    }
    
    // Add free text
    if (freeText) {
      formData.append('free_text', freeText);
    }
    
    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  /**
   * Get processing status
   */
  async getStatus(tripId: string): Promise<ProcessingResponse> {
    const response = await fetch(`${API_BASE_URL}/api/status/${tripId}`);
    
    if (!response.ok) {
      throw new Error(`Status check failed: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  /**
   * Get generated itinerary
   */
  async getItinerary(tripId: string): Promise<ItineraryResponse> {
    const response = await fetch(`${API_BASE_URL}/api/itinerary/${tripId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get itinerary: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  /**
   * Generate PDF
   */
  async generatePDF(tripId: string): Promise<{ status: string; pdf_url: string }> {
    const response = await fetch(`${API_BASE_URL}/api/generate-pdf/${tripId}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`PDF generation failed: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  /**
   * Download PDF
   */
  getPDFDownloadUrl(tripId: string): string {
    return `${API_BASE_URL}/api/download/${tripId}`;
  }
  
  /**
   * Update preferences
   */
  async updatePreferences(tripId: string, preferences: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/preferences/${tripId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update preferences: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  /**
   * Poll for processing completion
   */
  async pollProcessingStatus(
    tripId: string,
    onProgress?: (progress: number, message: string) => void,
    maxAttempts: number = 60,
    interval: number = 2000
  ): Promise<ProcessingResponse> {
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      const status = await this.getStatus(tripId);
      
      if (onProgress) {
        onProgress(status.progress, status.message);
      }
      
      if (status.status === 'completed' || status.status === 'error') {
        return status;
      }
      
      await new Promise(resolve => setTimeout(resolve, interval));
      attempts++;
    }
    
    throw new Error('Processing timeout');
  }
}

// Export singleton instance
export const api = new TripCraftAPI();
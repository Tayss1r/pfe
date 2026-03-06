/**
 * Intervention Service
 *
 * Handles intervention CRUD operations and attachments
 */

import { apiClient } from './api-client';

// Types
export interface InterventionAttachment {
  id: string;
  intervention_id: string;
  file_path: string;
  attachment_type: string;
  created_at: string;
}

export interface InterventionCreate {
  equipment_id: string;
  diagnostic?: string;
  actions_taken?: string;
}

export interface InterventionUpdate {
  diagnostic?: string;
  actions_taken?: string;
  result?: string;
  failure_reason?: string;
  status?: string;
}

export interface InterventionComplete {
  status: 'COMPLETED' | 'NOT_REPAIRED';
  result?: string;
  failure_reason?: string;
}

export interface InterventionDetail {
  id: string;
  equipment_id: string;
  equipment_serial: string;
  equipment_brand: string | null;
  equipment_model: string | null;
  technician_id: string;
  technician_name: string;
  status: string;
  diagnostic: string | null;
  actions_taken: string | null;
  result: string | null;
  failure_reason: string | null;
  started_at: string | null;
  completed_at: string | null;
  signature_image_path: string | null;
  created_at: string;
  attachments: InterventionAttachment[];
}

export interface InterventionHistory {
  id: string;
  technician_name: string;
  status: string;
  diagnostic: string | null;
  result: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

class InterventionService {
  /**
   * Create a new intervention
   */
  async createIntervention(data: InterventionCreate): Promise<InterventionDetail> {
    const response = await apiClient.post<InterventionDetail>('/interventions', data);
    return response.data;
  }

  /**
   * Get intervention details by ID
   */
  async getIntervention(interventionId: string): Promise<InterventionDetail> {
    const response = await apiClient.get<InterventionDetail>(`/interventions/${interventionId}`);
    return response.data;
  }

  /**
   * Update intervention
   */
  async updateIntervention(interventionId: string, data: InterventionUpdate): Promise<InterventionDetail> {
    const response = await apiClient.put<InterventionDetail>(`/interventions/${interventionId}`, data);
    return response.data;
  }

  /**
   * Complete intervention
   */
  async completeIntervention(interventionId: string, data: InterventionComplete): Promise<InterventionDetail> {
    const response = await apiClient.post<InterventionDetail>(`/interventions/${interventionId}/complete`, data);
    return response.data;
  }

  /**
   * Get intervention history for equipment
   */
  async getEquipmentHistory(equipmentId: string): Promise<InterventionHistory[]> {
    const response = await apiClient.get<InterventionHistory[]>(`/interventions/equipment/${equipmentId}/history`);
    return response.data;
  }

  /**
   * Get active intervention for equipment (if any)
   */
  async getActiveIntervention(equipmentId: string): Promise<InterventionDetail | null> {
    const response = await apiClient.get<InterventionDetail | null>(`/interventions/equipment/${equipmentId}/active`);
    return response.data;
  }

  /**
   * Upload photo to intervention
   */
  async uploadPhoto(interventionId: string, file: File): Promise<InterventionAttachment> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<InterventionAttachment>(
      `/interventions/${interventionId}/upload-photo`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Upload signature to intervention
   */
  async uploadSignature(interventionId: string, blob: Blob): Promise<{ message: string; file_path: string }> {
    const formData = new FormData();
    formData.append('file', blob, 'signature.png');

    const response = await apiClient.post<{ message: string; file_path: string }>(
      `/interventions/${interventionId}/upload-signature`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }
}

export const interventionService = new InterventionService();


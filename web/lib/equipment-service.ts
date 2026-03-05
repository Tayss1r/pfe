/**
 * Equipment Service
 *
 * Handles equipment search, details, and contact functionality
 */

import { apiClient } from './api-client';

// Types
export interface EquipmentSearchParams {
  q?: string;  // Single search query across all fields
  page?: number;
  page_size?: number;
}

export interface EquipmentSummary {
  id: string;
  serial_number: string;
  brand: string | null;
  model: string | null;
  type: string | null;
  image: string | null;
  client_name: string;
}

export interface EquipmentSearchResponse {
  items: EquipmentSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Client {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  created_at: string;
  updated_at: string;
}

export interface Manufacturer {
  id: string;
  name: string;
  support_email: string | null;
  support_phone: string | null;
  created_at: string;
  updated_at: string;
}

export interface TechnicalDocument {
  id: string;
  equipment_id: string;
  title: string;
  file_path: string;
  document_type: 'PDF' | 'VIDEO' | 'IMAGE';
  created_at: string;
}

export interface SparePart {
  id: string;
  equipment_id: string;
  name: string;
  reference_code: string | null;
  description: string | null;
  image: string | null;
  created_at: string;
}

export interface EquipmentDetail {
  id: string;
  serial_number: string;
  brand: string | null;
  model: string | null;
  type: string | null;
  image: string | null;
  created_at: string;
  updated_at: string;
  client: Client;
  manufacturer: Manufacturer | null;
  technical_documents: TechnicalDocument[];
  spare_parts: SparePart[];
}

export interface ContactInfo {
  manufacturer_name?: string;
  client_name?: string;
  support_email?: string;
  email?: string;
  support_phone?: string;
  phone?: string;
  address?: string;
}

export interface EmailSendResponse {
  success: boolean;
  message: string;
  email_log_id?: string;
}

class EquipmentService {
  /**
   * Search for equipment with a single query across all fields
   */
  async search(params: EquipmentSearchParams): Promise<EquipmentSearchResponse> {
    const queryParams = new URLSearchParams();
    
    if (params.q) queryParams.append('q', params.q);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());

    const response = await apiClient.get<EquipmentSearchResponse>(
      `/equipment/search?${queryParams.toString()}`
    );
    return response.data;
  }

  /**
   * Get equipment details by ID
   */
  async getById(equipmentId: string): Promise<EquipmentDetail> {
    const response = await apiClient.get<EquipmentDetail>(`/equipment/${equipmentId}`);
    return response.data;
  }

  /**
   * Get technical documents for equipment
   */
  async getDocuments(equipmentId: string, documentType?: string): Promise<TechnicalDocument[]> {
    let url = `/equipment/${equipmentId}/documents`;
    if (documentType) {
      url += `?document_type=${documentType}`;
    }
    const response = await apiClient.get<TechnicalDocument[]>(url);
    return response.data;
  }

  /**
   * Get spare parts for equipment
   */
  async getSpareParts(equipmentId: string): Promise<SparePart[]> {
    const response = await apiClient.get<SparePart[]>(`/equipment/${equipmentId}/spare-parts`);
    return response.data;
  }

  /**
   * Get manufacturer contact info
   */
  async getManufacturerContact(equipmentId: string): Promise<ContactInfo> {
    const response = await apiClient.get<ContactInfo>(`/contact/manufacturer/${equipmentId}/info`);
    return response.data;
  }

  /**
   * Get client contact info
   */
  async getClientContact(equipmentId: string): Promise<ContactInfo> {
    const response = await apiClient.get<ContactInfo>(`/contact/client/${equipmentId}/info`);
    return response.data;
  }

  /**
   * Send email to manufacturer
   */
  async contactManufacturer(
    equipmentId: string,
    subject: string,
    message: string,
    technicalDocumentIds?: string[],
    photos?: File[],
    interventionId?: string
  ): Promise<EmailSendResponse> {
    const formData = new FormData();
    formData.append('equipment_id', equipmentId);
    formData.append('subject', subject);
    formData.append('message', message);
    
    if (technicalDocumentIds && technicalDocumentIds.length > 0) {
      formData.append('technical_document_ids', technicalDocumentIds.join(','));
    }
    
    if (interventionId) {
      formData.append('intervention_id', interventionId);
    }
    
    if (photos) {
      photos.forEach((photo) => {
        formData.append('photos', photo);
      });
    }

    const response = await apiClient.post<EmailSendResponse>('/contact/manufacturer', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Send email to client
   */
  async contactClient(
    equipmentId: string,
    subject: string,
    message: string,
    photos?: File[],
    interventionId?: string,
    includeInterventionReport?: boolean
  ): Promise<EmailSendResponse> {
    const formData = new FormData();
    formData.append('equipment_id', equipmentId);
    formData.append('subject', subject);
    formData.append('message', message);
    
    if (interventionId) {
      formData.append('intervention_id', interventionId);
    }
    
    if (includeInterventionReport) {
      formData.append('include_intervention_report', 'true');
    }
    
    if (photos) {
      photos.forEach((photo) => {
        formData.append('photos', photo);
      });
    }

    const response = await apiClient.post<EmailSendResponse>('/contact/client', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Upload a photo
   */
  async uploadPhoto(file: File, interventionId?: string): Promise<{ file_path: string }> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (interventionId) {
      formData.append('intervention_id', interventionId);
    }

    const response = await apiClient.post<{ file_path: string }>('/contact/upload-photo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

export const equipmentService = new EquipmentService();

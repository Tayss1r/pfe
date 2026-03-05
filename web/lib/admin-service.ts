/**
 * Admin Service
 * 
 * Handles all admin API calls for CRUD operations
 */

import { apiClient } from './api-client';

// ============== Types ==============

export interface DashboardStats {
  total_equipment: number;
  total_clients: number;
  total_manufacturers: number;
  total_interventions: number;
  total_spare_parts: number;
  total_documents: number;
  interventions_in_progress: number;
  interventions_completed: number;
  interventions_not_repaired: number;
}

export interface RecentIntervention {
  id: string;
  equipment_serial: string;
  technician_name: string;
  status: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Client Types
export interface Client {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  created_at: string;
  updated_at: string;
}

export interface ClientCreate {
  name: string;
  email?: string;
  phone?: string;
  address?: string;
}

export interface ClientUpdate {
  name?: string;
  email?: string;
  phone?: string;
  address?: string;
}

// Manufacturer Types
export interface Manufacturer {
  id: string;
  name: string;
  support_email: string | null;
  support_phone: string | null;
  created_at: string;
  updated_at: string;
}

export interface ManufacturerCreate {
  name: string;
  support_email?: string;
  support_phone?: string;
}

export interface ManufacturerUpdate {
  name?: string;
  support_email?: string;
  support_phone?: string;
}

// Equipment Types
export interface Equipment {
  id: string;
  serial_number: string;
  brand: string | null;
  model: string | null;
  type: string | null;
  image: string | null;
  client_id: string;
  client_name: string;
  manufacturer_id: string | null;
  manufacturer_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface EquipmentCreate {
  serial_number: string;
  brand?: string;
  model?: string;
  type?: string;
  client_id: string;
  manufacturer_id?: string;
  image?: string;
}

export interface EquipmentUpdate {
  serial_number?: string;
  brand?: string;
  model?: string;
  type?: string;
  client_id?: string;
  manufacturer_id?: string;
  image?: string;
}

// Document Types
export interface TechnicalDocument {
  id: string;
  equipment_id: string;
  equipment_serial: string;
  title: string;
  file_path: string;
  document_type: 'PDF' | 'VIDEO' | 'IMAGE';
  created_at: string;
}

// Spare Part Types
export interface SparePart {
  id: string;
  equipment_id: string;
  equipment_serial: string;
  name: string;
  reference_code: string | null;
  description: string | null;
  image: string | null;
  created_at: string;
}

export interface SparePartCreate {
  equipment_id: string;
  name: string;
  reference_code?: string;
  description?: string;
  image?: string;
}

export interface SparePartUpdate {
  name?: string;
  reference_code?: string;
  description?: string;
  image?: string;
}

// ============== Admin Service ==============

class AdminService {
  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await apiClient.get<DashboardStats>('/admin/dashboard/stats');
    return response.data;
  }

  async getRecentInterventions(limit: number = 10): Promise<RecentIntervention[]> {
    const response = await apiClient.get<RecentIntervention[]>(
      `/admin/dashboard/recent-interventions?limit=${limit}`
    );
    return response.data;
  }

  // Clients
  async getClients(page = 1, pageSize = 10, search?: string): Promise<PaginatedResponse<Client>> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (search) params.append('search', search);
    const response = await apiClient.get<PaginatedResponse<Client>>(`/admin/clients?${params}`);
    return response.data;
  }

  async getClient(id: string): Promise<Client> {
    const response = await apiClient.get<Client>(`/admin/clients/${id}`);
    return response.data;
  }

  async createClient(data: ClientCreate): Promise<Client> {
    const response = await apiClient.post<Client>('/admin/clients', data);
    return response.data;
  }

  async updateClient(id: string, data: ClientUpdate): Promise<Client> {
    const response = await apiClient.put<Client>(`/admin/clients/${id}`, data);
    return response.data;
  }

  async deleteClient(id: string): Promise<void> {
    await apiClient.delete(`/admin/clients/${id}`);
  }

  // Manufacturers
  async getManufacturers(page = 1, pageSize = 10, search?: string): Promise<PaginatedResponse<Manufacturer>> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (search) params.append('search', search);
    const response = await apiClient.get<PaginatedResponse<Manufacturer>>(`/admin/manufacturers?${params}`);
    return response.data;
  }

  async getManufacturer(id: string): Promise<Manufacturer> {
    const response = await apiClient.get<Manufacturer>(`/admin/manufacturers/${id}`);
    return response.data;
  }

  async createManufacturer(data: ManufacturerCreate): Promise<Manufacturer> {
    const response = await apiClient.post<Manufacturer>('/admin/manufacturers', data);
    return response.data;
  }

  async updateManufacturer(id: string, data: ManufacturerUpdate): Promise<Manufacturer> {
    const response = await apiClient.put<Manufacturer>(`/admin/manufacturers/${id}`, data);
    return response.data;
  }

  async deleteManufacturer(id: string): Promise<void> {
    await apiClient.delete(`/admin/manufacturers/${id}`);
  }

  // Equipment
  async getEquipment(page = 1, pageSize = 10, search?: string): Promise<PaginatedResponse<Equipment>> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (search) params.append('search', search);
    const response = await apiClient.get<PaginatedResponse<Equipment>>(`/admin/equipment?${params}`);
    return response.data;
  }

  async getEquipmentById(id: string): Promise<Equipment> {
    const response = await apiClient.get<Equipment>(`/admin/equipment/${id}`);
    return response.data;
  }

  async createEquipment(data: EquipmentCreate): Promise<Equipment> {
    const response = await apiClient.post<Equipment>('/admin/equipment', data);
    return response.data;
  }

  async updateEquipment(id: string, data: EquipmentUpdate): Promise<Equipment> {
    const response = await apiClient.put<Equipment>(`/admin/equipment/${id}`, data);
    return response.data;
  }

  async deleteEquipment(id: string): Promise<void> {
    await apiClient.delete(`/admin/equipment/${id}`);
  }

  async uploadEquipmentImage(id: string, file: File): Promise<{ filename: string; path: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<{ filename: string; path: string }>(
      `/admin/equipment/${id}/image`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  }

  // Documents
  async getDocuments(
    page = 1,
    pageSize = 10,
    equipmentId?: string,
    search?: string
  ): Promise<PaginatedResponse<TechnicalDocument>> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (equipmentId) params.append('equipment_id', equipmentId);
    if (search) params.append('search', search);
    const response = await apiClient.get<PaginatedResponse<TechnicalDocument>>(`/admin/documents?${params}`);
    return response.data;
  }

  async uploadDocument(equipmentId: string, title: string, file: File): Promise<TechnicalDocument> {
    const formData = new FormData();
    formData.append('equipment_id', equipmentId);
    formData.append('title', title);
    formData.append('file', file);
    const response = await apiClient.post<TechnicalDocument>('/admin/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async deleteDocument(id: string): Promise<void> {
    await apiClient.delete(`/admin/documents/${id}`);
  }

  // Spare Parts
  async getSpareParts(
    page = 1,
    pageSize = 10,
    equipmentId?: string,
    search?: string
  ): Promise<PaginatedResponse<SparePart>> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (equipmentId) params.append('equipment_id', equipmentId);
    if (search) params.append('search', search);
    const response = await apiClient.get<PaginatedResponse<SparePart>>(`/admin/spare-parts?${params}`);
    return response.data;
  }

  async getSparePart(id: string): Promise<SparePart> {
    const response = await apiClient.get<SparePart>(`/admin/spare-parts/${id}`);
    return response.data;
  }

  async createSparePart(data: SparePartCreate): Promise<SparePart> {
    const response = await apiClient.post<SparePart>('/admin/spare-parts', data);
    return response.data;
  }

  async updateSparePart(id: string, data: SparePartUpdate): Promise<SparePart> {
    const response = await apiClient.put<SparePart>(`/admin/spare-parts/${id}`, data);
    return response.data;
  }

  async deleteSparePart(id: string): Promise<void> {
    await apiClient.delete(`/admin/spare-parts/${id}`);
  }
}

export const adminService = new AdminService();

'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { adminService, Equipment, EquipmentCreate, EquipmentUpdate, Client, Manufacturer } from '@/lib/admin-service';
import {
  AdminTable,
  Pagination,
  SearchBar,
  Modal,
  FormField,
  SelectField,
  Button,
} from '@/components/admin-ui';

export default function AdminEquipmentPage() {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Equipment | null>(null);
  const [formData, setFormData] = useState<EquipmentCreate>({
    serial_number: '',
    brand: '',
    model: '',
    type: '',
    client_id: '',
    manufacturer_id: '',
  });
  const [saving, setSaving] = useState(false);

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [toDelete, setToDelete] = useState<Equipment | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [equipmentData, clientsData, manufacturersData] = await Promise.all([
        adminService.getEquipment(page, 10, search || undefined),
        adminService.getClients(1, 100),
        adminService.getManufacturers(1, 100),
      ]);
      setEquipment(equipmentData.items);
      setTotalPages(equipmentData.total_pages);
      setClients(clientsData.items);
      setManufacturers(manufacturersData.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load equipment');
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  function openCreateModal() {
    setEditing(null);
    setFormData({
      serial_number: '',
      brand: '',
      model: '',
      type: '',
      client_id: '',
      manufacturer_id: '',
    });
    setModalOpen(true);
  }

  function openEditModal(item: Equipment) {
    setEditing(item);
    setFormData({
      serial_number: item.serial_number,
      brand: item.brand || '',
      model: item.model || '',
      type: item.type || '',
      client_id: item.client_id,
      manufacturer_id: item.manufacturer_id || '',
    });
    setModalOpen(true);
  }

  function handleFormChange(name: string, value: string) {
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const data = {
        ...formData,
        manufacturer_id: formData.manufacturer_id || undefined,
      };
      if (editing) {
        await adminService.updateEquipment(editing.id, data as EquipmentUpdate);
      } else {
        await adminService.createEquipment(data as EquipmentCreate);
      }
      setModalOpen(false);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save');
    } finally {
      setSaving(false);
    }
  }

  function openDeleteConfirm(item: Equipment) {
    setToDelete(item);
    setDeleteConfirmOpen(true);
  }

  async function handleDelete() {
    if (!toDelete) return;
    try {
      await adminService.deleteEquipment(toDelete.id);
      setDeleteConfirmOpen(false);
      setToDelete(null);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete');
    }
  }

  const columns = [
    { key: 'serial_number', label: 'Serial Number' },
    { key: 'brand', label: 'Brand', render: (e: Equipment) => e.brand || '-' },
    { key: 'model', label: 'Model', render: (e: Equipment) => e.model || '-' },
    { key: 'type', label: 'Type', render: (e: Equipment) => e.type || '-' },
    { key: 'client_name', label: 'Client' },
    { key: 'manufacturer_name', label: 'Manufacturer', render: (e: Equipment) => e.manufacturer_name || '-' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Equipment</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage equipment records</p>
        </div>
        <Button onClick={openCreateModal}>+ Add Equipment</Button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
          <button onClick={() => setError('')} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <SearchBar value={search} onChange={setSearch} placeholder="Search equipment..." />
        </div>

        <AdminTable
          columns={columns}
          data={equipment}
          keyExtractor={(e) => e.id}
          onEdit={openEditModal}
          onDelete={openDeleteConfirm}
          loading={loading}
          emptyMessage="No equipment found"
        />

        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Equipment' : 'Add Equipment'}>
        <form onSubmit={handleSubmit}>
          <FormField label="Serial Number" name="serial_number" value={formData.serial_number} onChange={handleFormChange} required placeholder="SN-12345" />
          <FormField label="Brand" name="brand" value={formData.brand || ''} onChange={handleFormChange} placeholder="Samsung" />
          <FormField label="Model" name="model" value={formData.model || ''} onChange={handleFormChange} placeholder="Galaxy S21" />
          <FormField label="Type" name="type" value={formData.type || ''} onChange={handleFormChange} placeholder="Smartphone" />
          <SelectField
            label="Client"
            name="client_id"
            value={formData.client_id}
            onChange={handleFormChange}
            options={clients.map((c) => ({ value: c.id, label: c.name }))}
            required
            placeholder="Select client..."
          />
          <SelectField
            label="Manufacturer"
            name="manufacturer_id"
            value={formData.manufacturer_id || ''}
            onChange={handleFormChange}
            options={manufacturers.map((m) => ({ value: m.id, label: m.name }))}
            placeholder="Select manufacturer (optional)"
          />
          <div className="flex justify-end gap-3 mt-6">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={saving}>{saving ? 'Saving...' : editing ? 'Update' : 'Create'}</Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)} title="Delete Equipment">
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete equipment <strong>{toDelete?.serial_number}</strong>? This will also delete all related documents and spare parts.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button variant="danger" onClick={handleDelete}>Delete</Button>
        </div>
      </Modal>
    </div>
  );
}

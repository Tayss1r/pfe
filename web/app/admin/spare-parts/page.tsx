'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { adminService, SparePart, SparePartCreate, SparePartUpdate, Equipment } from '@/lib/admin-service';
import {
  AdminTable,
  Pagination,
  SearchBar,
  Modal,
  FormField,
  SelectField,
  Button,
} from '@/components/admin-ui';

export default function AdminSparePartsPage() {
  const [spareParts, setSpareParts] = useState<SparePart[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<SparePart | null>(null);
  const [formData, setFormData] = useState<SparePartCreate>({
    equipment_id: '',
    name: '',
    reference_code: '',
    description: '',
  });
  const [saving, setSaving] = useState(false);

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [toDelete, setToDelete] = useState<SparePart | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [partsData, equipmentData] = await Promise.all([
        adminService.getSpareParts(page, 10, undefined, search || undefined),
        adminService.getEquipment(1, 100),
      ]);
      setSpareParts(partsData.items);
      setTotalPages(partsData.total_pages);
      setEquipment(equipmentData.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load spare parts');
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    const timer = setTimeout(() => setPage(1), 300);
    return () => clearTimeout(timer);
  }, [search]);

  function openCreateModal() {
    setEditing(null);
    setFormData({ equipment_id: '', name: '', reference_code: '', description: '' });
    setModalOpen(true);
  }

  function openEditModal(item: SparePart) {
    setEditing(item);
    setFormData({
      equipment_id: item.equipment_id,
      name: item.name,
      reference_code: item.reference_code || '',
      description: item.description || '',
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
      if (editing) {
        const updateData: SparePartUpdate = {
          name: formData.name,
          reference_code: formData.reference_code || undefined,
          description: formData.description || undefined,
        };
        await adminService.updateSparePart(editing.id, updateData);
      } else {
        await adminService.createSparePart(formData);
      }
      setModalOpen(false);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save');
    } finally {
      setSaving(false);
    }
  }

  function openDeleteConfirm(item: SparePart) {
    setToDelete(item);
    setDeleteConfirmOpen(true);
  }

  async function handleDelete() {
    if (!toDelete) return;
    try {
      await adminService.deleteSparePart(toDelete.id);
      setDeleteConfirmOpen(false);
      setToDelete(null);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete');
    }
  }

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'reference_code', label: 'Reference Code', render: (sp: SparePart) => sp.reference_code || '-' },
    { key: 'equipment_serial', label: 'Equipment' },
    { key: 'description', label: 'Description', render: (sp: SparePart) => (sp.description ? sp.description.slice(0, 50) + (sp.description.length > 50 ? '...' : '') : '-') },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Spare Parts</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage spare parts inventory</p>
        </div>
        <Button onClick={openCreateModal}>+ Add Spare Part</Button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
          <button onClick={() => setError('')} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <SearchBar value={search} onChange={setSearch} placeholder="Search spare parts..." />
        </div>

        <AdminTable
          columns={columns}
          data={spareParts}
          keyExtractor={(sp) => sp.id}
          onEdit={openEditModal}
          onDelete={openDeleteConfirm}
          loading={loading}
          emptyMessage="No spare parts found"
        />

        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Spare Part' : 'Add Spare Part'}>
        <form onSubmit={handleSubmit}>
          {!editing && (
            <SelectField
              label="Equipment"
              name="equipment_id"
              value={formData.equipment_id}
              onChange={handleFormChange}
              options={equipment.map((e) => ({ value: e.id, label: `${e.serial_number} - ${e.brand || ''} ${e.model || ''}` }))}
              required
              placeholder="Select equipment..."
            />
          )}
          <FormField label="Name" name="name" value={formData.name} onChange={handleFormChange} required placeholder="Part name" />
          <FormField label="Reference Code" name="reference_code" value={formData.reference_code || ''} onChange={handleFormChange} placeholder="SP-12345" />
          <FormField label="Description" name="description" type="textarea" value={formData.description || ''} onChange={handleFormChange} placeholder="Part description..." />
          <div className="flex justify-end gap-3 mt-6">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={saving}>{saving ? 'Saving...' : editing ? 'Update' : 'Create'}</Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)} title="Delete Spare Part">
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete <strong>{toDelete?.name}</strong>? This action cannot be undone.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button variant="danger" onClick={handleDelete}>Delete</Button>
        </div>
      </Modal>
    </div>
  );
}

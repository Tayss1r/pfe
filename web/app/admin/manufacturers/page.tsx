'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { adminService, Manufacturer, ManufacturerCreate, ManufacturerUpdate } from '@/lib/admin-service';
import {
  AdminTable,
  Pagination,
  SearchBar,
  Modal,
  FormField,
  Button,
} from '@/components/admin-ui';

export default function AdminManufacturersPage() {
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Manufacturer | null>(null);
  const [formData, setFormData] = useState<ManufacturerCreate>({
    name: '',
    support_email: '',
    support_phone: '',
  });
  const [saving, setSaving] = useState(false);

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [toDelete, setToDelete] = useState<Manufacturer | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const data = await adminService.getManufacturers(page, 10, search || undefined);
      setManufacturers(data.items);
      setTotalPages(data.total_pages);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load manufacturers');
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
      loadData();
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  function openCreateModal() {
    setEditing(null);
    setFormData({ name: '', support_email: '', support_phone: '' });
    setModalOpen(true);
  }

  function openEditModal(item: Manufacturer) {
    setEditing(item);
    setFormData({
      name: item.name,
      support_email: item.support_email || '',
      support_phone: item.support_phone || '',
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
        await adminService.updateManufacturer(editing.id, formData as ManufacturerUpdate);
      } else {
        await adminService.createManufacturer(formData);
      }
      setModalOpen(false);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save');
    } finally {
      setSaving(false);
    }
  }

  function openDeleteConfirm(item: Manufacturer) {
    setToDelete(item);
    setDeleteConfirmOpen(true);
  }

  async function handleDelete() {
    if (!toDelete) return;
    try {
      await adminService.deleteManufacturer(toDelete.id);
      setDeleteConfirmOpen(false);
      setToDelete(null);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete');
    }
  }

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'support_email', label: 'Support Email', render: (m: Manufacturer) => m.support_email || '-' },
    { key: 'support_phone', label: 'Support Phone', render: (m: Manufacturer) => m.support_phone || '-' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Manufacturers</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage manufacturer records</p>
        </div>
        <Button onClick={openCreateModal}>+ Add Manufacturer</Button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
          <button onClick={() => setError('')} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <SearchBar value={search} onChange={setSearch} placeholder="Search manufacturers..." />
        </div>

        <AdminTable
          columns={columns}
          data={manufacturers}
          keyExtractor={(m) => m.id}
          onEdit={openEditModal}
          onDelete={openDeleteConfirm}
          loading={loading}
          emptyMessage="No manufacturers found"
        />

        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Manufacturer' : 'Add Manufacturer'}>
        <form onSubmit={handleSubmit}>
          <FormField label="Name" name="name" value={formData.name} onChange={handleFormChange} required placeholder="Manufacturer name" />
          <FormField label="Support Email" name="support_email" type="email" value={formData.support_email || ''} onChange={handleFormChange} placeholder="support@example.com" />
          <FormField label="Support Phone" name="support_phone" value={formData.support_phone || ''} onChange={handleFormChange} placeholder="+1234567890" />
          <div className="flex justify-end gap-3 mt-6">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={saving}>{saving ? 'Saving...' : editing ? 'Update' : 'Create'}</Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)} title="Delete Manufacturer">
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

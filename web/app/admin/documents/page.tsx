'use client';

import React, { useEffect, useState, useCallback, useRef } from 'react';
import { adminService, TechnicalDocument, Equipment } from '@/lib/admin-service';
import {
  AdminTable,
  Pagination,
  SearchBar,
  Modal,
  FormField,
  SelectField,
  Button,
} from '@/components/admin-ui';

export default function AdminDocumentsPage() {
  const [documents, setDocuments] = useState<TechnicalDocument[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');

  const [modalOpen, setModalOpen] = useState(false);
  const [formData, setFormData] = useState({ equipment_id: '', title: '' });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [toDelete, setToDelete] = useState<TechnicalDocument | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [docsData, equipmentData] = await Promise.all([
        adminService.getDocuments(page, 10, undefined, search || undefined),
        adminService.getEquipment(1, 100),
      ]);
      setDocuments(docsData.items);
      setTotalPages(docsData.total_pages);
      setEquipment(equipmentData.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load documents');
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

  function openUploadModal() {
    setFormData({ equipment_id: '', title: '' });
    setSelectedFile(null);
    setModalOpen(true);
  }

  function handleFormChange(name: string, value: string) {
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files?.[0]) {
      setSelectedFile(e.target.files[0]);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }
    setSaving(true);
    try {
      await adminService.uploadDocument(formData.equipment_id, formData.title, selectedFile);
      setModalOpen(false);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setSaving(false);
    }
  }

  function openDeleteConfirm(item: TechnicalDocument) {
    setToDelete(item);
    setDeleteConfirmOpen(true);
  }

  async function handleDelete() {
    if (!toDelete) return;
    try {
      await adminService.deleteDocument(toDelete.id);
      setDeleteConfirmOpen(false);
      setToDelete(null);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete');
    }
  }

  function getTypeBadge(type: string) {
    switch (type) {
      case 'PDF':
        return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400';
      case 'VIDEO':
        return 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400';
      case 'IMAGE':
        return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';
    }
  }

  const columns = [
    { key: 'title', label: 'Title' },
    { key: 'equipment_serial', label: 'Equipment' },
    {
      key: 'document_type',
      label: 'Type',
      render: (d: TechnicalDocument) => (
        <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${getTypeBadge(d.document_type)}`}>
          {d.document_type}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Uploaded',
      render: (d: TechnicalDocument) =>
        new Date(d.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Technical Documents</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage technical documentation</p>
        </div>
        <Button onClick={openUploadModal}>+ Upload Document</Button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
          <button onClick={() => setError('')} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <SearchBar value={search} onChange={setSearch} placeholder="Search documents..." />
        </div>

        <AdminTable
          columns={columns}
          data={documents}
          keyExtractor={(d) => d.id}
          onDelete={openDeleteConfirm}
          loading={loading}
          emptyMessage="No documents found"
        />

        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Upload Document">
        <form onSubmit={handleSubmit}>
          <SelectField
            label="Equipment"
            name="equipment_id"
            value={formData.equipment_id}
            onChange={handleFormChange}
            options={equipment.map((e) => ({ value: e.id, label: `${e.serial_number} - ${e.brand || ''} ${e.model || ''}` }))}
            required
            placeholder="Select equipment..."
          />
          <FormField label="Title" name="title" value={formData.title} onChange={handleFormChange} required placeholder="Document title" />
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              File <span className="text-red-500">*</span>
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,image/*,video/*"
              onChange={handleFileChange}
              className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900/30 dark:file:text-blue-400"
            />
            {selectedFile && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
              </p>
            )}
          </div>
          <div className="flex justify-end gap-3 mt-6">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={saving}>{saving ? 'Uploading...' : 'Upload'}</Button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)} title="Delete Document">
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete <strong>{toDelete?.title}</strong>? This will also remove the file from storage.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button variant="danger" onClick={handleDelete}>Delete</Button>
        </div>
      </Modal>
    </div>
  );
}

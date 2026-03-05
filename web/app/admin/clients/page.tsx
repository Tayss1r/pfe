'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { adminService, Client, ClientCreate, ClientUpdate } from '@/lib/admin-service';
import {
  AdminTable,
  Pagination,
  SearchBar,
  Modal,
  FormField,
  Button,
} from '@/components/admin-ui';

export default function AdminClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState<ClientCreate>({
    name: '',
    email: '',
    phone: '',
    address: '',
  });
  const [saving, setSaving] = useState(false);

  // Delete confirmation
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [clientToDelete, setClientToDelete] = useState<Client | null>(null);

  const loadClients = useCallback(async () => {
    try {
      setLoading(true);
      const data = await adminService.getClients(page, 10, search || undefined);
      setClients(data.items);
      setTotalPages(data.total_pages);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load clients');
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    loadClients();
  }, [loadClients]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setPage(1);
      loadClients();
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  function openCreateModal() {
    setEditingClient(null);
    setFormData({ name: '', email: '', phone: '', address: '' });
    setModalOpen(true);
  }

  function openEditModal(client: Client) {
    setEditingClient(client);
    setFormData({
      name: client.name,
      email: client.email || '',
      phone: client.phone || '',
      address: client.address || '',
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
      if (editingClient) {
        await adminService.updateClient(editingClient.id, formData as ClientUpdate);
      } else {
        await adminService.createClient(formData);
      }
      setModalOpen(false);
      loadClients();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save client');
    } finally {
      setSaving(false);
    }
  }

  function openDeleteConfirm(client: Client) {
    setClientToDelete(client);
    setDeleteConfirmOpen(true);
  }

  async function handleDelete() {
    if (!clientToDelete) return;
    try {
      await adminService.deleteClient(clientToDelete.id);
      setDeleteConfirmOpen(false);
      setClientToDelete(null);
      loadClients();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete client');
    }
  }

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email', render: (c: Client) => c.email || '-' },
    { key: 'phone', label: 'Phone', render: (c: Client) => c.phone || '-' },
    { key: 'address', label: 'Address', render: (c: Client) => c.address || '-' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Clients</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage client records</p>
        </div>
        <Button onClick={openCreateModal}>+ Add Client</Button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
          <button onClick={() => setError('')} className="ml-2 underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Table Card */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        {/* Search */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <SearchBar
            value={search}
            onChange={setSearch}
            placeholder="Search clients..."
          />
        </div>

        {/* Table */}
        <AdminTable
          columns={columns}
          data={clients}
          keyExtractor={(c) => c.id}
          onEdit={openEditModal}
          onDelete={openDeleteConfirm}
          loading={loading}
          emptyMessage="No clients found"
        />

        {/* Pagination */}
        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingClient ? 'Edit Client' : 'Add Client'}
      >
        <form onSubmit={handleSubmit}>
          <FormField
            label="Name"
            name="name"
            value={formData.name}
            onChange={handleFormChange}
            required
            placeholder="Client name"
          />
          <FormField
            label="Email"
            name="email"
            type="email"
            value={formData.email || ''}
            onChange={handleFormChange}
            placeholder="client@example.com"
          />
          <FormField
            label="Phone"
            name="phone"
            value={formData.phone || ''}
            onChange={handleFormChange}
            placeholder="+1234567890"
          />
          <FormField
            label="Address"
            name="address"
            type="textarea"
            value={formData.address || ''}
            onChange={handleFormChange}
            placeholder="Street, City, Country"
          />
          <div className="flex justify-end gap-3 mt-6">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : editingClient ? 'Update' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation */}
      <Modal
        isOpen={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        title="Delete Client"
      >
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete <strong>{clientToDelete?.name}</strong>?
          This action cannot be undone.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteConfirmOpen(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            Delete
          </Button>
        </div>
      </Modal>
    </div>
  );
}

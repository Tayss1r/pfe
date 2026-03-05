'use client';

/**
 * Equipment Detail Dashboard Page
 *
 * Shows complete equipment information:
 * - Basic equipment info
 * - Technical documentation (PDFs, videos, images)
 * - Spare parts list
 * - Manufacturer contact
 * - Client contact
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import {
  equipmentService,
  EquipmentDetail,
  TechnicalDocument,
  SparePart,
} from '@/lib/equipment-service';
import Link from 'next/link';
import { ThemeToggle } from '@/components/theme-toggle';

type ActiveTab = 'documents' | 'spareparts' | 'manufacturer' | 'client';

export default function EquipmentDetailPage() {
  const { isLoading: authLoading, isAuthenticated } = useAuth();
  const router = useRouter();
  const params = useParams();
  const equipmentId = params.id as string;

  const [equipment, setEquipment] = useState<EquipmentDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<ActiveTab>('documents');

  // Contact form state
  const [contactSubject, setContactSubject] = useState('');
  const [contactMessage, setContactMessage] = useState('');
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [photos, setPhotos] = useState<File[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [sendSuccess, setSendSuccess] = useState('');
  const [sendError, setSendError] = useState('');

  const loadEquipment = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await equipmentService.getById(equipmentId);
      setEquipment(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load equipment details');
    } finally {
      setIsLoading(false);
    }
  }, [equipmentId]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }

    if (isAuthenticated && equipmentId) {
      loadEquipment();
    }
  }, [authLoading, isAuthenticated, equipmentId, router, loadEquipment]);

  const handlePhotoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPhotos(Array.from(e.target.files));
    }
  };

  const handleDocToggle = (docId: string) => {
    setSelectedDocs((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    );
  };

  const handleSendToManufacturer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!equipment?.manufacturer?.support_email) {
      setSendError('No manufacturer email configured');
      return;
    }

    setIsSending(true);
    setSendError('');
    setSendSuccess('');

    try {
      const response = await equipmentService.contactManufacturer(
        equipmentId,
        contactSubject,
        contactMessage,
        selectedDocs.length > 0 ? selectedDocs : undefined,
        photos.length > 0 ? photos : undefined
      );
      setSendSuccess(response.message);
      setContactSubject('');
      setContactMessage('');
      setSelectedDocs([]);
      setPhotos([]);
    } catch (err: any) {
      setSendError(err.response?.data?.detail || 'Failed to send email');
    } finally {
      setIsSending(false);
    }
  };

  const handleSendToClient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!equipment?.client?.email) {
      setSendError('No client email configured');
      return;
    }

    setIsSending(true);
    setSendError('');
    setSendSuccess('');

    try {
      const response = await equipmentService.contactClient(
        equipmentId,
        contactSubject,
        contactMessage,
        photos.length > 0 ? photos : undefined
      );
      setSendSuccess(response.message);
      setContactSubject('');
      setContactMessage('');
      setPhotos([]);
    } catch (err: any) {
      setSendError(err.response?.data?.detail || 'Failed to send email');
    } finally {
      setIsSending(false);
    }
  };

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="flex flex-col items-center gap-4">
          <svg className="animate-spin h-10 w-10 text-blue-600" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-gray-600 dark:text-gray-400">Loading equipment details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 mb-6">
            <h2 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">Error</h2>
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
          <Link href="/equipment" className="inline-flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors">
            ← Back to Search
          </Link>
        </div>
      </div>
    );
  }

  if (!equipment) {
    return null;
  }

  const tabs = [
    { key: 'documents', label: `Documents (${equipment.technical_documents.length})`, icon: '📚' },
    { key: 'spareparts', label: `Spare Parts (${equipment.spare_parts.length})`, icon: '🔧' },
    { key: 'manufacturer', label: 'Contact Manufacturer', icon: '📧' },
    { key: 'client', label: 'Contact Client', icon: '📨' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">Equipment Dashboard</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Serial: {equipment.serial_number}</p>
            </div>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <Link href="/equipment" className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white border border-gray-300 dark:border-gray-600 rounded-lg transition-colors">
                ← Back to Search
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Info Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
          {/* Equipment Info */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white mb-4">
              <span>📦</span> Equipment Info
            </h3>
            <dl className="space-y-3">
              <InfoRow label="Serial Number" value={equipment.serial_number} />
              <InfoRow label="Brand" value={equipment.brand} />
              <InfoRow label="Model" value={equipment.model} />
              <InfoRow label="Type" value={equipment.type} />
            </dl>
          </div>

          {/* Client Info */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white mb-4">
              <span>👤</span> Client
            </h3>
            <dl className="space-y-3">
              <InfoRow label="Name" value={equipment.client.name} />
              <InfoRow label="Email" value={equipment.client.email} isEmail />
              <InfoRow label="Phone" value={equipment.client.phone} isPhone />
              <InfoRow label="Address" value={equipment.client.address} />
            </dl>
          </div>

          {/* Manufacturer Info */}
          {equipment.manufacturer && (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white mb-4">
                <span>🏭</span> Manufacturer
              </h3>
              <dl className="space-y-3">
                <InfoRow label="Name" value={equipment.manufacturer.name} />
                <InfoRow label="Support Email" value={equipment.manufacturer.support_email} isEmail />
                <InfoRow label="Support Phone" value={equipment.manufacturer.support_phone} isPhone />
              </dl>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-2 border-b border-gray-200 dark:border-gray-700 pb-px">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as ActiveTab)}
                className={`px-4 py-3 text-sm font-medium rounded-t-lg transition-colors ${
                  activeTab === tab.key
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          {activeTab === 'documents' && <DocumentsTab documents={equipment.technical_documents} />}
          {activeTab === 'spareparts' && <SparePartsTab spareParts={equipment.spare_parts} />}
          {activeTab === 'manufacturer' && (
            <ContactManufacturerTab
              manufacturer={equipment.manufacturer}
              documents={equipment.technical_documents}
              subject={contactSubject}
              message={contactMessage}
              selectedDocs={selectedDocs}
              photos={photos}
              isSending={isSending}
              sendSuccess={sendSuccess}
              sendError={sendError}
              onSubjectChange={setContactSubject}
              onMessageChange={setContactMessage}
              onDocToggle={handleDocToggle}
              onPhotoSelect={handlePhotoSelect}
              onSubmit={handleSendToManufacturer}
            />
          )}
          {activeTab === 'client' && (
            <ContactClientTab
              client={equipment.client}
              subject={contactSubject}
              message={contactMessage}
              photos={photos}
              isSending={isSending}
              sendSuccess={sendSuccess}
              sendError={sendError}
              onSubjectChange={setContactSubject}
              onMessageChange={setContactMessage}
              onPhotoSelect={handlePhotoSelect}
              onSubmit={handleSendToClient}
            />
          )}
        </div>
      </main>
    </div>
  );
}

// Helper Components
function InfoRow({ label, value, isEmail, isPhone }: { label: string; value: string | null | undefined; isEmail?: boolean; isPhone?: boolean }) {
  return (
    <div className="flex justify-between">
      <dt className="text-gray-500 dark:text-gray-400">{label}:</dt>
      <dd className="font-medium text-gray-900 dark:text-white text-right max-w-[60%]">
        {value ? (
          isEmail ? (
            <a href={`mailto:${value}`} className="text-blue-600 dark:text-blue-400 hover:underline">{value}</a>
          ) : isPhone ? (
            <a href={`tel:${value}`} className="text-blue-600 dark:text-blue-400 hover:underline">{value}</a>
          ) : (
            value
          )
        ) : (
          <span className="text-gray-400">-</span>
        )}
      </dd>
    </div>
  );
}

function DocumentsTab({ documents }: { documents: TechnicalDocument[] }) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'PDF': return '📄';
      case 'VIDEO': return '🎬';
      case 'IMAGE': return '🖼️';
      default: return '📁';
    }
  };

  if (documents.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">📚</div>
        <p className="text-gray-500 dark:text-gray-400">No technical documents available for this equipment.</p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Technical Documentation</h3>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {documents.map((doc) => (
          <div key={doc.id} className="flex items-center gap-4 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <span className="text-3xl">{getIcon(doc.document_type)}</span>
            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-gray-900 dark:text-white truncate">{doc.title}</h4>
              <span className="inline-block px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded mt-1">
                {doc.document_type}
              </span>
            </div>
            <a
              href={doc.file_path}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-2 text-sm font-medium bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
            >
              Open
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

function SparePartsTab({ spareParts }: { spareParts: SparePart[] }) {
  if (spareParts.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">🔧</div>
        <p className="text-gray-500 dark:text-gray-400">No spare parts listed for this equipment.</p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Spare Parts List</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-200 dark:border-gray-700">
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Name</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Reference Code</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {spareParts.map((part) => (
              <tr key={part.id}>
                <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{part.name}</td>
                <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{part.reference_code || '-'}</td>
                <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{part.description || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ContactManufacturerTab({
  manufacturer,
  documents,
  subject,
  message,
  selectedDocs,
  photos,
  isSending,
  sendSuccess,
  sendError,
  onSubjectChange,
  onMessageChange,
  onDocToggle,
  onPhotoSelect,
  onSubmit,
}: {
  manufacturer: EquipmentDetail['manufacturer'];
  documents: TechnicalDocument[];
  subject: string;
  message: string;
  selectedDocs: string[];
  photos: File[];
  isSending: boolean;
  sendSuccess: string;
  sendError: string;
  onSubjectChange: (v: string) => void;
  onMessageChange: (v: string) => void;
  onDocToggle: (id: string) => void;
  onPhotoSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
}) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'PDF': return '📄';
      case 'VIDEO': return '🎬';
      case 'IMAGE': return '🖼️';
      default: return '📁';
    }
  };

  if (!manufacturer) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">🏭</div>
        <p className="text-gray-500 dark:text-gray-400">No manufacturer associated with this equipment.</p>
      </div>
    );
  }

  if (!manufacturer.support_email) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">📧</div>
        <p className="text-gray-500 dark:text-gray-400 mb-2">Manufacturer does not have a support email configured.</p>
        {manufacturer.support_phone && (
          <p className="text-gray-600 dark:text-gray-300">
            You can call: <a href={`tel:${manufacturer.support_phone}`} className="text-blue-600 dark:text-blue-400">{manufacturer.support_phone}</a>
          </p>
        )}
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Contact Manufacturer</h3>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        Send email to: <strong className="text-gray-900 dark:text-white">{manufacturer.support_email}</strong>
        {manufacturer.support_phone && (
          <span> | Phone: <a href={`tel:${manufacturer.support_phone}`} className="text-blue-600 dark:text-blue-400">{manufacturer.support_phone}</a></span>
        )}
      </p>

      {sendSuccess && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-600 dark:text-green-400 rounded-lg mb-6">
          {sendSuccess}
        </div>
      )}

      {sendError && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 rounded-lg mb-6">
          {sendError}
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Subject *</label>
          <input
            type="text"
            value={subject}
            onChange={(e) => onSubjectChange(e.target.value)}
            required
            placeholder="e.g., Technical issue with equipment"
            className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Message *</label>
          <textarea
            value={message}
            onChange={(e) => onMessageChange(e.target.value)}
            required
            placeholder="Describe the issue or question..."
            rows={5}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📷 Attach Photos</label>
          <input type="file" accept="image/*" multiple capture="environment" onChange={onPhotoSelect} className="text-gray-600 dark:text-gray-400" />
          {photos.length > 0 && <p className="text-sm text-gray-500 mt-2">{photos.length} photo(s) selected</p>}
        </div>

        {documents.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">📎 Attach Technical Documents</label>
            <div className="flex flex-wrap gap-3">
              {documents.map((doc) => (
                <label
                  key={doc.id}
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg cursor-pointer border-2 transition-colors ${
                    selectedDocs.includes(doc.id)
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <input type="checkbox" checked={selectedDocs.includes(doc.id)} onChange={() => onDocToggle(doc.id)} className="sr-only" />
                  <span>{getIcon(doc.document_type)}</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{doc.title}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={isSending}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors disabled:cursor-not-allowed"
        >
          {isSending ? 'Sending...' : '📧 Send to Manufacturer'}
        </button>
      </form>
    </div>
  );
}

function ContactClientTab({
  client,
  subject,
  message,
  photos,
  isSending,
  sendSuccess,
  sendError,
  onSubjectChange,
  onMessageChange,
  onPhotoSelect,
  onSubmit,
}: {
  client: EquipmentDetail['client'];
  subject: string;
  message: string;
  photos: File[];
  isSending: boolean;
  sendSuccess: string;
  sendError: string;
  onSubjectChange: (v: string) => void;
  onMessageChange: (v: string) => void;
  onPhotoSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
}) {
  if (!client.email) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">📨</div>
        <p className="text-gray-500 dark:text-gray-400 mb-2">Client does not have an email configured.</p>
        {client.phone && (
          <p className="text-gray-600 dark:text-gray-300">
            You can call: <a href={`tel:${client.phone}`} className="text-blue-600 dark:text-blue-400">{client.phone}</a>
          </p>
        )}
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Contact Client</h3>
      <p className="text-gray-600 dark:text-gray-400 mb-4">
        Send email to: <strong className="text-gray-900 dark:text-white">{client.email}</strong>
        {client.phone && (
          <span> | Phone: <a href={`tel:${client.phone}`} className="text-blue-600 dark:text-blue-400">{client.phone}</a></span>
        )}
      </p>

      <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-400 rounded-lg mb-6">
        <strong>Note:</strong> Technical documents from the internal database cannot be shared with clients. You can only attach photos and intervention reports.
      </div>

      {sendSuccess && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-600 dark:text-green-400 rounded-lg mb-6">
          {sendSuccess}
        </div>
      )}

      {sendError && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 rounded-lg mb-6">
          {sendError}
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Subject *</label>
          <input
            type="text"
            value={subject}
            onChange={(e) => onSubjectChange(e.target.value)}
            required
            placeholder="e.g., Update on your equipment repair"
            className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Message *</label>
          <textarea
            value={message}
            onChange={(e) => onMessageChange(e.target.value)}
            required
            placeholder="Write your message to the client..."
            rows={5}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📷 Attach Photos</label>
          <input type="file" accept="image/*" multiple capture="environment" onChange={onPhotoSelect} className="text-gray-600 dark:text-gray-400" />
          {photos.length > 0 && <p className="text-sm text-gray-500 mt-2">{photos.length} photo(s) selected</p>}
        </div>

        <button
          type="submit"
          disabled={isSending}
          className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors disabled:cursor-not-allowed"
        >
          {isSending ? 'Sending...' : '📨 Send to Client'}
        </button>
      </form>
    </div>
  );
}

'use client';

/**
 * Admin-Only Page Example
 *
 * Demonstrates role-based access control
 */

import React from 'react';
import { useProtectedRoute } from '@/hooks/use-protected-route';

export default function AdminPage() {
  const { user, isLoading } = useProtectedRoute({ requiredRole: 'admin' });

  if (isLoading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <p>Loading...</p>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect in useProtectedRoute
  }

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px' }}>
      <h1 style={{ marginBottom: '20px' }}>Admin Dashboard</h1>

      <div style={{
        padding: '20px',
        backgroundColor: '#fff3cd',
        borderRadius: '8px',
        marginBottom: '20px',
        borderLeft: '4px solid #ffc107'
      }}>
        <p style={{ margin: 0, fontWeight: 'bold' }}>
          🔐 This page is only accessible to users with the "admin" role.
        </p>
      </div>

      <div style={{
        padding: '20px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px'
      }}>
        <h2 style={{ marginBottom: '15px' }}>User Information</h2>
        <div style={{ marginBottom: '10px' }}>
          <strong>Email:</strong> {user.email}
        </div>
        <div style={{ marginBottom: '10px' }}>
          <strong>User ID:</strong> {user.uid}
        </div>
        <div style={{ marginBottom: '10px' }}>
          <strong>Role:</strong> <span style={{
            backgroundColor: '#28a745',
            color: 'white',
            padding: '2px 8px',
            borderRadius: '4px',
            fontSize: '14px'
          }}>{user.role}</span>
        </div>
      </div>

      <div style={{ marginTop: '20px' }}>
        <a href="/dashboard" style={{ color: '#007bff', textDecoration: 'none' }}>
          ← Back to Dashboard
        </a>
      </div>
    </div>
  );
}


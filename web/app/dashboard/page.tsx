'use client';

/**
 * Dashboard Page (Protected Route Example)
 *
 * Demonstrates:
 * - Protected route that requires authentication
 * - Using user data from auth context
 * - Logout functionality
 */

import React, { useEffect } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Redirect to login if not authenticated (after loading)
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null; // Will redirect in useEffect
  }

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '30px',
        paddingBottom: '20px',
        borderBottom: '1px solid #ddd'
      }}>
        <h1>Dashboard</h1>
        <button
          onClick={handleLogout}
          style={{
            padding: '10px 20px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Logout
        </button>
      </div>

      <div style={{
        padding: '20px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h2 style={{ marginBottom: '15px' }}>Welcome, {user.email}!</h2>
        <div style={{ marginBottom: '10px' }}>
          <strong>User ID:</strong> {user.uid}
        </div>
        <div style={{ marginBottom: '10px' }}>
          <strong>Email:</strong> {user.email}
        </div>
        <div style={{ marginBottom: '10px' }}>
          <strong>Role:</strong> {user.role}
        </div>
      </div>

      <div style={{
        padding: '20px',
        backgroundColor: '#e7f3ff',
        borderRadius: '8px',
        borderLeft: '4px solid #007bff'
      }}>
        <h3 style={{ marginBottom: '10px' }}>🔒 Security Features Active</h3>
        <ul style={{ marginLeft: '20px', lineHeight: '1.8' }}>
          <li>✅ Access token stored in-memory (not in localStorage)</li>
          <li>✅ Refresh token in HttpOnly cookie (protected from XSS)</li>
          <li>✅ Automatic token refresh on 401 errors</li>
          <li>✅ Credentials sent with every request (withCredentials: true)</li>
          <li>✅ Silent refresh on app initialization</li>
        </ul>
      </div>

      <div style={{ marginTop: '30px', textAlign: 'center', color: '#666' }}>
        <p>
          Note: If you refresh this page, the app will automatically attempt
          to restore your session using the refresh token cookie.
        </p>
      </div>
    </div>
  );
}


'use client';

import { useAuth } from "@/contexts/auth-context";
import { useRouter } from "next/navigation";

export default function Home() {
  const { isAuthenticated, user, isLoading } = useAuth();
  const router = useRouter();

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#f5f5f5',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '600px',
        width: '100%',
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '40px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        {isAuthenticated && user ? (
          <div>
            <div style={{
              padding: '20px',
              backgroundColor: '#e8f5e9',
              borderRadius: '8px',
              marginBottom: '20px',
              borderLeft: '4px solid #4caf50'
            }}>
              <p style={{ margin: 0, color: '#2e7d32', fontWeight: 'bold' }}>
                You are logged in as: {user.email}
              </p>
            </div>

            <button
              onClick={() => router.push('/dashboard')}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '16px',
                cursor: 'pointer',
                fontWeight: '500'
              }}
            >
              Go to Dashboard
            </button>
          </div>
        ) : (
          <div>
            <div style={{
              padding: '20px',
              backgroundColor: '#fff3cd',
              borderRadius: '8px',
              marginBottom: '30px',
              borderLeft: '4px solid #ffc107'
            }}>
              <p style={{ margin: 0, color: '#856404', fontSize: '14px' }}>
                ⚠️ You are not logged in. Please login or register to continue.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '15px', marginBottom: '30px' }}>
              <button
                onClick={() => router.push('/login')}
                style={{
                  flex: 1,
                  padding: '12px',
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '16px',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}
              >
                Login
              </button>

              <button
                onClick={() => router.push('/register')}
                style={{
                  flex: 1,
                  padding: '12px',
                  backgroundColor: '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '16px',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}
              >
                Register
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

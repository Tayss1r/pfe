'use client';

/**
 * Protected Route Hook
 *
 * Use this hook to protect pages that require authentication.
 * Automatically redirects to login if user is not authenticated.
 *
 * Usage:
 * ```tsx
 * 'use client';
 * import { useProtectedRoute } from '@/hooks/use-protected-route';
 *
 * export default function ProtectedPage() {
 *   const { user, isLoading } = useProtectedRoute();
 *
 *   if (isLoading) return <div>Loading...</div>;
 *
 *   return <div>Welcome {user.email}</div>;
 * }
 * ```
 */

import { useEffect } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { useRouter } from 'next/navigation';

interface UseProtectedRouteOptions {
  redirectTo?: string;
  requiredRole?: string;
}

export const useProtectedRoute = (options: UseProtectedRouteOptions = {}) => {
  const { redirectTo = '/login', requiredRole } = options;
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      // Not authenticated - redirect to login
      if (!isAuthenticated) {
        router.push(redirectTo);
        return;
      }

      // Check role if required
      if (requiredRole && user && user.role !== requiredRole) {
        router.push('/unauthorized');
        return;
      }
    }
  }, [isLoading, isAuthenticated, user, router, redirectTo, requiredRole]);

  return {
    user,
    isLoading,
    isAuthenticated,
  };
};


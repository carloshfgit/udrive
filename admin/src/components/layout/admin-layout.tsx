'use client';

import React from 'react';
import { useAuth } from '@/hooks/use-auth';
import { Sidebar } from '@/components/layout/sidebar';
import { TopBar } from '@/components/layout/topbar';
import { usePathname } from 'next/navigation';

export function AdminLayout({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, isLoading } = useAuth();
    const pathname = usePathname();

    // Se estiver carregando, mostra um loading simples (ou skeleton)
    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center bg-background">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    // Se não estiver autenticado e não for a página de login, o middleware cuida do redirecionamento
    // Mas por garantia, se for página de login, renderiza apenas o children
    if (pathname === '/login') {
        return <>{children}</>;
    }

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            <Sidebar />
            <div className="flex flex-1 flex-col overflow-hidden">
                <TopBar />
                <main className="flex-1 overflow-y-auto p-6 bg-zinc-50/50 dark:bg-zinc-950/50">
                    {children}
                </main>
            </div>
        </div>
    );
}

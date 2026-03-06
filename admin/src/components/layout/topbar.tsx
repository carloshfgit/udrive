'use client';

import React from 'react';
import { useAuth } from '@/hooks/use-auth';
import { User as UserIcon, Bell } from 'lucide-react';

export function TopBar() {
    const { user } = useAuth();

    return (
        <header className="flex h-16 items-center justify-end border-b bg-card px-6 gap-4">
            <button className="p-2 rounded-full hover:bg-accent text-muted-foreground transition-colors">
                <Bell size={20} />
            </button>

            <div className="flex items-center gap-3 pl-4 border-l">
                <div className="flex flex-col items-end">
                    <span className="text-sm font-semibold">{user?.full_name}</span>
                    <span className="text-xs text-muted-foreground capitalize">{user?.user_type}</span>
                </div>
                <div className="h-10 w-10 flex items-center justify-center rounded-full bg-accent border">
                    <UserIcon size={20} className="text-muted-foreground" />
                </div>
            </div>
        </header>
    );
}

'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Users,
    Calendar,
    AlertCircle,
    LogOut,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/use-auth';

const menuItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Usuários', href: '/users', icon: Users },
    { name: 'Agendamentos', href: '/schedulings', icon: Calendar },
    { name: 'Disputas', href: '/disputes', icon: AlertCircle },
];

export function Sidebar() {
    const pathname = usePathname();
    const { logout } = useAuth();
    const [isCollapsed, setIsCollapsed] = React.useState(false);

    return (
        <aside
            className={cn(
                "flex flex-col border-r bg-card transition-all duration-300 ease-in-out",
                isCollapsed ? "w-20" : "w-64"
            )}
        >
            <div className="flex h-16 items-center justify-between px-4 border-b">
                {!isCollapsed && <span className="text-xl font-bold tracking-tight text-primary">GoDrive Admin</span>}
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="p-1.5 rounded-md hover:bg-accent hover:text-accent-foreground"
                >
                    {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                </button>
            </div>

            <nav className="flex-1 space-y-1 p-2 mt-4">
                {menuItems.map((item) => {
                    const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground",
                                isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground",
                                isCollapsed && "justify-center"
                            )}
                        >
                            <item.icon size={20} />
                            {!isCollapsed && <span>{item.name}</span>}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-2 border-t">
                <button
                    onClick={logout}
                    className={cn(
                        "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-destructive hover:text-destructive-foreground text-muted-foreground",
                        isCollapsed && "justify-center"
                    )}
                >
                    <LogOut size={20} />
                    {!isCollapsed && <span>Sair</span>}
                </button>
            </div>
        </aside>
    );
}

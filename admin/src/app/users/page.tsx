"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useUsers } from "@/hooks/useUsers";
import { User, AdminUserFilters } from "@/types/user";

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

import { RoleBadge } from "@/components/shared/RoleBadge";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Pagination } from "@/components/shared/Pagination";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export default function UsersPage() {
    const router = useRouter();
    const searchParams = useSearchParams();

    // Parse Initial State from URL
    const initialPage = Number(searchParams.get("page")) || 1;
    const initialQ = searchParams.get("q") || "";
    const initialUserType = (searchParams.get("user_type") as "student" | "instructor" | "admin" | "all") || "all";
    const initialIsActive = searchParams.get("is_active") || "all";

    // Local State for Inputs (Debounced)
    const [searchTerm, setSearchTerm] = useState(initialQ);

    // Filters Derived Directly from URL params, instead of keeping a synced state
    const filters: AdminUserFilters = {
        page: initialPage,
        size: 10,
        q: initialQ,
        user_type: initialUserType,
        is_active: initialIsActive,
    };

    const { data, isLoading, isError } = useUsers(filters);

    // Debounce Search Term Input
    useEffect(() => {
        const handler = setTimeout(() => {
            const params = new URLSearchParams(searchParams);
            if (searchTerm) {
                params.set("q", searchTerm);
            } else {
                params.delete("q");
            }
            params.set("page", "1"); // reset to page 1 on new search
            router.push(`?${params.toString()}`);
        }, 500);

        return () => clearTimeout(handler);
    }, [searchTerm, router, searchParams, initialQ]);

    // Handle Select Changes
    const handleFilterChange = (key: string, value: string) => {
        const params = new URLSearchParams(searchParams);
        if (value && value !== "all") {
            params.set(key, value);
        } else {
            params.delete(key);
        }
        params.set("page", "1");
        router.push(`?${params.toString()}`);
    };

    const handleRowClick = (userId: string) => {
        router.push(`/users/${userId}`);
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Usuários</h1>
                    <p className="text-muted-foreground">
                        Gerencie os alunos, instrutores e administradores do sistema.
                    </p>
                </div>
            </div>

            <Card>
                <CardHeader className="pb-3">
                    <CardTitle>Filtros</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <Input
                            placeholder="Buscar por nome, email ou CPF..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full"
                        />

                        <Select
                            defaultValue={initialUserType}
                            onValueChange={(val) => handleFilterChange("user_type", val)}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="Tipo de Usuário" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Todos os tipos</SelectItem>
                                <SelectItem value="student">Aluno</SelectItem>
                                <SelectItem value="instructor">Instrutor</SelectItem>
                                <SelectItem value="admin">Administrador</SelectItem>
                            </SelectContent>
                        </Select>

                        <Select
                            defaultValue={initialIsActive}
                            onValueChange={(val) => handleFilterChange("is_active", val)}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="Status da Conta" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Todos os status</SelectItem>
                                <SelectItem value="true">Ativo</SelectItem>
                                <SelectItem value="false">Inativo</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-0">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Nome</TableHead>
                                <TableHead>Email</TableHead>
                                <TableHead>Tipo</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Data de Cadastro</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {isLoading ? (
                                Array.from({ length: 5 }).map((_, i) => (
                                    <TableRow key={i}>
                                        <TableCell><Skeleton className="h-4 w-[150px]" /></TableCell>
                                        <TableCell><Skeleton className="h-4 w-[200px]" /></TableCell>
                                        <TableCell><Skeleton className="h-6 w-[80px]" /></TableCell>
                                        <TableCell><Skeleton className="h-6 w-[70px]" /></TableCell>
                                        <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                                    </TableRow>
                                ))
                            ) : isError ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center text-red-500 py-6">
                                        Erro ao carregar os usuários. Tente novamente mais tarde.
                                    </TableCell>
                                </TableRow>
                            ) : data?.items?.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center py-6 text-muted-foreground">
                                        Nenhum usuário encontrado com os filtros selecionados.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                data?.items.map((user: User) => (
                                    <TableRow
                                        key={user.id}
                                        className="cursor-pointer hover:bg-muted/50 transition-colors"
                                        onClick={() => handleRowClick(user.id)}
                                    >
                                        <TableCell className="font-medium">{user.full_name}</TableCell>
                                        <TableCell className="text-muted-foreground">{user.email}</TableCell>
                                        <TableCell>
                                            <RoleBadge role={user.user_type} />
                                        </TableCell>
                                        <TableCell>
                                            <StatusBadge isActive={user.is_active} />
                                        </TableCell>
                                        <TableCell className="text-sm text-muted-foreground">
                                            {format(new Date(user.created_at), "dd 'de' MMM, yyyy", {
                                                locale: ptBR,
                                            })}
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {data && data.pages > 1 && (
                <Pagination
                    currentPage={data.page}
                    totalPages={data.pages}
                />
            )}
        </div>
    );
}

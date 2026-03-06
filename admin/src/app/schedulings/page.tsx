"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useSchedulings } from "@/hooks/useSchedulings";
import { Scheduling, SchedulingFilters, SchedulingStatus } from "@/types/scheduling";

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

import { StatusBadge } from "@/components/shared/StatusBadge";
import { Pagination } from "@/components/shared/Pagination";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export default function SchedulingsPage() {
    const router = useRouter();
    const searchParams = useSearchParams();

    // Parse Initial State from URL
    const initialPage = Number(searchParams.get("page")) || 1;
    const initialStatus = (searchParams.get("status") as SchedulingStatus) || undefined;
    const initialStudentId = searchParams.get("student_id") || "";
    const initialInstructorId = searchParams.get("instructor_id") || "";

    // Local state for debounced inputs
    const [studentInput, setStudentInput] = useState(initialStudentId);
    const [instructorInput, setInstructorInput] = useState(initialInstructorId);

    const filters: SchedulingFilters = {
        page: initialPage,
        limit: 10,
        status: initialStatus,
        student_id: initialStudentId || undefined,
        instructor_id: initialInstructorId || undefined,
    };

    const { data, isLoading, isError } = useSchedulings(filters);

    // Debounce for inputs
    useEffect(() => {
        const handler = setTimeout(() => {
            const params = new URLSearchParams(searchParams);
            let changed = false;

            if (studentInput !== (searchParams.get("student_id") || "")) {
                if (studentInput) params.set("student_id", studentInput);
                else params.delete("student_id");
                changed = true;
            }

            if (instructorInput !== (searchParams.get("instructor_id") || "")) {
                if (instructorInput) params.set("instructor_id", instructorInput);
                else params.delete("instructor_id");
                changed = true;
            }

            if (changed) {
                params.set("page", "1");
                router.push(`?${params.toString()}`);
            }
        }, 500);

        return () => clearTimeout(handler);
    }, [studentInput, instructorInput, router, searchParams]);

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

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Agendamentos</h1>
                <p className="text-muted-foreground">
                    Gerencie todos os agendamentos realizados no sistema.
                </p>
            </div>

            <Card>
                <CardHeader className="pb-3">
                    <CardTitle>Filtros</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <Input
                            placeholder="Buscar por ID do Aluno..."
                            value={studentInput}
                            onChange={(e) => setStudentInput(e.target.value)}
                        />
                        <Input
                            placeholder="Buscar por ID do Instrutor..."
                            value={instructorInput}
                            onChange={(e) => setInstructorInput(e.target.value)}
                        />
                        <Select
                            defaultValue={initialStatus || "all"}
                            onValueChange={(val) => handleFilterChange("status", val)}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="Status" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Todos os status</SelectItem>
                                <SelectItem value="pending">Pendente</SelectItem>
                                <SelectItem value="confirmed">Confirmado</SelectItem>
                                <SelectItem value="cancelled">Cancelado</SelectItem>
                                <SelectItem value="completed">Concluído</SelectItem>
                                <SelectItem value="reschedule_requested">Reagendamento</SelectItem>
                                <SelectItem value="disputed">Em Disputa</SelectItem>
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
                                <TableHead>Aluno</TableHead>
                                <TableHead>Instrutor</TableHead>
                                <TableHead>Data/Hora</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Valor</TableHead>
                                <TableHead>Categoria</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {isLoading ? (
                                Array.from({ length: 5 }).map((_, i) => (
                                    <TableRow key={i}>
                                        <TableCell><Skeleton className="h-4 w-[150px]" /></TableCell>
                                        <TableCell><Skeleton className="h-4 w-[150px]" /></TableCell>
                                        <TableCell><Skeleton className="h-4 w-[120px]" /></TableCell>
                                        <TableCell><Skeleton className="h-6 w-[100px]" /></TableCell>
                                        <TableCell><Skeleton className="h-4 w-[80px]" /></TableCell>
                                    </TableRow>
                                ))
                            ) : isError ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center text-red-500 py-6">
                                        Erro ao carregar os agendamentos. Tente novamente mais tarde.
                                    </TableCell>
                                </TableRow>
                            ) : data?.schedulings.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center py-6 text-muted-foreground">
                                        Nenhum agendamento encontrado.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                data?.schedulings.map((scheduling: Scheduling) => (
                                    <TableRow
                                        key={scheduling.id}
                                        className="cursor-pointer hover:bg-muted/50 transition-colors"
                                        onClick={() => router.push(`/schedulings/${scheduling.id}`)}
                                    >
                                        <TableCell className="font-medium">
                                            {scheduling.student_name || scheduling.student_id}
                                        </TableCell>
                                        <TableCell>
                                            {scheduling.instructor_name || scheduling.instructor_id}
                                        </TableCell>
                                        <TableCell>
                                            {format(new Date(scheduling.scheduled_datetime), "dd/MM/yyyy HH:mm", {
                                                locale: ptBR,
                                            })}
                                        </TableCell>
                                        <TableCell>
                                            <StatusBadge status={scheduling.status} />
                                        </TableCell>
                                        <TableCell>
                                            {new Intl.NumberFormat('pt-BR', {
                                                style: 'currency',
                                                currency: 'BRL'
                                            }).format(scheduling.price)}
                                        </TableCell>
                                        <TableCell>
                                            {scheduling.lesson_category || "-"}
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {data && data.total_count > filters.limit! && (
                <Pagination
                    currentPage={filters.page!}
                    totalPages={Math.ceil(data.total_count / filters.limit!)}
                />
            )}
        </div>
    );
}

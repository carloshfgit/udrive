import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Pagination } from "@/components/shared/Pagination";
import { Dispute, DisputeReason } from '@/types/dispute';
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { useRouter } from 'next/navigation';

interface DisputesTableProps {
    disputes: Dispute[];
    totalCount: number;
    currentPage: number;
    totalPages: number;
    isLoading: boolean;
    isError: boolean;
}

const reasonLabels: Record<string, string> = {
    [DisputeReason.NO_SHOW]: "Instrutor não compareceu",
    [DisputeReason.VEHICLE_PROBLEM]: "Problema no veículo",
    [DisputeReason.OTHER]: "Outro motivo",
};

export function DisputesTable({
    disputes,
    currentPage,
    totalPages,
    isLoading,
    isError
}: DisputesTableProps) {
    const router = useRouter();

    const handleRowClick = (id: string) => {
        router.push(`/disputes/${id}`);
    };

    return (
        <div className="space-y-4">
            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Motivo</TableHead>
                            <TableHead>Aluno</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Data de Abertura</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {isLoading ? (
                            Array.from({ length: 5 }).map((_, i) => (
                                <TableRow key={i}>
                                    <TableCell><Skeleton className="h-4 w-[200px]" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-[150px]" /></TableCell>
                                    <TableCell><Skeleton className="h-6 w-[100px]" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-[120px]" /></TableCell>
                                </TableRow>
                            ))
                        ) : isError ? (
                            <TableRow>
                                <TableCell colSpan={4} className="text-center text-red-500 py-10">
                                    Erro ao carregar as disputas.
                                </TableCell>
                            </TableRow>
                        ) : disputes.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={4} className="text-center py-10 text-muted-foreground">
                                    Nenhuma disputa encontrada.
                                </TableCell>
                            </TableRow>
                        ) : (
                            disputes.map((dispute) => (
                                <TableRow 
                                    key={dispute.id}
                                    className="cursor-pointer hover:bg-muted/50 transition-colors"
                                    onClick={() => handleRowClick(dispute.id)}
                                >
                                    <TableCell className="font-medium">
                                        {reasonLabels[dispute.reason as string] || dispute.reason}
                                    </TableCell>
                                    <TableCell>
                                        {dispute.student_name || "N/A"}
                                    </TableCell>
                                    <TableCell>
                                        <StatusBadge status={dispute.status as any} />
                                    </TableCell>
                                    <TableCell className="text-sm text-muted-foreground">
                                        {format(new Date(dispute.created_at), "dd/MM/yyyy HH:mm", {
                                            locale: ptBR,
                                        })}
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
            />
        </div>
    );
}

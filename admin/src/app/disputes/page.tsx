"use client";

import React from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useDisputes } from "@/hooks/useDisputes";
import { DisputeFilters } from "@/components/disputes/DisputeFilters";
import { DisputesTable } from "@/components/disputes/DisputesTable";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AdminDisputeFilters } from "@/types/dispute";

export default function DisputesPage() {
    const router = useRouter();
    const searchParams = useSearchParams();

    // Filtros derivados da URL
    const page = Number(searchParams.get("page")) || 1;
    const status = searchParams.get("status") || "all";

    const filters: AdminDisputeFilters = {
        page,
        size: 10,
        status,
    };

    const { data, isLoading, isError } = useDisputes(filters);

    const handleStatusChange = (newStatus: string) => {
        const params = new URLSearchParams(searchParams);
        if (newStatus && newStatus !== "all") {
            params.set("status", newStatus);
        } else {
            params.delete("status");
        }
        params.set("page", "1"); // Reseta para primeira página ao filtrar
        router.push(`?${params.toString()}`);
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Gestão de Disputas</h1>
                <p className="text-muted-foreground">
                    Analise e resolva conflitos entre alunos e instrutores.
                </p>
            </div>

            <Card>
                <CardHeader className="pb-3">
                    <CardTitle>Filtros</CardTitle>
                </CardHeader>
                <CardContent>
                    <DisputeFilters 
                        status={status} 
                        onStatusChange={handleStatusChange} 
                    />
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-0">
                    <DisputesTable
                        disputes={data?.items || []}
                        totalCount={data?.total || 0}
                        currentPage={data?.page || page}
                        totalPages={data?.pages || 1}
                        isLoading={isLoading}
                        isError={isError}
                    />
                </CardContent>
            </Card>
        </div>
    );
}

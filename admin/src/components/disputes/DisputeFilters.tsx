import React from 'react';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { DisputeStatus } from '@/types/dispute';

interface DisputeFiltersProps {
    status: string;
    onStatusChange: (status: string) => void;
}

export function DisputeFilters({ status, onStatusChange }: DisputeFiltersProps) {
    return (
        <div className="flex flex-wrap items-center gap-4 py-4">
            <div className="w-full max-w-[200px]">
                <Select value={status} onValueChange={onStatusChange}>
                    <SelectTrigger>
                        <SelectValue placeholder="Filtrar por Status" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">Todos os Status</SelectItem>
                        <SelectItem value={DisputeStatus.OPEN}>Urgente (Abertas)</SelectItem>
                        <SelectItem value={DisputeStatus.UNDER_REVIEW}>Em Análise</SelectItem>
                        <SelectItem value={DisputeStatus.RESOLVED}>Resolvidas</SelectItem>
                    </SelectContent>
                </Select>
            </div>
        </div>
    );
}

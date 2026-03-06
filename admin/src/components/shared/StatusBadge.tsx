import { Badge } from "@/components/ui/badge";
import { SchedulingStatus } from "@/types/scheduling";

interface StatusBadgeProps {
    isActive?: boolean;
    status?: SchedulingStatus;
}

export function StatusBadge({ isActive, status }: StatusBadgeProps) {
    if (status) {
        const statusConfig: Record<SchedulingStatus, { label: string; className: string }> = {
            pending: { 
                label: "Pendente", 
                className: "bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-200" 
            },
            confirmed: { 
                label: "Confirmado", 
                className: "bg-blue-100 text-blue-800 hover:bg-blue-200 border-blue-200" 
            },
            cancelled: { 
                label: "Cancelado", 
                className: "bg-red-100 text-red-800 hover:bg-red-200 border-red-200" 
            },
            completed: { 
                label: "Concluído", 
                className: "bg-green-100 text-green-800 hover:bg-green-200 border-green-200" 
            },
            reschedule_requested: { 
                label: "Reagendamento", 
                className: "bg-purple-100 text-purple-800 hover:bg-purple-200 border-purple-200" 
            },
            disputed: { 
                label: "Em Disputa", 
                className: "bg-orange-100 text-orange-800 hover:bg-orange-200 border-orange-200" 
            },
        };

        const config = statusConfig[status] || { label: status, className: "" };

        return (
            <Badge variant="outline" className={config.className}>
                {config.label}
            </Badge>
        );
    }

    return (
        <Badge
            variant={isActive ? "default" : "destructive"}
            className={
                isActive
                    ? "bg-green-100 text-green-800 hover:bg-green-200 border-green-200"
                    : "bg-red-100 text-red-800 hover:bg-red-200 border-red-200"
            }
        >
            {isActive ? "Ativo" : "Inativo"}
        </Badge>
    );
}

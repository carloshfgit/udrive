import { Badge } from "@/components/ui/badge";

interface StatusBadgeProps {
    isActive: boolean;
}

export function StatusBadge({ isActive }: StatusBadgeProps) {
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

import { Badge } from "@/components/ui/badge";
import { UserType } from "@/types/user";

interface RoleBadgeProps {
    role: UserType;
}

export function RoleBadge({ role }: RoleBadgeProps) {
    const roleStyles: Record<UserType, { label: string; className: string }> = {
        student: {
            label: "Aluno",
            className: "bg-blue-100 text-blue-800 hover:bg-blue-200 border-blue-200",
        },
        instructor: {
            label: "Instrutor",
            className: "bg-purple-100 text-purple-800 hover:bg-purple-200 border-purple-200",
        },
        admin: {
            label: "Admin",
            className: "bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-200",
        },
    };

    const { label, className } = roleStyles[role];

    return (
        <Badge variant="outline" className={className}>
            {label}
        </Badge>
    );
}

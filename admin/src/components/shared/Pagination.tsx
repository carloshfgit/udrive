"use client";

import {
    PaginationContent,
    PaginationItem,
    PaginationLink,
    PaginationNext,
    PaginationPrevious,
    Pagination as PaginationUI,
} from "@/components/ui/pagination";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

interface PaginationProps {
    currentPage: number;
    totalPages: number;
}

export function Pagination({ currentPage, totalPages }: PaginationProps) {
    const pathname = usePathname();
    const searchParams = useSearchParams();
    const router = useRouter();

    if (totalPages <= 1) return null;

    const createPageURL = (pageNumber: number) => {
        const params = new URLSearchParams(searchParams);
        params.set("page", pageNumber.toString());
        return `${pathname}?${params.toString()}`;
    };

    const handlePageChange = (
        e: React.MouseEvent<HTMLAnchorElement>,
        pageNumber: number
    ) => {
        e.preventDefault();
        router.push(createPageURL(pageNumber));
    };

    return (
        <PaginationUI className="mt-4 justify-end">
            <PaginationContent>
                <PaginationItem>
                    {currentPage > 1 ? (
                        <PaginationPrevious
                            href={createPageURL(currentPage - 1)}
                            onClick={(e) => handlePageChange(e, currentPage - 1)}
                        />
                    ) : (
                        <PaginationPrevious
                            href="#"
                            className="pointer-events-none opacity-50"
                        />
                    )}
                </PaginationItem>

                <PaginationItem>
                    <span className="text-sm px-4">
                        Página {currentPage} de {totalPages}
                    </span>
                </PaginationItem>

                <PaginationItem>
                    {currentPage < totalPages ? (
                        <PaginationNext
                            href={createPageURL(currentPage + 1)}
                            onClick={(e) => handlePageChange(e, currentPage + 1)}
                        />
                    ) : (
                        <PaginationNext
                            href="#"
                            className="pointer-events-none opacity-50"
                        />
                    )}
                </PaginationItem>
            </PaginationContent>
        </PaginationUI>
    );
}

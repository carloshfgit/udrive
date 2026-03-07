"use client";

import React from "react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { CreditCard, CheckCircle2, XCircle } from "lucide-react";

import { DisputePayment } from "@/types/dispute";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";

interface PaymentSelectorProps {
    payments: DisputePayment[];
    selectedIds: string[];
    onSelectionChange: (ids: string[]) => void;
    isLoading?: boolean;
    readOnly?: boolean;
}

function getStatusBadge(status: string) {
    switch (status) {
        case "completed":
            return <Badge className="bg-green-600 hover:bg-green-700">Pago</Badge>;
        case "refunded":
            return <Badge className="bg-red-600 hover:bg-red-700">Reembolsado</Badge>;
        case "partially_refunded":
            return <Badge className="bg-orange-600 hover:bg-orange-700">Parcialmente Reembolsado</Badge>;
        case "pending":
            return <Badge variant="outline">Pendente</Badge>;
        case "processing":
            return <Badge className="bg-blue-600 hover:bg-blue-700">Processando</Badge>;
        case "failed":
            return <Badge variant="destructive">Falhou</Badge>;
        default:
            return <Badge variant="outline">{status}</Badge>;
    }
}

function isEligibleForRefund(payment: DisputePayment): boolean {
    return payment.status === "completed" && !payment.mp_refund_id;
}

export default function PaymentSelector({
    payments,
    selectedIds,
    onSelectionChange,
    isLoading = false,
    readOnly = false,
}: PaymentSelectorProps) {
    const eligiblePayments = payments.filter(isEligibleForRefund);
    const allEligibleSelected = eligiblePayments.length > 0 &&
        eligiblePayments.every(p => selectedIds.includes(p.id));

    const handleToggle = (paymentId: string) => {
        if (readOnly) return;
        if (selectedIds.includes(paymentId)) {
            onSelectionChange(selectedIds.filter(id => id !== paymentId));
        } else {
            onSelectionChange([...selectedIds, paymentId]);
        }
    };

    const handleSelectAllEligible = () => {
        if (readOnly) return;
        if (allEligibleSelected) {
            onSelectionChange([]);
        } else {
            onSelectionChange(eligiblePayments.map(p => p.id));
        }
    };

    if (isLoading) {
        return (
            <Card>
                <CardHeader>
                    <Skeleton className="h-6 w-48" />
                </CardHeader>
                <CardContent className="space-y-3">
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-10 w-full" />
                </CardContent>
            </Card>
        );
    }

    if (payments.length === 0) {
        return (
            <Card>
                <CardContent className="py-6 text-center text-muted-foreground">
                    Nenhum pagamento encontrado para esta disputa.
                </CardContent>
            </Card>
        );
    }

    const totalSelected = payments
        .filter(p => selectedIds.includes(p.id))
        .reduce((sum, p) => sum + p.amount, 0);

    return (
        <Card className="border-blue-200 dark:border-blue-900">
            <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                    <CreditCard className="h-4 w-4 text-blue-500" />
                    Aulas do Checkout ({payments.length})
                </CardTitle>
                <CardDescription>
                    Selecione as aulas que devem ser reembolsadas. Aulas já reembolsadas estão desabilitadas.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                {!readOnly && eligiblePayments.length > 1 && (
                    <div className="flex items-center gap-3">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleSelectAllEligible}
                            type="button"
                        >
                            {allEligibleSelected ? (
                                <>
                                    <XCircle className="mr-1.5 h-3.5 w-3.5" />
                                    Limpar Seleção
                                </>
                            ) : (
                                <>
                                    <CheckCircle2 className="mr-1.5 h-3.5 w-3.5" />
                                    Selecionar Todos Elegíveis
                                </>
                            )}
                        </Button>
                        {selectedIds.length > 0 && (
                            <span className="text-sm text-muted-foreground">
                                {selectedIds.length} de {eligiblePayments.length} selecionada(s)
                            </span>
                        )}
                    </div>
                )}

                <div className="rounded-md border">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                {!readOnly && <TableHead className="w-12"></TableHead>}
                                <TableHead>Data da Aula</TableHead>
                                <TableHead className="text-right">Valor</TableHead>
                                <TableHead>Status</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {payments.map((payment) => {
                                const eligible = isEligibleForRefund(payment);
                                const isSelected = selectedIds.includes(payment.id);

                                return (
                                    <TableRow
                                        key={payment.id}
                                        className={
                                            isSelected
                                                ? "bg-blue-50/50 dark:bg-blue-900/10"
                                                : !eligible
                                                ? "opacity-60"
                                                : ""
                                        }
                                    >
                                        {!readOnly && (
                                            <TableCell>
                                                <Checkbox
                                                    checked={isSelected}
                                                    onCheckedChange={() => handleToggle(payment.id)}
                                                    disabled={!eligible}
                                                    aria-label={`Selecionar aula de ${payment.scheduled_datetime ? format(new Date(payment.scheduled_datetime), "dd/MM/yyyy", { locale: ptBR }) : "data desconhecida"}`}
                                                />
                                            </TableCell>
                                        )}
                                        <TableCell className="font-medium">
                                            {payment.scheduled_datetime
                                                ? format(
                                                      new Date(payment.scheduled_datetime),
                                                      "dd/MM/yyyy 'às' HH:mm",
                                                      { locale: ptBR }
                                                  )
                                                : "Data não disponível"}
                                        </TableCell>
                                        <TableCell className="text-right font-bold text-green-600">
                                            R$ {payment.amount.toFixed(2)}
                                        </TableCell>
                                        <TableCell>{getStatusBadge(payment.status)}</TableCell>
                                    </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                </div>

                {selectedIds.length > 0 && !readOnly && (
                    <div className="flex justify-between items-center pt-2 px-1 text-sm border-t">
                        <span className="text-muted-foreground">Total a reembolsar:</span>
                        <span className="font-bold text-lg text-green-600">
                            R$ {totalSelected.toFixed(2)}
                        </span>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

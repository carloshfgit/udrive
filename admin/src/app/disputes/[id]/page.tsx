"use client";

import React, { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { 
    ArrowLeft, 
    AlertCircle, 
    Calendar, 
    User, 
    Phone, 
    Mail, 
    MessageSquare, 
    Clock, 
    ShieldCheck, 
    CheckCircle,
    Info,
    Gavel,
    FileText,
    History,
    CreditCard
} from "lucide-react";

import { useDispute, useUpdateDisputeStatus, useResolveDispute, useDisputePayments } from "@/hooks/useDisputes";
import { DisputeStatus, DisputeResolution, DisputePayment, ResolveDisputeData } from "@/types/dispute";
import PaymentSelector from "@/components/disputes/PaymentSelector";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
    Select, 
    SelectContent, 
    SelectItem, 
    SelectTrigger, 
    SelectValue 
} from "@/components/ui/select";
import { StatusBadge } from "@/components/shared/StatusBadge";

export default function DisputeDetailsPage() {
    const params = useParams();
    const router = useRouter();
    const disputeId = params.id as string;

    const { data: dispute, isLoading, isError } = useDispute(disputeId);
    const updateStatusMutation = useUpdateDisputeStatus();
    const resolveMutation = useResolveDispute();

    const [isResolving, setIsResolving] = useState(false);
    const [selectedPaymentIds, setSelectedPaymentIds] = useState<string[]>([]);
    const [resolutionData, setResolutionData] = useState<ResolveDisputeData>({
        resolution: "",
        resolution_notes: "",
        refund_type: "full",
        new_datetime: ""
    });

    // Buscar pagamentos quando o admin está resolvendo a favor do aluno
    const shouldFetchPayments = isResolving && resolutionData.resolution === DisputeResolution.FAVOR_STUDENT;
    const { data: payments, isLoading: paymentsLoading } = useDisputePayments(disputeId, shouldFetchPayments);

    // Buscar pagamentos para exibir na visualização de disputa resolvida
    const isResolved = dispute?.status === DisputeStatus.RESOLVED;
    const showResolvedPayments = isResolved && dispute?.resolution === DisputeResolution.FAVOR_STUDENT;
    const { data: resolvedPayments } = useDisputePayments(disputeId, showResolvedPayments || false);

    if (isLoading) {
        return (
            <div className="space-y-6 animate-pulse">
                <div className="flex items-center gap-4">
                    <Skeleton className="h-10 w-10 rounded-full" />
                    <Skeleton className="h-8 w-64" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Skeleton className="h-64 col-span-1 md:col-span-2" />
                    <Skeleton className="h-64" />
                </div>
            </div>
        );
    }

    if (isError || !dispute) {
        return (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
                <AlertCircle className="h-12 w-12 text-destructive" />
                <h2 className="text-2xl font-bold">Disputa não encontrada</h2>
                <p className="text-muted-foreground">Não foi possível carregar os detalhes da disputa.</p>
                <Button onClick={() => router.back()}>Voltar para a lista</Button>
            </div>
        );
    }

    const handleStartAnalysis = async () => {
        try {
            await updateStatusMutation.mutateAsync({ 
                id: disputeId, 
                status: DisputeStatus.UNDER_REVIEW 
            });
        } catch (error) {
            console.error("Error starting analysis:", error);
        }
    };

    const handleResolve = async () => {
        if (!resolutionData.resolution || !resolutionData.resolution_notes) {
            alert("Por favor, preencha a resolução e as notas.");
            return;
        }

        if (resolutionData.resolution_notes.length < 5) {
            alert("As notas de resolução devem ter pelo menos 5 caracteres.");
            return;
        }

        // Limpar o payload para evitar erro 422 no backend
        const payload: ResolveDisputeData = {
            resolution: resolutionData.resolution,
            resolution_notes: resolutionData.resolution_notes,
        };

        if (resolutionData.resolution === DisputeResolution.FAVOR_STUDENT) {
            if (selectedPaymentIds.length === 0) {
                alert("Por favor, selecione ao menos uma aula para reembolsar.");
                return;
            }
            // Determinar refund_type baseado na seleção
            const eligibleCount = payments?.filter(
                (p: DisputePayment) => p.status === "completed" && !p.mp_refund_id
            ).length || 0;
            payload.refund_type = selectedPaymentIds.length >= eligibleCount ? "full" : "partial";
            payload.payment_ids_to_refund = selectedPaymentIds;
        }

        if (resolutionData.resolution === DisputeResolution.RESCHEDULED) {
            if (!resolutionData.new_datetime) {
                alert("Por favor, selecione uma nova data/hora para o reagendamento.");
                return;
            }
            payload.new_datetime = resolutionData.new_datetime;
        }

        try {
            await resolveMutation.mutateAsync({
                id: disputeId,
                data: payload
            });
            setIsResolving(false);
        } catch (error) {
            console.error("Error resolving dispute:", error);
        }
    };

    const getResolutionLabel = (res?: string | null) => {
        switch (res) {
            case DisputeResolution.FAVOR_INSTRUCTOR: return "Favorável ao Instrutor";
            case DisputeResolution.FAVOR_STUDENT: return "Favorável ao Aluno";
            case DisputeResolution.RESCHEDULED: return "Reagendamento";
            default: return "Não resolvida";
        }
    };

    return (
        <div className="space-y-6 pb-12">
            {/* Header / Actions */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div className="flex items-center gap-4">
                    <Button variant="outline" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-3xl font-bold tracking-tight">Disputa #{disputeId.substring(0, 8)}</h1>
                            <StatusBadge status={dispute.status} />
                        </div>
                        <p className="text-muted-foreground flex items-center gap-2 text-sm">
                            <Calendar className="h-3 w-3" /> Aberta em {format(new Date(dispute.created_at), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                        </p>
                    </div>
                </div>
                
                <div className="flex items-center gap-3">
                    {!isResolved && dispute.status === DisputeStatus.OPEN && (
                        <Button 
                            variant="default" 
                            className="bg-orange-600 hover:bg-orange-700 text-white"
                            onClick={handleStartAnalysis}
                            disabled={updateStatusMutation.isPending}
                        >
                            <ShieldCheck className="mr-2 h-4 w-4" />
                            {updateStatusMutation.isPending ? "Processando..." : "Iniciar Análise"}
                        </Button>
                    )}
                    
                    {!isResolved && !isResolving && (
                        <Button 
                            variant="default"
                            onClick={() => setIsResolving(true)}
                        >
                            <Gavel className="mr-2 h-4 w-4" />
                            Resolver Disputa
                        </Button>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Content: Dispute Info & Resolution */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Dispute Info */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-lg">
                                <MessageSquare className="h-5 w-5 text-primary" /> Detalhes da Disputa
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <InfoItem 
                                    label="Motivo" 
                                    value={<Badge variant="outline" className="capitalize">{dispute.reason.replace('_', ' ')}</Badge>} 
                                />
                                <InfoItem label="Status Atual" value={<StatusBadge status={dispute.status} />} />
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-semibold text-muted-foreground uppercase">Descrição do Aluno</label>
                                <div className="p-4 bg-muted/30 rounded-lg border text-sm leading-relaxed italic">
                                    "{dispute.description}"
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                                <InfoItem icon={<Phone className="h-4 w-4" />} label="Telefone de Contato" value={dispute.contact_phone} />
                                <InfoItem icon={<Mail className="h-4 w-4" />} label="E-mail de Contato" value={dispute.contact_email} />
                            </div>
                        </CardContent>
                    </Card>

                    {/* Resolution Form or Result */}
                    {isResolved ? (
                        <Card className="border-green-200 dark:border-green-900 bg-green-50/30 dark:bg-green-900/10">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-lg text-green-700 dark:text-green-400">
                                    <CheckCircle className="h-5 w-5" /> Resolução Finalizada
                                </CardTitle>
                                <CardDescription>
                                    Resolvido em {format(new Date(dispute.resolved_at!), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <InfoItem label="Decisão" value={<strong>{getResolutionLabel(dispute.resolution)}</strong>} />
                                    {dispute.refund_type && (
                                        <InfoItem label="Reembolso" value={<Badge className="bg-green-600 capitalize">{dispute.refund_type === 'full' ? 'Total' : 'Parcial'}</Badge>} />
                                    )}
                                </div>

                                {showResolvedPayments && resolvedPayments && resolvedPayments.length > 0 && (
                                    <PaymentSelector
                                        payments={resolvedPayments}
                                        selectedIds={[]}
                                        onSelectionChange={() => {}}
                                        readOnly={true}
                                    />
                                )}
                                <div className="space-y-2">
                                    <label className="text-xs font-semibold text-muted-foreground uppercase">Notas do Admin</label>
                                    <div className="p-4 bg-background rounded-lg border text-sm italic">
                                        {dispute.resolution_notes}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ) : isResolving ? (
                        <Card className="border-primary ring-1 ring-primary/20">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-lg">
                                    <Gavel className="h-5 w-5 text-primary" /> Formular Resolução
                                </CardTitle>
                                <CardDescription>
                                    Tome uma decisão final para esta disputa. Esta ação é irreversível.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium">Resolução</label>
                                        <Select 
                                            value={resolutionData.resolution} 
                                            onValueChange={(v) => setResolutionData({...resolutionData, resolution: v})}
                                        >
                                            <SelectTrigger>
                                                <SelectValue placeholder="Selecione a decisão" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value={DisputeResolution.FAVOR_STUDENT}>Favorável ao Aluno (Reembolso)</SelectItem>
                                                <SelectItem value={DisputeResolution.FAVOR_INSTRUCTOR}>Favorável ao Instrutor</SelectItem>
                                                <SelectItem value={DisputeResolution.RESCHEDULED}>Reagendamento Forçado</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    {resolutionData.resolution === DisputeResolution.FAVOR_STUDENT && (
                                        <div className="col-span-1 md:col-span-2">
                                            <PaymentSelector
                                                payments={payments || []}
                                                selectedIds={selectedPaymentIds}
                                                onSelectionChange={setSelectedPaymentIds}
                                                isLoading={paymentsLoading}
                                            />
                                        </div>
                                    )}

                                    {resolutionData.resolution === DisputeResolution.RESCHEDULED && (
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium">Nova Data/Hora</label>
                                            <Input 
                                                type="datetime-local" 
                                                value={resolutionData.new_datetime || ""}
                                                onChange={(e) => setResolutionData({...resolutionData, new_datetime: e.target.value})}
                                            />
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Notas Internas / Justificativa</label>
                                    <Textarea 
                                        placeholder="Descreva o motivo da decisão..." 
                                        className="min-h-[120px]"
                                        value={resolutionData.resolution_notes}
                                        onChange={(e) => setResolutionData({...resolutionData, resolution_notes: e.target.value})}
                                    />
                                </div>

                                <div className="flex justify-end gap-3 pt-4 border-t">
                                    <Button variant="outline" onClick={() => setIsResolving(false)}>Cancelar</Button>
                                    <Button 
                                        onClick={handleResolve} 
                                        disabled={resolveMutation.isPending}
                                    >
                                        {resolveMutation.isPending ? "Enviando..." : "Confirmar Resolução"}
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ) : null}
                </div>

                {/* Sidebar: Scheduling Info */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-lg">
                                <Info className="h-5 w-5 text-primary" /> Agendamento
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-3">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                                        <User className="h-5 w-5 text-primary" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-semibold text-muted-foreground uppercase">Aluno</p>
                                        <p className="text-sm font-bold">{dispute.student_name || "N/A"}</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 rounded-full bg-secondary/20 flex items-center justify-center">
                                        <User className="h-5 w-5 text-secondary-foreground" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-semibold text-muted-foreground uppercase">Instrutor</p>
                                        <p className="text-sm font-bold">{dispute.instructor_name || "N/A"}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="border-t pt-4 space-y-3">
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-muted-foreground flex items-center gap-1">
                                        <Calendar className="h-4 w-4" /> Data da Aula
                                    </span>
                                    <span className="font-medium">
                                        {dispute.scheduled_datetime 
                                            ? format(new Date(dispute.scheduled_datetime), "dd/MM/yyyy HH:mm") 
                                            : "N/A"}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-muted-foreground flex items-center gap-1">
                                        <CreditCard className="h-4 w-4" /> Valor
                                    </span>
                                    <span className="font-bold text-green-600">
                                        {dispute.price !== undefined ? `R$ ${dispute.price.toFixed(2)}` : "N/A"}
                                    </span>
                                </div>
                            </div>

                            <Button 
                                variant="outline" 
                                className="w-full mt-4"
                                onClick={() => router.push(`/schedulings/${dispute.scheduling_id}`)}
                            >
                                <ArrowLeft className="mr-2 h-4 w-4 rotate-180" />
                                Ver Agendamento
                            </Button>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base flex items-center gap-2">
                                <History className="h-4 w-4" /> Histórico
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="text-xs space-y-3">
                            <div className="flex gap-3">
                                <div className="flex flex-col items-center">
                                    <div className="h-2 w-2 rounded-full bg-primary" />
                                    <div className="w-0.5 grow bg-border" />
                                </div>
                                <div>
                                    <p className="font-semibold">Disputa Aberta</p>
                                    <p className="text-muted-foreground">{format(new Date(dispute.created_at), "dd/MM/yyyy HH:mm")}</p>
                                </div>
                            </div>
                            
                            {dispute.status !== DisputeStatus.OPEN && (
                                <div className="flex gap-3">
                                    <div className="flex flex-col items-center">
                                        <div className="h-2 w-2 rounded-full bg-orange-500" />
                                        <div className="w-0.5 grow bg-border" />
                                    </div>
                                    <div>
                                        <p className="font-semibold text-orange-600">Em Análise</p>
                                        <p className="text-muted-foreground">{format(new Date(dispute.updated_at), "dd/MM/yyyy HH:mm")}</p>
                                    </div>
                                </div>
                            )}

                            {isResolved && (
                                <div className="flex gap-3">
                                    <div className="flex flex-col items-center">
                                        <div className="h-2 w-2 rounded-full bg-green-500" />
                                    </div>
                                    <div>
                                        <p className="font-semibold text-green-600">Resolvida</p>
                                        <p className="text-muted-foreground">{format(new Date(dispute.resolved_at!), "dd/MM/yyyy HH:mm")}</p>
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

function InfoItem({ icon, label, value }: { icon?: React.ReactNode, label: string, value: React.ReactNode }) {
    return (
        <div className="space-y-1">
            <div className="text-xs font-semibold text-muted-foreground uppercase flex items-center gap-1">
                {icon} {label}
            </div>
            <div className="text-sm font-medium">{value}</div>
        </div>
    );
}

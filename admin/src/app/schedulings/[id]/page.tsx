"use client";

import React, { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useScheduling } from "@/hooks/useScheduling";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { 
    ArrowLeft, 
    Calendar, 
    Clock, 
    User, 
    Car, 
    CreditCard, 
    AlertCircle, 
    CheckCircle2, 
    XCircle, 
    History,
    ExternalLink
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { 
    Dialog, 
    DialogContent, 
    DialogHeader, 
    DialogTitle, 
    DialogFooter 
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

export default function SchedulingDetailsPage() {
    const params = useParams();
    const router = useRouter();
    const schedulingId = params.id as string;
    
    const { scheduling, isLoading, isError, cancelScheduling, isCancelling } = useScheduling(schedulingId);
    
    const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
    const [cancelReason, setCancelReason] = useState("");

    if (isLoading) {
        return (
            <div className="space-y-6">
                <div className="flex items-center gap-4">
                    <Skeleton className="h-10 w-10 rounded-full" />
                    <Skeleton className="h-8 w-64" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Skeleton className="h-48" />
                    <Skeleton className="h-48" />
                </div>
                <Skeleton className="h-96 w-full" />
            </div>
        );
    }

    if (isError || !scheduling) {
        return (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
                <AlertCircle className="h-12 w-12 text-destructive" />
                <h2 className="text-2xl font-bold">Agendamento não encontrado</h2>
                <Button onClick={() => router.back()}>Voltar</Button>
            </div>
        );
    }

    const handleCancel = async () => {
        if (!cancelReason) return;
        try {
            await cancelScheduling({ reason: cancelReason });
            setIsCancelModalOpen(false);
            setCancelReason("");
        } catch (error) {
            console.error(error);
        }
    };

    const timelineEvents = [
        { label: "Solicitado", date: scheduling.created_at, icon: <History className="h-4 w-4" />, color: "text-blue-500" },
        { label: "Confirmado", date: scheduling.status !== 'pending' ? scheduling.updated_at : null, icon: <CheckCircle2 className="h-4 w-4" />, color: "text-green-500" },
        { label: "Iniciado", date: scheduling.started_at, icon: <Clock className="h-4 w-4" />, color: "text-indigo-500" },
        { label: "Concluído", date: scheduling.completed_at, icon: <CheckCircle2 className="h-4 w-4" />, color: "text-green-600" },
        { label: "Cancelado", date: scheduling.cancelled_at, icon: <XCircle className="h-4 w-4" />, color: "text-red-500" },
    ].filter(event => event.date).sort((a, b) => new Date(a.date!).getTime() - new Date(b.date!).getTime());

    return (
        <div className="space-y-6 pb-12">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div className="flex items-center gap-4">
                    <Button variant="outline" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-2xl font-bold tracking-tight">Agendamento</h1>
                            <StatusBadge status={scheduling.status} />
                        </div>
                        <p className="text-sm text-muted-foreground font-mono">ID: {scheduling.id}</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    {scheduling.status !== 'cancelled' && scheduling.status !== 'completed' && (
                        <Button variant="destructive" onClick={() => setIsCancelModalOpen(true)}>
                            Cancelar Agendamento
                        </Button>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Users info */}
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                            <User className="h-4 w-4 text-primary" /> Participantes
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-1">
                            <p className="text-xs text-muted-foreground uppercase font-semibold">Aluno</p>
                            <p className="text-sm font-medium flex items-center justify-between">
                                {scheduling.student_name}
                                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => router.push(`/users/${scheduling.student_id}`)}>
                                    <ExternalLink className="h-3 w-3" />
                                </Button>
                            </p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-xs text-muted-foreground uppercase font-semibold">Instrutor</p>
                            <p className="text-sm font-medium flex items-center justify-between">
                                {scheduling.instructor_name}
                                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => router.push(`/users/${scheduling.instructor_id}`)}>
                                    <ExternalLink className="h-3 w-3" />
                                </Button>
                            </p>
                        </div>
                    </CardContent>
                </Card>

                {/* Lesson Info */}
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-primary" /> Aula
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex justify-between items-center border-b pb-2">
                            <span className="text-sm text-muted-foreground">Data/Hora</span>
                            <span className="text-sm font-medium">
                                {format(new Date(scheduling.scheduled_datetime), "dd/MM/yyyy HH:mm", { locale: ptBR })}
                            </span>
                        </div>
                        <div className="flex justify-between items-center border-b pb-2">
                            <span className="text-sm text-muted-foreground">Duração</span>
                            <span className="text-sm font-medium">{scheduling.duration_minutes} min</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-muted-foreground">Categoria</span>
                            <Badge variant="outline">{scheduling.lesson_category}</Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-muted-foreground font-medium flex items-center gap-1">
                                <Car className="h-3 w-3" /> Veículo
                            </span>
                            <span className="text-sm text-muted-foreground">
                                {scheduling.vehicle_ownership === 'instructor' ? 'Do Instrutor' : 'Do Aluno'}
                            </span>
                        </div>
                    </CardContent>
                </Card>

                {/* Payment Info */}
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                            <CreditCard className="h-4 w-4 text-primary" /> Pagamento
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex justify-between items-center border-b pb-2">
                            <span className="text-sm text-muted-foreground">Status</span>
                            <Badge variant={scheduling.payment_status === 'paid' ? 'default' : 'secondary'} className="capitalize">
                                {scheduling.payment_status === 'paid' ? 'Pago' : scheduling.payment_status}
                            </Badge>
                        </div>
                        <div className="flex justify-between items-center border-b pb-2">
                            <span className="text-sm text-muted-foreground">Preço Base</span>
                            <span className="text-sm font-medium">R$ {scheduling.applied_base_price?.toFixed(2) || scheduling.price.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between items-center pt-1">
                            <span className="text-sm font-bold">Total Final</span>
                            <span className="text-lg font-bold text-green-600">R$ {scheduling.applied_final_price?.toFixed(2) || scheduling.price.toFixed(2)}</span>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Timeline */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Linha do Tempo</CardTitle>
                        <CardDescription>Eventos registrados para este agendamento.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="relative space-y-4 border-l-2 border-muted ml-3 pl-6">
                            {timelineEvents.map((event, index) => (
                                <div key={index} className="relative">
                                    <div className={`absolute -left-[31px] top-1 p-1 bg-background border-2 rounded-full ${event.color}`}>
                                        {event.icon}
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold">{event.label}</span>
                                        <span className="text-xs text-muted-foreground">
                                            {format(new Date(event.date!), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                        
                        {scheduling.status === 'cancelled' && scheduling.cancellation_reason && (
                            <div className="mt-6 p-4 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 rounded-lg">
                                <h4 className="text-sm font-bold text-red-800 dark:text-red-400 mb-1">Motivo do Cancelamento</h4>
                                <p className="text-sm text-red-700 dark:text-red-300">{scheduling.cancellation_reason}</p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Dispute Link (Placeholder) */}
                {scheduling.status === 'disputed' && (
                    <Card className="border-orange-200 bg-orange-50 dark:bg-orange-950/20 dark:border-orange-900">
                        <CardHeader>
                            <CardTitle className="text-lg flex items-center gap-2 text-orange-800 dark:text-orange-400">
                                <AlertCircle className="h-5 w-5" /> Disputa Aberta
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4 text-orange-700 dark:text-orange-300">
                            <p className="text-sm">Este agendamento possui uma disputa ativa aberta pelo aluno.</p>
                            <Button variant="default" className="bg-orange-600 hover:bg-orange-700 text-white w-full" onClick={() => router.push(`/disputes?scheduling_id=${scheduling.id}`)}>
                                Ver Detalhes da Disputa
                            </Button>
                        </CardContent>
                    </Card>
                )}
            </div>

            {/* Cancel Modal */}
            <Dialog open={isCancelModalOpen} onOpenChange={setIsCancelModalOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Cancelar Agendamento como Admin</DialogTitle>
                    </DialogHeader>
                    <div className="py-4 space-y-4">
                        <p className="text-sm text-muted-foreground">
                            O cancelamento administrativo reverte o status da aula e não está sujeito às travas normais de tempo. Por favor, informe o motivo.
                        </p>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Motivo do Cancelamento</label>
                            <Input 
                                placeholder="Descreva o motivo..." 
                                value={cancelReason} 
                                onChange={(e) => setCancelReason(e.target.value)}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsCancelModalOpen(false)}>Cancelar</Button>
                        <Button variant="destructive" disabled={!cancelReason || isCancelling} onClick={handleCancel}>
                            {isCancelling ? "Cancelando..." : "Confirmar Cancelamento"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}

"use client";

import React from "react";
import { useParams, useRouter } from "next/navigation";
import { useUser } from "@/hooks/useUser";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { ArrowLeft, User as UserIcon, Calendar, CheckCircle, XCircle, AlertCircle, Car, GraduationCap, Phone, Mail, FileText, Activity } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

import { RoleBadge } from "@/components/shared/RoleBadge";
import { StatusBadge } from "@/components/shared/StatusBadge";

export default function UserDetailsPage() {
    const params = useParams();
    const router = useRouter();
    const userId = params.id as string;

    const { user, isLoading, isError, toggleStatus, isTogglingStatus } = useUser(userId);

    if (isLoading) {
        return (
            <div className="space-y-6 animate-pulse">
                <div className="flex items-center gap-4">
                    <Skeleton className="h-10 w-10 rounded-full" />
                    <Skeleton className="h-8 w-64" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Skeleton className="h-48 col-span-1 md:col-span-2" />
                    <Skeleton className="h-48" />
                </div>
            </div>
        );
    }

    if (isError || !user) {
        return (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
                <AlertCircle className="h-12 w-12 text-destructive" />
                <h2 className="text-2xl font-bold">Usuário não encontrado</h2>
                <p className="text-muted-foreground">Não foi possível carregar os detalhes do usuário.</p>
                <Button onClick={() => router.back()}>Voltar para a lista</Button>
            </div>
        );
    }

    const isInstructor = user.user_type === "instructor";
    const isStudent = user.user_type === "student";

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
                            <h1 className="text-3xl font-bold tracking-tight">{user.full_name}</h1>
                            <RoleBadge role={user.user_type} />
                        </div>
                        <p className="text-muted-foreground flex items-center gap-2">
                            <Mail className="h-3 w-3" /> {user.email}
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <Button 
                        variant={user.is_active ? "destructive" : "default"}
                        disabled={isTogglingStatus}
                        onClick={() => toggleStatus()}
                    >
                        {user.is_active ? "Desativar Conta" : "Ativar Conta"}
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Basic Info */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-lg">
                            <UserIcon className="h-5 w-5 text-primary" /> Dados Pessoais
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-8">
                        <InfoItem icon={<Mail className="h-4 w-4" />} label="Email" value={user.email} />
                        <InfoItem icon={<Phone className="h-4 w-4" />} label="Telefone" value={user.phone || "Não informado"} />
                        <InfoItem icon={<FileText className="h-4 w-4" />} label="CPF" value={user.cpf || "Não informado"} />
                        <InfoItem icon={<Calendar className="h-4 w-4" />} label="Nascimento" value={user.birth_date ? format(new Date(user.birth_date), "dd/MM/yyyy") : "Não informado"} />
                        <InfoItem icon={<Activity className="h-4 w-4" />} label="Status" value={<StatusBadge isActive={user.is_active} />} />
                        <InfoItem icon={<Calendar className="h-4 w-4" />} label="Cadastrado em" value={format(new Date(user.created_at), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })} />
                    </CardContent>
                </Card>

                {/* Profile Details (Conditional) */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-lg">
                            {isInstructor ? (
                                <><Car className="h-5 w-5 text-primary" /> Perfil Profissional</>
                            ) : (
                                <><GraduationCap className="h-5 w-5 text-primary" /> Progresso do Aluno</>
                            )}
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {user.profile ? (
                            <div className="space-y-4">
                                {isInstructor && (
                                    <>
                                        <div className="flex justify-between items-center border-b pb-2">
                                            <span className="text-sm font-medium">Veículo</span>
                                            <span className="text-sm text-muted-foreground">{user.profile.vehicle_type || "N/A"}</span>
                                        </div>
                                        <div className="flex justify-between items-center border-b pb-2">
                                            <span className="text-sm font-medium">Categoria CNH</span>
                                            <Badge variant="outline">{user.profile.license_category || "B"}</Badge>
                                        </div>
                                        <div className="flex justify-between items-center border-b pb-2">
                                            <span className="text-sm font-medium">Valor/Hora</span>
                                            <span className="text-sm font-bold text-green-600">R$ {user.profile.hourly_rate?.toFixed(2)}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm font-medium">Avaliação</span>
                                            <div className="flex items-center gap-1">
                                                <span className="text-sm font-bold">{user.profile.rating?.toFixed(1)}</span>
                                                <span className="text-xs text-muted-foreground">({user.profile.total_reviews} reviews)</span>
                                            </div>
                                        </div>
                                    </>
                                )}
                                {isStudent && (
                                    <>
                                        <div className="flex justify-between items-center border-b pb-2">
                                            <span className="text-sm font-medium">Estágio</span>
                                            <Badge variant="secondary">{user.profile.learning_stage || "Iniciante"}</Badge>
                                        </div>
                                        <div className="flex justify-between items-center border-b pb-2">
                                            <span className="text-sm font-medium">Objetivo CNH</span>
                                            <Badge variant="outline">{user.profile.license_category_goal || "B"}</Badge>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm font-medium">Total de Aulas</span>
                                            <span className="text-sm font-bold">{user.profile.total_lessons || 0}</span>
                                        </div>
                                    </>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-6 text-muted-foreground text-sm italic">
                                Perfil ainda não configurado ou usuário é Administrador.
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Recent Schedulings */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Agendamentos Recentes</CardTitle>
                    <CardDescription>As últimas aulas agendadas por este usuário.</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Data/Hora</TableHead>
                                <TableHead>{isInstructor ? "Aluno" : "Instrutor"}</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="text-right">Valor</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {!user.recent_schedulings || user.recent_schedulings.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={4} className="text-center py-8 text-muted-foreground italic text-sm">
                                        Nenhum agendamento encontrado para este usuário.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                user.recent_schedulings.map((sched) => (
                                    <TableRow key={sched.id}>
                                        <TableCell className="font-medium">
                                            {format(new Date(sched.scheduled_datetime), "dd/MM/yyyy HH:mm")}
                                        </TableCell>
                                        <TableCell>
                                            {isInstructor ? sched.student_name : sched.instructor_name}
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant="outline" className="capitalize">{sched.status}</Badge>
                                        </TableCell>
                                        <TableCell className="text-right font-medium">
                                            R$ {sched.price.toFixed(2)}
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}

function InfoItem({ icon, label, value }: { icon: React.ReactNode, label: string, value: React.ReactNode }) {
    return (
        <div className="space-y-1">
            <div className="text-xs font-semibold text-muted-foreground uppercase flex items-center gap-1">
                {icon} {label}
            </div>
            <div className="text-sm font-medium">{value}</div>
        </div>
    );
}

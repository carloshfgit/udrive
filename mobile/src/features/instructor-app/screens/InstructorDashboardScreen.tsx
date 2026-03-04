/**
 * InstructorDashboardScreen
 *
 * Tela de dashboard/métricas do instrutor.
 * Exibe ganhos totais, ganhos do mês, aulas concluídas, avaliação média e aulas recentes.
 */

import React, { useCallback } from 'react';
import {
    View,
    Text,
    SafeAreaView,
    ScrollView,
    RefreshControl,
    ActivityIndicator,
    TouchableOpacity,
} from 'react-native';
import { TrendingUp, Star, BookOpen, DollarSign, Calendar, ChevronRight } from 'lucide-react-native';
import { useFocusEffect } from '@react-navigation/native';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

import { Card, Avatar, ProgressBar, Input } from '../../../shared/components';
import { useInstructorDashboard } from '../hooks/useInstructorDashboard';
import { useInstructorSettingsStore } from '../stores/instructorSettingsStore';
import { useAuth } from '../../../features/auth/hooks/useAuth';
import { Scheduling } from '../api/scheduleApi';

// ============= Helpers =============

function formatCurrency(value: number | string): string {
    const num = Number(value) || 0;
    return `R$ ${num.toFixed(2).replace('.', ',')}`;
}

// ============= Subcomponents =============

interface MetricCardProps {
    icon: React.ReactNode;
    label: string;
    value: string;
    subtext?: string;
    color: string;
}

function MetricCard({ icon, label, value, subtext, color }: MetricCardProps) {
    return (
        <View
            className="bg-white rounded-[32px] p-5 mb-4 border border-neutral-100/50 flex-1 min-w-[46%] mx-1 shadow-sm shadow-neutral-200"
        >
            <View
                className="w-12 h-12 rounded-2xl items-center justify-center mb-4 shadow-inner"
                style={{ backgroundColor: `${color}15` }}
            >
                {icon}
            </View>
            <View>
                <Text className="text-neutral-400 text-[10px] font-bold uppercase tracking-widest mb-1">{label}</Text>
                <Text className="text-xl font-black text-neutral-900 tracking-tight">{value}</Text>
                {subtext && (
                    <View className="mt-2 py-1 px-2.5 bg-neutral-50 rounded-lg self-start">
                        <Text className="text-neutral-500 text-[9px] font-black uppercase tracking-tighter">{subtext}</Text>
                    </View>
                )}
            </View>
        </View>
    );
}

interface LessonRowProps {
    scheduling: Scheduling;
}

function LessonRow({ scheduling }: LessonRowProps) {
    const date = new Date(scheduling.scheduled_datetime);
    return (
        <View className="flex-row items-center justify-between py-4 border-b border-neutral-50 px-2">
            <View className="flex-1">
                <Text className="text-neutral-900 font-bold text-sm">
                    {scheduling.student_name || 'Aluno'}
                </Text>
                <Text className="text-neutral-400 text-[11px] font-medium mt-1">
                    {format(date, "dd 'de' MMMM 'às' HH:mm", { locale: ptBR })}
                </Text>
            </View>
            <View className="bg-green-50 px-3 py-1.5 rounded-xl border border-green-100/50">
                <Text className="text-green-600 font-black text-xs">
                    +{formatCurrency(Number(scheduling.price))}
                </Text>
            </View>
        </View>
    );
}

// ============= Main Screen =============

export function InstructorDashboardScreen() {
    const { user } = useAuth();
    const { earnings, reviews, recentLessons, isLoading, isError, refetch } =
        useInstructorDashboard();
    const { monthlyGoal, setMonthlyGoal, loadSettings } = useInstructorSettingsStore();

    useFocusEffect(
        useCallback(() => {
            refetch();
            loadSettings();
            // eslint-disable-next-line react-hooks/exhaustive-deps
        }, [])
    );

    const now = new Date();
    const monthName = format(now, 'MMMM', { locale: ptBR });
    const monthNameCapitalized = monthName.charAt(0).toUpperCase() + monthName.slice(1);

    if (isLoading) {
        return (
            <SafeAreaView className="flex-1 bg-white items-center justify-center">
                <ActivityIndicator size="large" color="#2563EB" />
            </SafeAreaView>
        );
    }

    if (isError) {
        return (
            <SafeAreaView className="flex-1 bg-white items-center justify-center p-6">
                <Text className="text-lg font-semibold text-gray-900 text-center mb-4">
                    Erro ao carregar o dashboard
                </Text>
                <TouchableOpacity
                    onPress={refetch}
                    className="bg-blue-600 px-6 py-3 rounded-full"
                    activeOpacity={0.8}
                >
                    <Text className="text-white font-bold">Tentar Novamente</Text>
                </TouchableOpacity>
            </SafeAreaView>
        );
    }

    const totalEarnings = earnings?.total_earnings ?? 0;
    const monthlyEarnings = earnings?.monthly_earnings ?? 0;
    const completedLessons = earnings?.completed_lessons ?? 0;
    const baseLessonPrice = earnings?.base_lesson_price ?? 0;
    const rating = reviews?.rating ?? 0;
    const totalReviews = reviews?.total_reviews ?? 0;

    const missingAmount = Math.max(0, monthlyGoal - monthlyEarnings);
    const missingLessons = baseLessonPrice > 0 ? Math.ceil(missingAmount / baseLessonPrice) : 0;

    return (
        <SafeAreaView className="flex-1 bg-primary-50">
            {/* Header Rico */}
            <View className="px-5 pt-8 pb-8 bg-white rounded-b-[40px] shadow-md shadow-neutral-100 z-10">
                <View className="flex-row justify-between items-center">
                    <View>
                        <Text className="text-neutral-400 text-[10px] font-black uppercase tracking-[2px]">
                            {format(new Date(), "EEEE, d 'de' MMMM", { locale: ptBR })}
                        </Text>
                        <Text className="text-3xl font-black text-neutral-900 mt-1">
                            Olá, {user?.full_name.split(' ')[0] || 'Instrutor'}
                        </Text>
                    </View>
                    <Avatar
                        source={user?.avatarUrl}
                        fallback={user?.full_name?.[0] || 'I'}
                        size="lg"
                        className="border-4 border-neutral-50 shadow-sm"
                    />
                </View>

                <View className="mt-6 flex-row items-center">
                    <View className="bg-primary-50 px-4 py-2 rounded-2xl flex-row items-center border border-primary-100/50">
                        <TrendingUp size={14} color="#3b82f6" />
                        <Text className="text-primary-600 text-[10px] font-black ml-2 uppercase tracking-widest">
                            Dashboard Ativo
                        </Text>
                    </View>
                    <View className="ml-3 bg-amber-50 px-4 py-2 rounded-2xl flex-row items-center border border-amber-100/50">
                        <Star size={14} color="#f59e0b" />
                        <Text className="text-amber-600 text-[10px] font-black ml-2 uppercase tracking-widest">
                            {reviews?.rating ? `${reviews.rating.toFixed(1)} Rating` : '—'}
                        </Text>
                    </View>
                </View>
            </View>

            <ScrollView
                className="flex-1 px-4"
                contentContainerStyle={{ paddingBottom: 32 }}
                showsVerticalScrollIndicator={false}
                refreshControl={
                    <RefreshControl refreshing={isLoading} onRefresh={refetch} />
                }
            >
                {/* Metrics Grid */}
                <View className="flex-row flex-wrap justify-between mt-6 px-1">
                    <MetricCard
                        icon={<DollarSign size={22} color="#22c55e" />}
                        label="Ganhos Totais"
                        value={formatCurrency(totalEarnings)}
                        subtext={`${completedLessons} ${completedLessons === 1 ? 'aula' : 'aulas'}`}
                        color="#22c55e"
                    />
                    <MetricCard
                        icon={<Calendar size={22} color="#3b82f6" />}
                        label={`${monthNameCapitalized}`}
                        value={formatCurrency(monthlyEarnings)}
                        subtext="Ganhos do mês"
                        color="#3b82f6"
                    />
                    <MetricCard
                        icon={<BookOpen size={22} color="#8b5cf6" />}
                        label="Aulas"
                        value={String(completedLessons)}
                        subtext="Concluídas"
                        color="#8b5cf6"
                    />
                    <MetricCard
                        icon={<Star size={22} color="#f59e0b" />}
                        label="Avaliação"
                        value={rating > 0 ? rating.toFixed(1) : '—'}
                        subtext={totalReviews > 0 ? `${totalReviews} ${totalReviews === 1 ? 'nota' : 'notas'}` : 'Sem notas'}
                        color="#f59e0b"
                    />
                </View>

                <View className="mt-4 mb-8 bg-neutral-900 rounded-[40px] overflow-hidden shadow-2xl shadow-black/30 border border-neutral-800/50">
                    {/* Goal Input Header */}
                    <View className="p-8 pb-4 border-b border-neutral-800/50">
                        <View className="flex-row items-center mb-4">
                            <Calendar size={18} color="#6b7280" />
                            <Text className="text-neutral-400 font-black ml-2 uppercase tracking-[2px] text-[10px]">Meta de {monthNameCapitalized}</Text>
                        </View>
                        <Input
                            placeholder="Digite sua meta mensal..."
                            keyboardType="numeric"
                            value={monthlyGoal > 0 ? monthlyGoal.toString() : ''}
                            onChangeText={(text) => {
                                const val = parseFloat(text.replace(',', '.'));
                                if (!isNaN(val)) {
                                    setMonthlyGoal(val);
                                } else if (text === '') {
                                    setMonthlyGoal(0);
                                }
                            }}
                            innerContainerClassName="bg-neutral-800 border-neutral-700 h-14 rounded-2xl"
                            inputClassName="text-white font-bold text-lg px-2"
                            leftIcon={<DollarSign size={18} color="#3b82f6" />}
                            placeholderTextColor="#4b5563"
                        />
                    </View>

                    {/* Progress Card Content */}
                    {monthlyGoal > 0 ? (
                        <View className="p-8">
                            <View className="absolute top-0 right-0 p-6 opacity-5">
                                <TrendingUp size={120} color="#FFFFFF" />
                            </View>

                            <View className="flex-row justify-between items-end mb-6">
                                <View>
                                    <View className="flex-row items-center mb-2">
                                        <View className="w-2 h-2 rounded-full bg-primary-500 mr-2 shadow-sm shadow-primary-500" />
                                        <Text className="text-neutral-500 text-[10px] font-black uppercase tracking-widest">
                                            Progresso Atual
                                        </Text>
                                    </View>
                                    <View className="flex-row items-baseline">
                                        <Text className="text-4xl font-black text-white">
                                            {((monthlyEarnings / monthlyGoal) * 100).toFixed(0)}%
                                        </Text>
                                        <Text className="text-neutral-500 text-xs font-bold ml-2 uppercase tracking-tighter">da sua meta</Text>
                                    </View>
                                </View>
                                <View className="items-end">
                                    <Text className="text-[10px] text-neutral-500 font-black uppercase tracking-widest mb-1">Objetivo</Text>
                                    <Text className="text-lg font-black text-primary-400">
                                        {formatCurrency(monthlyGoal)}
                                    </Text>
                                </View>
                            </View>

                            <ProgressBar
                                progress={Math.min(100, (monthlyEarnings / monthlyGoal) * 100)}
                                height={14}
                                color="#3b82f6"
                                className="bg-neutral-800 rounded-full"
                            />

                            <View className="flex-row justify-between mt-8 items-center bg-neutral-800/30 p-4 rounded-[24px] border border-neutral-800/50">
                                <View>
                                    <Text className="text-[10px] text-neutral-500 uppercase font-black tracking-widest mb-1">Conquistado</Text>
                                    <Text className="text-xl font-black text-white">
                                        {formatCurrency(monthlyEarnings)}
                                    </Text>
                                </View>
                                <View className="w-[1px] h-8 bg-neutral-800 mx-2" />
                                <View className="items-end">
                                    <Text className="text-[10px] text-neutral-500 uppercase font-black tracking-widest mb-1">Faltam</Text>
                                    <Text className="text-xl font-black text-white">
                                        {formatCurrency(missingAmount)}
                                    </Text>
                                    {missingLessons > 0 && (
                                        <Text className="text-[9px] text-neutral-400 font-bold mt-1">
                                            Aprox. {missingLessons} {missingLessons === 1 ? 'aula' : 'aulas'}
                                        </Text>
                                    )}
                                </View>
                            </View>
                        </View>
                    ) : (
                        <View className="p-8 items-center justify-center">
                            <TrendingUp size={32} color="#374151" />
                            <Text className="text-neutral-500 text-xs mt-3 text-center font-medium">
                                Defina uma meta acima para visualizar{'\n'}seu gráfico de progresso mensal.
                            </Text>
                        </View>
                    )}
                </View>

                {/* Aulas Recentes */}
                <View className="mt-2 mb-10 bg-white rounded-[40px] p-8 border border-neutral-100/50 shadow-sm shadow-neutral-200">
                    <View className="flex-row justify-between items-center mb-6">
                        <Text className="text-xl font-black text-neutral-900 tracking-tight">
                            Aulas Recentes
                        </Text>
                        <View className="bg-neutral-50 p-2 rounded-full">
                            <ChevronRight size={20} color="#9ca3af" />
                        </View>
                    </View>

                    {recentLessons.length > 0 ? (
                        <View className="-mx-2">
                            {recentLessons.map((lesson) => (
                                <LessonRow key={lesson.id} scheduling={lesson} />
                            ))}
                        </View>
                    ) : (
                        <View className="py-10 items-center">
                            <View className="w-16 h-16 bg-neutral-50 rounded-full items-center justify-center mb-4">
                                <BookOpen size={32} color="#e5e7eb" />
                            </View>
                            <Text className="text-neutral-400 text-sm text-center font-medium leading-5">
                                Nenhuma aula concluída ainda.{"\n"}
                                Suas atividades aparecerão aqui.
                            </Text>
                        </View>
                    )}
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}

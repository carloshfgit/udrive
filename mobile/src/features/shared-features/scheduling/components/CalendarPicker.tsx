/**
 * GoDrive Mobile - CalendarPicker Component
 *
 * Componente de calendário para seleção de data na marcação de aulas.
 * Segue a identidade visual do projeto com cores primárias azuis.
 */

import React, { useState, useMemo } from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { ChevronLeft, ChevronRight } from 'lucide-react-native';

interface CalendarPickerProps {
    selectedDate: Date | null;
    onDateSelect: (date: Date) => void;
    availableDaysOfWeek?: number[]; // 0=Segunda, 6=Domingo
    minDate?: Date;
    maxDate?: Date;
}

// Nomes dos dias da semana
const WEEK_DAYS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
const MONTHS = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

export function CalendarPicker({
    selectedDate,
    onDateSelect,
    availableDaysOfWeek = [0, 1, 2, 3, 4, 5, 6], // Todos os dias por padrão
    minDate = new Date(),
    maxDate,
}: CalendarPickerProps) {
    const [currentMonth, setCurrentMonth] = useState(new Date());

    // Gerar os dias do mês atual
    const calendarDays = useMemo(() => {
        const year = currentMonth.getFullYear();
        const month = currentMonth.getMonth();

        // Primeiro dia do mês
        const firstDay = new Date(year, month, 1);
        // Último dia do mês
        const lastDay = new Date(year, month + 1, 0);

        // Dia da semana do primeiro dia (0 = Domingo)
        const startDayOfWeek = firstDay.getDay();

        const days: (Date | null)[] = [];

        // Preencher dias vazios antes do início do mês
        for (let i = 0; i < startDayOfWeek; i++) {
            days.push(null);
        }

        // Adicionar todos os dias do mês
        for (let day = 1; day <= lastDay.getDate(); day++) {
            days.push(new Date(year, month, day));
        }

        return days;
    }, [currentMonth]);

    // Navegação entre meses
    const goToPreviousMonth = () => {
        setCurrentMonth(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
    };

    const goToNextMonth = () => {
        setCurrentMonth(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
    };

    // Verificar se uma data pode ser selecionada
    const isDateAvailable = (date: Date): boolean => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        // Não permitir datas passadas
        if (date < today) return false;

        // Verificar limite máximo
        if (maxDate && date > maxDate) return false;

        // Converter dia da semana do JavaScript (0=Dom) para nosso padrão (0=Seg)
        // JavaScript: 0=Sunday, 1=Monday, ... 6=Saturday
        // Backend:    0=Monday, 1=Tuesday, ... 6=Sunday
        const jsDay = date.getDay(); // 0-6 (Dom-Sab)
        const backendDay = jsDay === 0 ? 6 : jsDay - 1; // Converte para 0-6 (Seg-Dom)

        return availableDaysOfWeek.includes(backendDay);
    };

    // Verificar se uma data está selecionada
    const isDateSelected = (date: Date): boolean => {
        if (!selectedDate) return false;
        return (
            date.getDate() === selectedDate.getDate() &&
            date.getMonth() === selectedDate.getMonth() &&
            date.getFullYear() === selectedDate.getFullYear()
        );
    };

    // Verificar se é o dia atual
    const isToday = (date: Date): boolean => {
        const today = new Date();
        return (
            date.getDate() === today.getDate() &&
            date.getMonth() === today.getMonth() &&
            date.getFullYear() === today.getFullYear()
        );
    };

    // Verificar se pode navegar para mês anterior
    const canGoToPrevious = useMemo(() => {
        const today = new Date();
        const firstOfCurrentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1);
        const firstOfToday = new Date(today.getFullYear(), today.getMonth(), 1);
        return firstOfCurrentMonth > firstOfToday;
    }, [currentMonth]);

    return (
        <View className="bg-white rounded-2xl border border-neutral-100 p-2">
            {/* Header com navegação */}
            <View className="flex-row items-center justify-between mb-2">
                <TouchableOpacity
                    onPress={goToPreviousMonth}
                    disabled={!canGoToPrevious}
                    className={`w-10 h-10 items-center justify-center rounded-full ${canGoToPrevious ? 'bg-neutral-100 active:bg-neutral-200' : 'opacity-30'
                        }`}
                    accessibilityLabel="Mês anterior"
                >
                    <ChevronLeft size={20} color="#6B7280" />
                </TouchableOpacity>

                <Text className="text-lg font-semibold text-gray-900">
                    {MONTHS[currentMonth.getMonth()]} {currentMonth.getFullYear()}
                </Text>

                <TouchableOpacity
                    onPress={goToNextMonth}
                    className="w-10 h-10 items-center justify-center rounded-full bg-neutral-100 active:bg-neutral-200"
                    accessibilityLabel="Próximo mês"
                >
                    <ChevronRight size={20} color="#6B7280" />
                </TouchableOpacity>
            </View>

            {/* Dias da semana */}
            <View className="flex-row">
                {WEEK_DAYS.map((day) => (
                    <View key={day} className="flex-1 items-center py-0.5">
                        <Text className="text-xs font-medium text-gray-500">{day}</Text>
                    </View>
                ))}
            </View>

            {/* Grid de dias */}
            <View className="flex-row flex-wrap">
                {calendarDays.map((date, index) => {
                    if (!date) {
                        return <View key={`empty-${index}`} className="w-[14.28%] aspect-square" />;
                    }

                    const available = isDateAvailable(date);
                    const selected = isDateSelected(date);
                    const today = isToday(date);

                    return (
                        <TouchableOpacity
                            key={date.toISOString()}
                            disabled={!available}
                            onPress={() => onDateSelect(date)}
                            className={`w-[14.28%] aspect-square items-center justify-center rounded-full ${selected
                                ? 'bg-primary-600'
                                : available
                                    ? 'active:bg-primary-50'
                                    : ''
                                }`}
                            accessibilityLabel={`${date.getDate()} de ${MONTHS[date.getMonth()]}`}
                        >
                            <Text
                                className={`text-sm font-medium ${selected
                                    ? 'text-white'
                                    : available
                                        ? today
                                            ? 'text-primary-600'
                                            : 'text-gray-900'
                                        : 'text-gray-300'
                                    }`}
                            >
                                {date.getDate()}
                            </Text>
                            {today && !selected && (
                                <View className="absolute bottom-1 w-1 h-1 rounded-full bg-primary-600" />
                            )}
                        </TouchableOpacity>
                    );
                })}
            </View>
        </View>
    );
}

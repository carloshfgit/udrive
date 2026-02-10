import React, { useState, useCallback, useEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    TouchableOpacity,
    SafeAreaView,
    StatusBar,
    ActivityIndicator,
    RefreshControl,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SearchBar, TabSegment, EmptyState, LoadingState } from '../../../../shared/components';
import { InstructorCard } from '../components/InstructorCard';
import { FilterModal } from '../components/FilterModal';
import { MapView } from '../components/MapView';
import {
    useInstructorSearch,
    useUserLocation,
    useSearchFilters,
    SearchFilters,
} from '../hooks/useInstructorSearch';
import { Instructor } from '../api/searchApi';
import { SearchStackParamList } from '../navigation/SearchStackNavigator';

// Opções do TabSegment
const VIEW_OPTIONS = [
    { value: 'list', label: '≡ Lista' },
    { value: 'map', label: '🗺 Mapa' },
];

// Chips de filtro
const FILTER_CHIPS = [
    { key: 'category', label: 'Categoria', icon: '▼' },
    { key: 'biological_sex', label: 'Gênero', icon: '▼' },
];

// Tipo de navegação
type SearchScreenNavigationProp = NativeStackNavigationProp<SearchStackParamList, 'InstructorSearch'>;

/**
 * Tela principal de busca de instrutores.
 */
export function InstructorSearchScreen() {
    const navigation = useNavigation<SearchScreenNavigationProp>();

    // Estado de view (lista ou mapa)
    const [viewMode, setViewMode] = useState<string>('list');

    // Estado de busca por texto
    const [searchText, setSearchText] = useState('');

    // Debounce do texto de busca (400ms)
    const [debouncedSearch, setDebouncedSearch] = useState('');
    useEffect(() => {
        const timer = setTimeout(() => setDebouncedSearch(searchText), 400);
        return () => clearTimeout(timer);
    }, [searchText]);

    // Estado do modal de filtros
    const [filterModalVisible, setFilterModalVisible] = useState(false);
    const [activeFilterChip, setActiveFilterChip] = useState<string | null>(null);

    // Hooks
    const { location, isLoading: locationLoading, error: locationError } = useUserLocation();
    const { filters, setFilters, hasActiveFilters } = useSearchFilters();
    const {
        instructors,
        isLoading,
        isError,
        error,
        refetch,
        totalCount,
    } = useInstructorSearch(location, filters, debouncedSearch);

    // O backend já filtra por nome e cidade via search_query.
    // Nenhum filtro local adicional necessário.

    // Handlers
    const handleViewProfile = useCallback((instructorId: string) => {
        navigation.navigate('InstructorProfile', { instructorId });
    }, [navigation]);

    const handleFilterChipPress = useCallback((chipKey: string) => {
        setActiveFilterChip(chipKey);
        setFilterModalVisible(true);
    }, []);

    const handleApplyFilters = useCallback((newFilters: SearchFilters) => {
        setFilters(newFilters);
        setFilterModalVisible(false);
    }, [setFilters]);

    const renderInstructorCard = useCallback(
        ({ item }: { item: Instructor }) => (
            <InstructorCard instructor={item} onViewProfile={handleViewProfile} />
        ),
        [handleViewProfile]
    );

    const keyExtractor = useCallback((item: Instructor) => item.id, []);

    // Renderizar header com busca e filtros
    const renderHeader = () => (
        <>
            {/* SearchBar */}
            <View className="px-4 py-2">
                <SearchBar
                    value={searchText}
                    onChangeText={setSearchText}
                    placeholder="Buscar por nome ou cidade..."
                />
            </View>

            {/* Filter Chips */}
            <View className="flex-row px-4 py-2 gap-2">
                {FILTER_CHIPS.map((chip, index) => {
                    const isActive = chip.key === 'category'
                        ? !!filters.category
                        : chip.key === 'biological_sex'
                            ? !!filters.biological_sex
                            : false;
                    return (
                        <TouchableOpacity
                            key={chip.key}
                            onPress={() => handleFilterChipPress(chip.key)}
                            className={`flex-row items-center px-4 py-2 rounded-full ${isActive
                                ? 'bg-primary-500'
                                : 'bg-white border border-neutral-200'
                                }`}
                        >
                            <Text
                                className={`text-sm font-medium ${isActive ? 'text-white' : 'text-neutral-900'
                                    }`}
                            >
                                {chip.label}
                            </Text>
                            <Text
                                className={`ml-1.5 text-xs ${isActive ? 'text-white' : 'text-neutral-400'
                                    }`}
                            >
                                {chip.icon}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </View>

            {/* TabSegment */}
            <View className="px-4 py-3">
                <TabSegment
                    options={VIEW_OPTIONS}
                    value={viewMode}
                    onChange={setViewMode}
                />
            </View>
        </>
    );

    // Renderizar estado de erro de localização
    if (locationError) {
        return (
            <SafeAreaView className="flex-1 bg-neutral-50">
                <StatusBar barStyle="dark-content" />
                <Header />
                <View className="flex-1 items-center justify-center p-8">
                    <Text className="text-4xl mb-4">📍</Text>
                    <Text className="text-neutral-900 text-lg font-semibold text-center">
                        Localização necessária
                    </Text>
                    <Text className="text-neutral-500 text-sm text-center mt-2 mb-6">
                        Precisamos da sua localização para encontrar instrutores próximos.
                    </Text>
                    <TouchableOpacity
                        onPress={() => { }}
                        className="bg-primary-500 px-6 py-3 rounded-xl"
                    >
                        <Text className="text-white font-semibold">Permitir localização</Text>
                    </TouchableOpacity>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView className="flex-1 bg-neutral-50">
            <StatusBar barStyle="dark-content" />

            {/* Header */}
            <Header />

            {/* Conteúdo principal */}
            {viewMode === 'list' ? (
                <FlatList
                    data={instructors}
                    renderItem={renderInstructorCard}
                    keyExtractor={keyExtractor}
                    ListHeaderComponent={renderHeader()}
                    ListEmptyComponent={
                        isLoading || locationLoading ? (
                            <>
                                <LoadingState.Card />
                                <LoadingState.Card />
                                <LoadingState.Card />
                            </>
                        ) : isError ? (
                            <View className="p-8 items-center">
                                <Text className="text-red-500 text-center mb-4">
                                    Erro ao buscar instrutores
                                </Text>
                                <TouchableOpacity
                                    onPress={() => refetch()}
                                    className="bg-primary-500 px-6 py-3 rounded-xl"
                                >
                                    <Text className="text-white font-semibold">Tentar novamente</Text>
                                </TouchableOpacity>
                            </View>
                        ) : (
                            <EmptyState
                                title="Nenhum instrutor encontrado"
                                message="Tente ajustar os filtros ou ampliar o raio de busca."
                                icon={<Text className="text-2xl">🔍</Text>}
                            />
                        )
                    }
                    contentContainerStyle={{ paddingBottom: 100 }}
                    refreshControl={
                        <RefreshControl
                            refreshing={isLoading}
                            onRefresh={refetch}
                            tintColor="#2563EB"
                        />
                    }
                    showsVerticalScrollIndicator={false}
                />
            ) : (
                <View className="flex-1">
                    {renderHeader()}
                    <MapView className="flex-1" />
                </View>
            )}

            {/* Modal de filtros */}
            <FilterModal
                visible={filterModalVisible}
                onClose={() => setFilterModalVisible(false)}
                filters={filters}
                onApply={handleApplyFilters}
            />
        </SafeAreaView>
    );
}

/**
 * Header da tela de busca.
 */
function Header() {
    return (
        <View className="flex-row items-center justify-between px-4 py-3 bg-white border-b border-neutral-100">
            {/* Botão Voltar */}
            <TouchableOpacity className="w-10 h-10 items-center justify-center">
                <Text className="text-xl">‹</Text>
            </TouchableOpacity>

            {/* Título */}
            <Text className="text-lg font-bold text-neutral-900">
                Busca de Instrutores
            </Text>

            {/* Botão Notificações */}
            <TouchableOpacity className="w-10 h-10 items-center justify-center">
                <Text className="text-xl">🔔</Text>
            </TouchableOpacity>
        </View>
    );
}

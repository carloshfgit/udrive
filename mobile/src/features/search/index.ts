/**
 * GoDrive Mobile - Search Feature
 *
 * Exports centralizados da feature de busca de instrutores.
 */

// Screens
export { InstructorSearchScreen } from './screens/InstructorSearchScreen';

// Components
export { InstructorCard } from './components/InstructorCard';
export { FilterModal } from './components/FilterModal';
export { MapView } from './components/MapView';

// Hooks
export {
    useInstructorSearch,
    useUserLocation,
    useSearchFilters,
} from './hooks/useInstructorSearch';
export type { SearchFilters, UserLocation } from './hooks/useInstructorSearch';

// API
export {
    searchInstructors,
    getInstructorById,
} from './api/searchApi';
export type {
    Instructor,
    SearchInstructorsParams,
    SearchInstructorsResponse,
} from './api/searchApi';

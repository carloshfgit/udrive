export type SchedulingStatus = 
  | "pending" 
  | "confirmed" 
  | "cancelled" 
  | "completed" 
  | "reschedule_requested" 
  | "disputed";

export interface Scheduling {
  id: string;
  student_id: string;
  instructor_id: string;
  scheduled_datetime: string;
  status: SchedulingStatus;
  price: number;
  lesson_category?: string;
  student_name?: string;
  instructor_name?: string;
  payment_status?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SchedulingFilters {
  status?: SchedulingStatus;
  student_id?: string;
  instructor_id?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  limit?: number;
}

export interface SchedulingListResponse {
  schedulings: Scheduling[];
  total_count: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

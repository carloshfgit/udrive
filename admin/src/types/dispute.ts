export enum DisputeReason {
    NO_SHOW = "no_show",
    VEHICLE_PROBLEM = "vehicle_problem",
    OTHER = "other",
}

export enum DisputeStatus {
    OPEN = "open",
    UNDER_REVIEW = "under_review",
    RESOLVED = "resolved",
}

export enum DisputeResolution {
    FAVOR_INSTRUCTOR = "favor_instructor",
    FAVOR_STUDENT = "favor_student",
    RESCHEDULED = "rescheduled",
}

export interface Dispute {
    id: string;
    scheduling_id: string;
    opened_by: string;
    reason: DisputeReason | string;
    description: string;
    contact_phone: string;
    contact_email: string;
    status: DisputeStatus | string;
    resolution?: DisputeResolution | string | null;
    resolution_notes?: string | null;
    refund_type?: "full" | "partial" | null;
    resolved_by?: string | null;
    resolved_at?: string | null;
    created_at: string;
    updated_at: string;

    // Enriched data from backend (if available)
    student_name?: string;
    instructor_name?: string;
    scheduled_datetime?: string;
    price?: number;
}

export interface DisputePayment {
    id: string;
    scheduling_id: string;
    amount: number;
    status: string;
    mp_refund_id?: string | null;
    refund_amount?: number | null;
    refunded_at?: string | null;
    scheduled_datetime?: string | null;
}

export interface AdminDisputeFilters {
    status?: string | "all";
    page: number;
    size: number;
}

export interface ResolveDisputeData {
    resolution: string;
    resolution_notes: string;
    refund_type?: string | null;
    new_datetime?: string | null;
    payment_ids_to_refund?: string[];
}

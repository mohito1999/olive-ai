export type Call = {
    id: string;
    organization_id: string;
    campaign_id: string;
    customer_id: string;
    type: string;
    from_number: string;
    to_number: string;
    status: string;
    retry_count: number;
    start_time: Date | null;
    end_time: Date | null;
    duration: number | null;
    recording_url: string | null;
    transcript: string | null;
    actions: object | null;
};


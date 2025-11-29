import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export interface RecalibrationLog {
    id: string;
    recalibrated_at: string;
    window_start: string;
    window_end: string;
    previous_trust_index: number;
    new_trust_index: number;
    calibration_error: number;
    playbooks_adjusted: boolean;
    adjustments: any;
    trigger_reason: string;
    notes: string;
}

export function useRecalibrationLog(limit: number = 200) {
    const { data, error, isLoading } = useSWR<RecalibrationLog[]>(
        `/api/recalibration?limit=${limit}`,
        fetcher,
        {
            refreshInterval: 60000, // Refresh every minute
        }
    );

    return {
        logs: data,
        isLoading,
        isError: error,
    };
}

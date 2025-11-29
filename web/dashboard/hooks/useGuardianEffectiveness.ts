import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export interface EffectivenessRecord {
    action_id: string;
    chosen_action: string;
    severity: string;
    predicted_state: string;
    actual_state: string;
    intervention_prevented_collapse: boolean;
    effectiveness_score: number;
    projected_probability: number;
    guardian_influence: number | null;
    action_taken_at: string;
    outcome_recorded_at: string;
}

export function useGuardianEffectiveness(limit: number = 200) {
    const { data, error, isLoading } = useSWR<EffectivenessRecord[]>(
        `/api/effectiveness?limit=${limit}`,
        fetcher,
        {
            refreshInterval: 60000, // Refresh every minute
        }
    );

    return {
        records: data,
        isLoading,
        isError: error,
    };
}

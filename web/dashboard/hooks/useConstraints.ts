import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export function useConstraints() {
    const { data, error, isLoading } = useSWR('/api/governance/constraints', fetcher);

    return {
        constraints: data?.constraints,
        violations: data?.violations,
        isLoading,
        isError: error,
    };
}

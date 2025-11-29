import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export function useAmendments() {
    const { data, error, isLoading, mutate } = useSWR('/api/governance/amendments', fetcher);

    return {
        amendments: data,
        isLoading,
        isError: error,
        mutate,
    };
}

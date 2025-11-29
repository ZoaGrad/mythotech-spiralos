import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export function useConstitution() {
    const { data, error, isLoading } = useSWR('/api/governance/constitution', fetcher);

    return {
        articles: data,
        isLoading,
        isError: error,
    };
}

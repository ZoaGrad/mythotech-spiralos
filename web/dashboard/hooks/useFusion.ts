import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export function useFusion() {
    const { data, error } = useSWR("/api/fusion", fetcher);
    return { data, error };
}

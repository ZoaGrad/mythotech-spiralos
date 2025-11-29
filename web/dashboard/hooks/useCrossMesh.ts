"use client";

import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export function useCrossMesh() {
    const { data, error, isLoading } = useSWR("/api/cross-mesh", fetcher, {
        refreshInterval: 5000
    });

    return {
        data,
        error,
        loading: isLoading
    };
}

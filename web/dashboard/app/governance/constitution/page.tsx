'use client';

import { useConstitution } from '@/hooks/useConstitution';

export default function ConstitutionPage() {
    const { articles, isLoading, isError } = useConstitution();

    if (isLoading) return <div className="p-8 text-zinc-400">Loading Constitution...</div>;
    if (isError) return <div className="p-8 text-red-400">Failed to load Constitution.</div>;

    return (
        <div className="p-8 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-2 text-zinc-100">Core Constitution</h1>
            <p className="text-zinc-400 mb-8">The fundamental laws binding the Guardian.</p>

            <div className="space-y-6">
                {articles?.map((article: any) => (
                    <div key={article.id} className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-lg">
                        <div className="flex items-baseline gap-4 mb-2">
                            <span className="text-xl font-mono text-emerald-400">Article {article.article_number}</span>
                            <h2 className="text-xl font-semibold text-zinc-200">{article.title}</h2>
                        </div>
                        <p className="text-zinc-300 leading-relaxed text-lg">{article.body}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

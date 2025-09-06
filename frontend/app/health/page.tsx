import React from 'react';

async function fetchHealth() {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_PATH || ''}/api/proxy/health/secrets`, {
      // Opt out of caching to show current status
      cache: 'no-store',
    });
    if (!res.ok) {
      return { error: `Backend returned ${res.status}` } as any;
    }
    return res.json();
  } catch (e: any) {
    return { error: e?.message || 'Failed to fetch' } as any;
  }
}

export default async function HealthPage() {
  const data = await fetchHealth();
  const required = data?.required || {};
  const optional = data?.optional || {};
  const cache = data?.cache || {};
  const error = data?.error;

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">System Health</h1>
      {error ? (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-red-700">
          Failed to fetch health status: {error}
        </div>
      ) : (
        <div className="space-y-6">
          <section>
            <h2 className="text-xl font-medium mb-2">Required Secrets</h2>
            <ul className="space-y-1">
              {Object.entries(required).map(([k, v]) => (
                <li key={k} className="flex items-center gap-2">
                  <span className={`inline-block h-2 w-2 rounded-full ${v ? 'bg-green-500' : 'bg-red-500'}`} />
                  <code className="text-sm">{k}</code>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-medium mb-2">Optional Secrets</h2>
            <ul className="space-y-1">
              {Object.entries(optional).map(([k, v]) => (
                <li key={k} className="flex items-center gap-2">
                  <span className={`inline-block h-2 w-2 rounded-full ${v ? 'bg-green-500' : 'bg-yellow-500'}`} />
                  <code className="text-sm">{k}</code>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-medium mb-2">Cache</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="rounded border p-3">
                <div className="font-medium mb-1">Connected</div>
                <div>{String(cache?.connected)}</div>
              </div>
              <div className="rounded border p-3">
                <div className="font-medium mb-1">Host</div>
                <div>{cache?.host || '-'}</div>
              </div>
              <div className="rounded border p-3">
                <div className="font-medium mb-1">Total Keys</div>
                <div>{cache?.total_keys ?? '-'}</div>
              </div>
              <div className="rounded border p-3">
                <div className="font-medium mb-1">Hit Rate</div>
                <div>{cache?.hit_rate != null ? `${cache.hit_rate}%` : '-'}</div>
              </div>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}

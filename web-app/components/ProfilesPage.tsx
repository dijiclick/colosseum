/* eslint-disable @next/next/no-img-element */
"use client";

import { useState } from "react";
import { useProfilesQuery } from "./useProfilesQuery";
import type { ProfilesFilter } from "./types";

const initialFilters: ProfilesFilter = {
  search: "",
  location: "",
  language: "",
  role: "",
  topic: "",
  isUniversityStudent: ""
};

export default function ProfilesPage() {
  const [filters, setFilters] = useState<ProfilesFilter>(initialFilters);
  const [page, setPage] = useState(0);
  const { data, loading, error, total } = useProfilesQuery(filters, page);

  const totalPages = total ? Math.ceil(total / 24) : 1;

  function handleChange<K extends keyof ProfilesFilter>(
    key: K,
    value: ProfilesFilter[K]
  ) {
    setPage(0);
    setFilters((prev) => ({ ...prev, [key]: value }));
  }

  function resetFilters() {
    setPage(0);
    setFilters(initialFilters);
  }

  return (
    <div className="flex w-full flex-col gap-4 md:flex-row">
      <aside className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 p-4 md:w-72">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
            Filters
          </h2>
          <button
            onClick={resetFilters}
            className="text-xs text-slate-400 underline-offset-2 hover:text-slate-200 hover:underline"
          >
            Reset
          </button>
        </div>

        <div className="space-y-4 text-sm">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Search everywhere
            </label>
            <input
              value={filters.search}
              onChange={(e) => handleChange("search", e.target.value)}
              placeholder="name, username, about..."
              className="w-full rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2 text-sm outline-none ring-emerald-500/60 focus:ring-2"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Location
            </label>
            <input
              value={filters.location}
              onChange={(e) => handleChange("location", e.target.value)}
              placeholder="e.g. Toronto"
              className="w-full rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2 text-sm outline-none ring-emerald-500/60 focus:ring-2"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Language
            </label>
            <input
              value={filters.language}
              onChange={(e) => handleChange("language", e.target.value)}
              placeholder="e.g. English"
              className="w-full rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2 text-sm outline-none ring-emerald-500/60 focus:ring-2"
            />
            <p className="mt-1 text-[11px] text-slate-500">
              Matches language tags in the array.
            </p>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Role (I am a)
            </label>
            <input
              value={filters.role}
              onChange={(e) => handleChange("role", e.target.value)}
              placeholder="e.g. Product Manager"
              className="w-full rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2 text-sm outline-none ring-emerald-500/60 focus:ring-2"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Topic (Interested in)
            </label>
            <input
              value={filters.topic}
              onChange={(e) => handleChange("topic", e.target.value)}
              placeholder="e.g. DeFi"
              className="w-full rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2 text-sm outline-none ring-emerald-500/60 focus:ring-2"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              University student
            </label>
            <select
              value={filters.isUniversityStudent}
              onChange={(e) =>
                handleChange("isUniversityStudent", e.target.value)
              }
              className="w-full rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2 text-sm outline-none ring-emerald-500/60 focus:ring-2"
            >
              <option value="">Any</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </div>

          <div className="mt-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-3 text-[11px] text-slate-300">
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-300">
              Active filters
            </div>
            <div className="flex flex-wrap gap-1">
              {Object.entries(filters)
                .filter(([, v]) => v)
                .map(([key, value]) => (
                  <span
                    key={key}
                    className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] text-emerald-200"
                  >
                    {key}: {value}
                  </span>
                ))}
              {!Object.values(filters).some(Boolean) && (
                <span className="text-slate-500">None</span>
              )}
            </div>
          </div>
        </div>
      </aside>

      <section className="flex-1 space-y-4">
        <div className="flex items-center justify-between gap-2">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Results
            </p>
            <p className="text-sm text-slate-300">
              {loading
                ? "Loading..."
                : `${total.toLocaleString()} profiles found`}
            </p>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
            Error loading profiles: {error}
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {loading &&
            Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="h-40 animate-pulse rounded-2xl bg-slate-900/60"
              />
            ))}

          {!loading && data.length === 0 && !error && (
            <div className="col-span-full rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-6 text-sm text-slate-300">
              No profiles match your filters. Try broadening your search.
            </div>
          )}

          {!loading &&
            data.map((p) => (
              <article
                key={p.id}
                className="group flex flex-col justify-between rounded-2xl border border-slate-800 bg-slate-950/60 p-4 shadow-sm shadow-black/40 transition hover:border-emerald-400/60 hover:bg-slate-900/70"
              >
                <header className="mb-3 flex items-start justify-between gap-2">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-50">
                      {p.display_name || p.username || "Unknown"}
                    </h3>
                    {p.username && (
                      <p className="text-xs text-emerald-300">{p.username}</p>
                    )}
                    {p.current_position && (
                      <p className="mt-1 text-xs text-slate-400">
                        {p.current_position}
                      </p>
                    )}
                  </div>
                  {p.location && (
                    <span className="rounded-full bg-slate-900/80 px-2 py-1 text-[11px] text-slate-300">
                      {p.location}
                    </span>
                  )}
                </header>

                {p.about && (
                  <p className="mb-2 line-clamp-3 text-xs text-slate-300">
                    {p.about}
                  </p>
                )}

                <div className="mt-2 space-y-1">
                  {p.languages && p.languages.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {p.languages.map((lang) => (
                        <span
                          key={lang}
                          className="rounded-full bg-slate-900/80 px-2 py-0.5 text-[11px] text-slate-200"
                        >
                          {lang}
                        </span>
                      ))}
                    </div>
                  )}

                  {p.i_am_a_roles && p.i_am_a_roles.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {p.i_am_a_roles.map((role) => (
                        <span
                          key={role}
                          className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] text-emerald-200"
                        >
                          {role}
                        </span>
                      ))}
                    </div>
                  )}

                  {p.interested_in_topics &&
                    p.interested_in_topics.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {p.interested_in_topics.map((topic) => (
                          <span
                            key={topic}
                            className="rounded-full bg-sky-500/10 px-2 py-0.5 text-[11px] text-sky-200"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}
                </div>

                <footer className="mt-3 flex items-center justify-between border-t border-slate-800 pt-2 text-[11px] text-slate-400">
                  <div className="flex flex-wrap gap-2">
                    {p.github_handle && (
                      <a
                        href={`https://github.com/${p.github_handle.replace(
                          "@",
                          ""
                        )}`}
                        target="_blank"
                        rel="noreferrer"
                        className="hover:text-slate-100"
                      >
                        GitHub
                      </a>
                    )}
                    {p.linkedin_handle && (
                      <a
                        href={`https://linkedin.com/in/${p.linkedin_handle.replace(
                          "@",
                          ""
                        )}`}
                        target="_blank"
                        rel="noreferrer"
                        className="hover:text-slate-100"
                      >
                        LinkedIn
                      </a>
                    )}
                    {p.twitter_handle && (
                      <a
                        href={`https://twitter.com/${p.twitter_handle.replace(
                          "@",
                          ""
                        )}`}
                        target="_blank"
                        rel="noreferrer"
                        className="hover:text-slate-100"
                      >
                        X
                      </a>
                    )}
                    {p.telegram_handle && (
                      <a
                        href={`https://t.me/${p.telegram_handle.replace(
                          "@",
                          ""
                        )}`}
                        target="_blank"
                        rel="noreferrer"
                        className="hover:text-slate-100"
                      >
                        Telegram
                      </a>
                    )}
                  </div>
                  {p.is_university_student && (
                    <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-[11px] text-amber-300">
                      Student
                    </span>
                  )}
                </footer>
              </article>
            ))}
        </div>

        {totalPages > 1 && (
          <div className="mt-4 flex items-center justify-between text-xs text-slate-300">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="rounded-full border border-slate-700 px-3 py-1 disabled:opacity-40"
            >
              Previous
            </button>
            <div>
              Page {page + 1} of {totalPages}
            </div>
            <button
              onClick={() =>
                setPage((p) => (p + 1 < totalPages ? p + 1 : p))
              }
              disabled={page + 1 >= totalPages}
              className="rounded-full border border-slate-700 px-3 py-1 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        )}
      </section>
    </div>
  );
}



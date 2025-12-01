"use client";

import { useEffect, useState, useMemo, useCallback, useRef } from "react";
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

type Profile = {
  id: number;
  user_id: number | null;
  username: string | null;
  display_name: string | null;
  description: string | null;
  location: string | null;
  languages: string[] | null;
  github_handle: string | null;
  linkedin_handle: string | null;
  twitter_handle: string | null;
  telegram_handle: string | null;
  i_am_a_roles: string[] | null;
  interested_in_topics: string[] | null;
  about: string | null;
  tags: string[] | null;
  company: string | null;
  current_position: string | null;
  is_university_student: boolean | null;
  looking_for_teammates: boolean | null;
  project_description: string | null;
  looking_for_roles: string[] | null;
  profile_url: string | null;
  avatar_url: string | null;
  account_roles: string[] | null;
  batches: string[] | null;
  source_url: string | null;
  scraped_at: string | null;
  created_at: string | null;
  updated_at: string | null;
};

type SortField = "display_name" | "username" | "location" | "company" | "current_position" | "scraped_at";
type SortOrder = "asc" | "desc";

function extractCountry(location: string | null): string {
  if (!location) return "";
  const parts = location.split(",").map((p) => p.trim());
  return parts[parts.length - 1] || "";
}

// Multi-select dropdown
function MultiSelect({ label, options, selected, onChange }: {
  label: string; options: string[]; selected: string[]; onChange: (v: string[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) { setOpen(false); setSearch(""); }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const filtered = options.filter((o) => o.toLowerCase().includes(search.toLowerCase()));
  const toggle = (o: string) => onChange(selected.includes(o) ? selected.filter((s) => s !== o) : [...selected, o]);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className={`h-6 px-1.5 sm:px-2 rounded text-[10px] sm:text-[11px] flex items-center gap-0.5 border transition-all ${
          selected.length > 0 ? "bg-sky-500/20 border-sky-500/40 text-sky-300" : "bg-zinc-800/80 border-zinc-700 text-zinc-400 hover:border-zinc-600"
        }`}
      >
        <span className="truncate max-w-[60px] sm:max-w-[80px]">
          {selected.length === 0 ? label : selected.length === 1 ? selected[0] : `${label} (${selected.length})`}
        </span>
        <svg className={`w-2.5 h-2.5 shrink-0 transition-transform ${open ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="absolute z-50 mt-1 w-48 sm:w-52 bg-zinc-900 border border-zinc-700 rounded shadow-xl left-0">
          <div className="p-1.5 border-b border-zinc-800">
            <input
              type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search..."
              className="w-full h-6 px-2 bg-zinc-800 border border-zinc-700 rounded text-[11px] text-white placeholder-zinc-500 focus:outline-none" autoFocus
            />
          </div>
          <div className="max-h-40 overflow-y-auto">
            {filtered.length === 0 ? (
              <div className="px-2 py-1.5 text-[11px] text-zinc-500">No results</div>
            ) : filtered.map((o) => (
              <button key={o} onClick={() => toggle(o)}
                className={`w-full flex items-center gap-2 px-2 py-1 text-left text-[11px] hover:bg-zinc-800 ${selected.includes(o) ? "text-sky-300 bg-sky-500/10" : "text-zinc-300"}`}>
                <span className={`w-3 h-3 rounded-sm border flex items-center justify-center ${selected.includes(o) ? "bg-sky-500 border-sky-500" : "border-zinc-600"}`}>
                  {selected.includes(o) && <svg className="w-2 h-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                </span>
                <span className="truncate">{o}</span>
              </button>
            ))}
          </div>
          {selected.length > 0 && (
            <div className="p-1 border-t border-zinc-800">
              <button onClick={() => onChange([])} className="w-full px-2 py-1 text-[11px] text-zinc-400 hover:text-white rounded hover:bg-zinc-800">Clear</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Toggle button
function Toggle({ label, value, onChange }: { label: string; value: boolean | null; onChange: (v: boolean | null) => void }) {
  return (
    <button
      onClick={() => onChange(value === null ? true : value === true ? false : null)}
      className={`h-6 px-1.5 sm:px-2 rounded text-[10px] sm:text-[11px] border transition-all whitespace-nowrap ${
        value === true ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300"
          : value === false ? "bg-rose-500/20 border-rose-500/40 text-rose-300"
          : "bg-zinc-800/80 border-zinc-700 text-zinc-400 hover:border-zinc-600"
      }`}
    >
      {label}{value !== null && <span className="ml-0.5">{value ? "✓" : "✗"}</span>}
    </button>
  );
}

// Tags display
function Tags({ items, color = "zinc", max = 2 }: { items: string[] | null; color?: string; max?: number }) {
  const [expanded, setExpanded] = useState(false);
  if (!items || items.length === 0) return <span className="text-zinc-600 text-[10px]">—</span>;

  const colors: Record<string, string> = {
    zinc: "bg-zinc-800 text-zinc-300 border-zinc-700",
    sky: "bg-sky-500/10 text-sky-300 border-sky-500/30",
    violet: "bg-violet-500/10 text-violet-300 border-violet-500/30",
    amber: "bg-amber-500/10 text-amber-300 border-amber-500/30",
    emerald: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
    rose: "bg-rose-500/10 text-rose-300 border-rose-500/30",
    pink: "bg-pink-500/10 text-pink-300 border-pink-500/30",
    cyan: "bg-cyan-500/10 text-cyan-300 border-cyan-500/30",
  };

  const shown = expanded ? items : items.slice(0, max);
  const rest = items.length - max;

  return (
    <div className="flex flex-wrap gap-0.5 items-center">
      {shown.map((t, i) => (
        <span key={i} className={`px-1 py-0.5 rounded border text-[9px] sm:text-[10px] leading-tight ${colors[color]}`} title={t}>
          {t.length > 12 ? t.slice(0, 12) + "…" : t}
        </span>
      ))}
      {!expanded && rest > 0 && (
        <button onClick={(e) => { e.stopPropagation(); setExpanded(true); }} className="px-0.5 text-[9px] text-zinc-500 hover:text-zinc-300">+{rest}</button>
      )}
      {expanded && items.length > max && (
        <button onClick={(e) => { e.stopPropagation(); setExpanded(false); }} className="px-0.5 text-[9px] text-zinc-500 hover:text-zinc-300">less</button>
      )}
    </div>
  );
}

// Social icons
function Socials({ p }: { p: Profile }) {
  return (
    <div className="flex items-center gap-0.5">
      {p.github_handle && (
        <a href={`https://github.com/${p.github_handle}`} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="p-0.5 text-zinc-600 hover:text-white" title="GitHub">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
        </a>
      )}
      {p.twitter_handle && (
        <a href={`https://twitter.com/${p.twitter_handle}`} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="p-0.5 text-zinc-600 hover:text-white" title="Twitter">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        </a>
      )}
      {p.telegram_handle && (
        <a href={`https://t.me/${p.telegram_handle}`} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="p-0.5 text-zinc-600 hover:text-white" title="Telegram">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>
        </a>
      )}
      {p.linkedin_handle && (
        <a href={`https://linkedin.com/in/${p.linkedin_handle}`} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="p-0.5 text-zinc-600 hover:text-white" title="LinkedIn">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
        </a>
      )}
      {p.profile_url && (
        <a href={p.profile_url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="p-0.5 text-zinc-600 hover:text-sky-400" title="Profile">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
        </a>
      )}
    </div>
  );
}

// Mobile card view
function MobileCard({ p, expanded, onToggle }: { p: Profile; expanded: boolean; onToggle: () => void }) {
  return (
    <div className="border-b border-zinc-800/50">
      <div onClick={onToggle} className={`p-3 ${expanded ? "bg-zinc-800/40" : "hover:bg-zinc-800/30"} cursor-pointer`}>
        {/* Row 1: Username, Position, Socials */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="min-w-0 flex-1">
            <div className="text-[11px] text-zinc-400">{p.username}</div>
            <div className="text-[12px] text-zinc-200 font-medium truncate">{p.current_position || p.i_am_a_roles?.[0] || "—"}</div>
          </div>
          <Socials p={p} />
        </div>

        {/* Row 2: Company, Location */}
        <div className="flex items-center gap-3 text-[11px] mb-2">
          <span className="text-zinc-300 truncate">{p.company || "—"}</span>
          <span className="text-zinc-500 truncate">{p.location || "—"}</span>
        </div>

        {/* Row 3: Skills */}
        <div className="mb-2">
          <Tags items={p.tags} color="emerald" max={3} />
        </div>

        {/* Row 4: Looking For, Status */}
        <div className="flex items-center justify-between gap-2">
          <Tags items={p.looking_for_roles} color="amber" max={2} />
          <div className="flex gap-1 shrink-0">
            {p.looking_for_teammates && <span className="px-1 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[9px]">Team</span>}
            {p.is_university_student && <span className="px-1 py-0.5 bg-blue-500/20 text-blue-400 rounded text-[9px]">Edu</span>}
          </div>
        </div>
      </div>

      {/* Expanded */}
      {expanded && (
        <div className="bg-zinc-900/50 px-3 py-3 space-y-3 text-[11px]">
          {p.display_name && <div><span className="text-zinc-500">Name:</span> <span className="text-zinc-300">{p.display_name}</span></div>}
          {p.about && <div><span className="text-zinc-500">About:</span> <span className="text-zinc-300">{p.about}</span></div>}
          {p.description && <div><span className="text-zinc-500">Description:</span> <span className="text-zinc-300">{p.description}</span></div>}
          {p.project_description && <div><span className="text-zinc-500">Project:</span> <span className="text-zinc-300">{p.project_description}</span></div>}

          {p.languages && p.languages.length > 0 && (
            <div><span className="text-zinc-500 block mb-1">Languages:</span><Tags items={p.languages} color="sky" max={10} /></div>
          )}
          {p.i_am_a_roles && p.i_am_a_roles.length > 0 && (
            <div><span className="text-zinc-500 block mb-1">Roles:</span><Tags items={p.i_am_a_roles} color="violet" max={10} /></div>
          )}
          {p.interested_in_topics && p.interested_in_topics.length > 0 && (
            <div><span className="text-zinc-500 block mb-1">Interests:</span><Tags items={p.interested_in_topics} color="rose" max={10} /></div>
          )}
          {p.tags && p.tags.length > 0 && (
            <div><span className="text-zinc-500 block mb-1">All Skills:</span><Tags items={p.tags} color="emerald" max={20} /></div>
          )}
          {p.looking_for_roles && p.looking_for_roles.length > 0 && (
            <div><span className="text-zinc-500 block mb-1">Looking For:</span><Tags items={p.looking_for_roles} color="amber" max={10} /></div>
          )}
          {p.account_roles && p.account_roles.length > 0 && (
            <div><span className="text-zinc-500 block mb-1">Account Roles:</span><Tags items={p.account_roles} color="pink" max={10} /></div>
          )}
          {p.batches && p.batches.length > 0 && (
            <div><span className="text-zinc-500 block mb-1">Batches:</span><Tags items={p.batches} color="cyan" max={10} /></div>
          )}

          <div className="grid grid-cols-2 gap-2 text-[10px] text-zinc-500 pt-2 border-t border-zinc-800">
            <div>ID: <span className="text-zinc-400">{p.id}</span></div>
            <div>User ID: <span className="text-zinc-400">{p.user_id}</span></div>
            {p.scraped_at && <div>Scraped: <span className="text-zinc-400">{new Date(p.scraped_at).toLocaleDateString()}</span></div>}
            {p.updated_at && <div>Updated: <span className="text-zinc-400">{new Date(p.updated_at).toLocaleDateString()}</span></div>}
          </div>
        </div>
      )}
    </div>
  );
}

// Desktop row
function DesktopRow({ p, expanded, onToggle }: { p: Profile; expanded: boolean; onToggle: () => void }) {
  return (
    <>
      <div
        onClick={onToggle}
        className={`hidden lg:grid grid-cols-[minmax(100px,1fr)_minmax(120px,1.2fr)_minmax(100px,1fr)_minmax(90px,0.9fr)_minmax(80px,0.8fr)_minmax(80px,0.8fr)_minmax(100px,1fr)_minmax(100px,1fr)_70px_50px] gap-1 px-2 py-1.5 border-b border-zinc-800/50 hover:bg-zinc-800/30 cursor-pointer items-center text-[11px] ${expanded ? "bg-zinc-800/40" : ""}`}
      >
        <div className="truncate text-zinc-400" title={p.username || ""}>{p.username || "—"}</div>
        <div className="truncate text-zinc-200" title={p.current_position || ""}>{p.current_position || p.i_am_a_roles?.[0] || "—"}</div>
        <div className="truncate text-zinc-300" title={p.company || ""}>{p.company || "—"}</div>
        <div className="truncate text-zinc-400" title={p.location || ""}>{p.location || "—"}</div>
        <Tags items={p.languages} color="sky" max={1} />
        <Tags items={p.i_am_a_roles} color="violet" max={1} />
        <Tags items={p.tags} color="emerald" max={2} />
        <Tags items={p.looking_for_roles} color="amber" max={2} />
        <div className="flex gap-0.5">
          {p.looking_for_teammates && <span className="px-1 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[9px]">Team</span>}
          {p.is_university_student && <span className="px-1 py-0.5 bg-blue-500/20 text-blue-400 rounded text-[9px]">Edu</span>}
        </div>
        <Socials p={p} />
      </div>

      {/* Expanded */}
      {expanded && (
        <div className="hidden lg:block bg-zinc-900/50 border-b border-zinc-800 px-3 py-3">
          <div className="grid grid-cols-3 gap-4 text-[11px]">
            <div className="space-y-2">
              {p.display_name && <div><span className="text-zinc-500">Name:</span> <span className="text-zinc-300">{p.display_name}</span></div>}
              {p.about && <div><span className="text-zinc-500">About:</span> <span className="text-zinc-300">{p.about}</span></div>}
              {p.description && <div><span className="text-zinc-500">Description:</span> <span className="text-zinc-300">{p.description}</span></div>}
              {p.project_description && <div><span className="text-zinc-500">Project:</span> <span className="text-zinc-300">{p.project_description}</span></div>}
            </div>
            <div className="space-y-2">
              {p.languages && p.languages.length > 0 && <div><span className="text-zinc-500 block mb-1">Languages:</span><Tags items={p.languages} color="sky" max={10} /></div>}
              {p.interested_in_topics && p.interested_in_topics.length > 0 && <div><span className="text-zinc-500 block mb-1">Interests:</span><Tags items={p.interested_in_topics} color="rose" max={10} /></div>}
              {p.tags && p.tags.length > 0 && <div><span className="text-zinc-500 block mb-1">All Skills:</span><Tags items={p.tags} color="emerald" max={20} /></div>}
            </div>
            <div className="space-y-2">
              {p.looking_for_roles && p.looking_for_roles.length > 0 && <div><span className="text-zinc-500 block mb-1">Looking For:</span><Tags items={p.looking_for_roles} color="amber" max={10} /></div>}
              {p.account_roles && p.account_roles.length > 0 && <div><span className="text-zinc-500 block mb-1">Account Roles:</span><Tags items={p.account_roles} color="pink" max={10} /></div>}
              {p.batches && p.batches.length > 0 && <div><span className="text-zinc-500 block mb-1">Batches:</span><Tags items={p.batches} color="cyan" max={10} /></div>}
              <div className="grid grid-cols-2 gap-2 text-[10px] text-zinc-500 pt-2">
                <div>ID: <span className="text-zinc-400">{p.id}</span></div>
                <div>User ID: <span className="text-zinc-400">{p.user_id}</span></div>
                {p.scraped_at && <div>Scraped: <span className="text-zinc-400">{new Date(p.scraped_at).toLocaleDateString()}</span></div>}
                {p.updated_at && <div>Updated: <span className="text-zinc-400">{new Date(p.updated_at).toLocaleDateString()}</span></div>}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default function Home() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  const [search, setSearch] = useState("");
  const [selCountries, setSelCountries] = useState<string[]>([]);
  const [selLocations, setSelLocations] = useState<string[]>([]);
  const [selLanguages, setSelLanguages] = useState<string[]>([]);
  const [selRoles, setSelRoles] = useState<string[]>([]);
  const [selTopics, setSelTopics] = useState<string[]>([]);
  const [selTags, setSelTags] = useState<string[]>([]);
  const [selCompanies, setSelCompanies] = useState<string[]>([]);
  const [selLookingFor, setSelLookingFor] = useState<string[]>([]);
  const [selAccountRoles, setSelAccountRoles] = useState<string[]>([]);
  const [selBatches, setSelBatches] = useState<string[]>([]);
  const [lookingTeam, setLookingTeam] = useState<boolean | null>(null);
  const [isStudent, setIsStudent] = useState<boolean | null>(null);
  const [hasGithub, setHasGithub] = useState<boolean | null>(null);
  const [hasTwitter, setHasTwitter] = useState<boolean | null>(null);
  const [hasTelegram, setHasTelegram] = useState<boolean | null>(null);
  const [hasLinkedin, setHasLinkedin] = useState<boolean | null>(null);

  const [sortField, setSortField] = useState<SortField>("scraped_at");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [visibleCount, setVisibleCount] = useState(100);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function fetchAll() {
      try {
        const all: Profile[] = [];
        let page = 0, hasMore = true;
        while (hasMore) {
          const { data, error } = await supabase.from("colosseum_profiles").select("*").range(page * 1000, (page + 1) * 1000 - 1).order("id", { ascending: false });
          if (error) throw error;
          if (data && data.length > 0) { all.push(...data); setLoadingProgress(all.length); page++; hasMore = data.length === 1000; }
          else hasMore = false;
        }
        setProfiles(all);
      } catch (e: unknown) { setError(e instanceof Error ? e.message : "Error"); }
      finally { setLoading(false); }
    }
    fetchAll();
  }, []);

  const options = useMemo(() => {
    const countries = new Set<string>(), locations = new Set<string>(), languages = new Set<string>(), roles = new Set<string>();
    const topics = new Set<string>(), tags = new Set<string>(), companies = new Set<string>(), lookingFor = new Set<string>();
    const accountRoles = new Set<string>(), batches = new Set<string>();
    profiles.forEach((p) => {
      const c = extractCountry(p.location); if (c) countries.add(c);
      if (p.location) locations.add(p.location);
      if (p.company) companies.add(p.company);
      p.languages?.forEach((l) => languages.add(l));
      p.i_am_a_roles?.forEach((r) => roles.add(r));
      p.interested_in_topics?.forEach((t) => topics.add(t));
      p.tags?.forEach((t) => tags.add(t));
      p.looking_for_roles?.forEach((r) => lookingFor.add(r));
      p.account_roles?.forEach((r) => accountRoles.add(r));
      p.batches?.forEach((b) => batches.add(b));
    });
    return {
      countries: [...countries].sort(), locations: [...locations].sort(), languages: [...languages].sort(),
      roles: [...roles].sort(), topics: [...topics].sort(), tags: [...tags].sort(), companies: [...companies].sort(),
      lookingFor: [...lookingFor].sort(), accountRoles: [...accountRoles].sort(), batches: [...batches].sort(),
    };
  }, [profiles]);

  const filtered = useMemo(() => {
    let result = profiles.filter((p) => {
      if (search) {
        const s = search.toLowerCase();
        const match = p.username?.toLowerCase().includes(s) || p.display_name?.toLowerCase().includes(s) || p.about?.toLowerCase().includes(s) ||
          p.company?.toLowerCase().includes(s) || p.current_position?.toLowerCase().includes(s) || p.location?.toLowerCase().includes(s) ||
          p.description?.toLowerCase().includes(s) || p.project_description?.toLowerCase().includes(s) ||
          p.tags?.some((t) => t.toLowerCase().includes(s)) || p.languages?.some((l) => l.toLowerCase().includes(s)) ||
          p.looking_for_roles?.some((r) => r.toLowerCase().includes(s)) || p.i_am_a_roles?.some((r) => r.toLowerCase().includes(s));
        if (!match) return false;
      }
      if (selCountries.length && !selCountries.includes(extractCountry(p.location))) return false;
      if (selLocations.length && !selLocations.includes(p.location || "")) return false;
      if (selLanguages.length && !p.languages?.some((l) => selLanguages.includes(l))) return false;
      if (selRoles.length && !p.i_am_a_roles?.some((r) => selRoles.includes(r))) return false;
      if (selTopics.length && !p.interested_in_topics?.some((t) => selTopics.includes(t))) return false;
      if (selTags.length && !p.tags?.some((t) => selTags.includes(t))) return false;
      if (selCompanies.length && !selCompanies.includes(p.company || "")) return false;
      if (selLookingFor.length && !p.looking_for_roles?.some((r) => selLookingFor.includes(r))) return false;
      if (selAccountRoles.length && !p.account_roles?.some((r) => selAccountRoles.includes(r))) return false;
      if (selBatches.length && !p.batches?.some((b) => selBatches.includes(b))) return false;
      if (lookingTeam !== null && p.looking_for_teammates !== lookingTeam) return false;
      if (isStudent !== null && p.is_university_student !== isStudent) return false;
      if (hasGithub !== null && !!p.github_handle !== hasGithub) return false;
      if (hasTwitter !== null && !!p.twitter_handle !== hasTwitter) return false;
      if (hasTelegram !== null && !!p.telegram_handle !== hasTelegram) return false;
      if (hasLinkedin !== null && !!p.linkedin_handle !== hasLinkedin) return false;
      return true;
    });
    result.sort((a, b) => {
      let av = "", bv = "";
      switch (sortField) {
        case "display_name": av = (a.display_name || a.username || "").toLowerCase(); bv = (b.display_name || b.username || "").toLowerCase(); break;
        case "username": av = (a.username || "").toLowerCase(); bv = (b.username || "").toLowerCase(); break;
        case "location": av = (a.location || "").toLowerCase(); bv = (b.location || "").toLowerCase(); break;
        case "company": av = (a.company || "").toLowerCase(); bv = (b.company || "").toLowerCase(); break;
        case "current_position": av = (a.current_position || "").toLowerCase(); bv = (b.current_position || "").toLowerCase(); break;
        case "scraped_at": av = a.scraped_at || ""; bv = b.scraped_at || ""; break;
      }
      if (av < bv) return sortOrder === "asc" ? -1 : 1;
      if (av > bv) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
    return result;
  }, [profiles, search, selCountries, selLocations, selLanguages, selRoles, selTopics, selTags, selCompanies, selLookingFor, selAccountRoles, selBatches, lookingTeam, isStudent, hasGithub, hasTwitter, hasTelegram, hasLinkedin, sortField, sortOrder]);

  useEffect(() => { setVisibleCount(100); }, [search, selCountries, selLocations, selLanguages, selRoles, selTopics, selTags, selCompanies, selLookingFor, selAccountRoles, selBatches, lookingTeam, isStudent, hasGithub, hasTwitter, hasTelegram, hasLinkedin]);

  const handleScroll = useCallback(() => {
    if (!listRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = listRef.current;
    if (scrollTop + clientHeight >= scrollHeight - 400) setVisibleCount((v) => Math.min(v + 50, filtered.length));
  }, [filtered.length]);

  const clearAll = () => {
    setSearch(""); setSelCountries([]); setSelLocations([]); setSelLanguages([]); setSelRoles([]);
    setSelTopics([]); setSelTags([]); setSelCompanies([]); setSelLookingFor([]); setSelAccountRoles([]);
    setSelBatches([]); setLookingTeam(null); setIsStudent(null); setHasGithub(null); setHasTwitter(null);
    setHasTelegram(null); setHasLinkedin(null);
  };

  const filterCount = selCountries.length + selLocations.length + selLanguages.length + selRoles.length + selTopics.length +
    selTags.length + selCompanies.length + selLookingFor.length + selAccountRoles.length + selBatches.length +
    (lookingTeam !== null ? 1 : 0) + (isStudent !== null ? 1 : 0) + (hasGithub !== null ? 1 : 0) +
    (hasTwitter !== null ? 1 : 0) + (hasTelegram !== null ? 1 : 0) + (hasLinkedin !== null ? 1 : 0);

  const toggleSort = (f: SortField) => { if (sortField === f) setSortOrder(sortOrder === "asc" ? "desc" : "asc"); else { setSortField(f); setSortOrder("asc"); } };
  const SortIcon = ({ f }: { f: SortField }) => sortField === f ? <svg className={`w-2.5 h-2.5 ml-0.5 ${sortOrder === "desc" ? "rotate-180" : ""}`} fill="currentColor" viewBox="0 0 20 20"><path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/></svg> : null;

  if (loading) return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
      <div className="text-center">
        <div className="w-5 h-5 border-2 border-sky-500/30 border-t-sky-500 rounded-full animate-spin mx-auto mb-2" />
        <p className="text-zinc-500 text-xs">Loading {loadingProgress.toLocaleString()} profiles...</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      <div className="bg-red-500/10 border border-red-500/20 rounded p-3 text-red-400 text-xs">{error}</div>
    </div>
  );

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-300">
      <header className="sticky top-0 z-40 bg-zinc-950/95 backdrop-blur border-b border-zinc-800">
        {/* Top bar */}
        <div className="flex items-center gap-2 px-2 sm:px-3 py-1.5 border-b border-zinc-800/50">
          <span className="text-xs font-semibold text-white">Colosseum</span>
          <span className="text-zinc-600 hidden sm:inline">|</span>
          <span className="text-[10px] sm:text-[11px] text-zinc-400">{filtered.length.toLocaleString()} / {profiles.length.toLocaleString()}</span>

          <div className="relative flex-1 max-w-[140px] sm:max-w-[200px] ml-1 sm:ml-2">
            <svg className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search..."
              className="w-full h-6 pl-7 pr-2 bg-zinc-800 border border-zinc-700 rounded text-[11px] text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-600" />
          </div>

          {/* Mobile filter toggle */}
          <button onClick={() => setShowFilters(!showFilters)} className="lg:hidden p-1.5 text-zinc-400 hover:text-white">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            {filterCount > 0 && <span className="absolute -top-1 -right-1 w-4 h-4 bg-sky-500 text-white text-[9px] rounded-full flex items-center justify-center">{filterCount}</span>}
          </button>

          {filterCount > 0 && <button onClick={clearAll} className="text-[10px] sm:text-[11px] text-zinc-400 hover:text-white ml-auto">Clear ({filterCount})</button>}
        </div>

        {/* Filters - Desktop always visible, Mobile toggle */}
        <div className={`${showFilters ? "block" : "hidden"} lg:block`}>
          <div className="flex items-center gap-1 px-2 sm:px-3 py-1.5 overflow-x-auto flex-wrap">
            <MultiSelect label="Country" options={options.countries} selected={selCountries} onChange={setSelCountries} />
            <MultiSelect label="Location" options={options.locations} selected={selLocations} onChange={setSelLocations} />
            <MultiSelect label="Language" options={options.languages} selected={selLanguages} onChange={setSelLanguages} />
            <MultiSelect label="Role" options={options.roles} selected={selRoles} onChange={setSelRoles} />
            <MultiSelect label="Interest" options={options.topics} selected={selTopics} onChange={setSelTopics} />
            <MultiSelect label="Skills" options={options.tags} selected={selTags} onChange={setSelTags} />
            <MultiSelect label="Company" options={options.companies} selected={selCompanies} onChange={setSelCompanies} />
            <MultiSelect label="Looking For" options={options.lookingFor} selected={selLookingFor} onChange={setSelLookingFor} />
            <MultiSelect label="Acct Role" options={options.accountRoles} selected={selAccountRoles} onChange={setSelAccountRoles} />
            <MultiSelect label="Batch" options={options.batches} selected={selBatches} onChange={setSelBatches} />
          </div>
          <div className="flex items-center gap-1 px-2 sm:px-3 py-1.5 border-t border-zinc-800/50 flex-wrap">
            <Toggle label="Team" value={lookingTeam} onChange={setLookingTeam} />
            <Toggle label="Student" value={isStudent} onChange={setIsStudent} />
            <span className="w-px h-4 bg-zinc-700 mx-0.5" />
            <Toggle label="GitHub" value={hasGithub} onChange={setHasGithub} />
            <Toggle label="Twitter" value={hasTwitter} onChange={setHasTwitter} />
            <Toggle label="Telegram" value={hasTelegram} onChange={setHasTelegram} />
            <Toggle label="LinkedIn" value={hasLinkedin} onChange={setHasLinkedin} />
          </div>
        </div>

        {/* Desktop headers */}
        <div className="hidden lg:grid grid-cols-[minmax(100px,1fr)_minmax(120px,1.2fr)_minmax(100px,1fr)_minmax(90px,0.9fr)_minmax(80px,0.8fr)_minmax(80px,0.8fr)_minmax(100px,1fr)_minmax(100px,1fr)_70px_50px] gap-1 px-2 py-1 bg-zinc-900/50 border-t border-zinc-800 text-[10px] font-medium text-zinc-500 uppercase">
          <button onClick={() => toggleSort("username")} className="flex items-center hover:text-zinc-300 text-left">Username<SortIcon f="username" /></button>
          <button onClick={() => toggleSort("current_position")} className="flex items-center hover:text-zinc-300 text-left">Position<SortIcon f="current_position" /></button>
          <button onClick={() => toggleSort("company")} className="flex items-center hover:text-zinc-300 text-left">Company<SortIcon f="company" /></button>
          <button onClick={() => toggleSort("location")} className="flex items-center hover:text-zinc-300 text-left">Location<SortIcon f="location" /></button>
          <div>Lang</div>
          <div>Roles</div>
          <div>Skills</div>
          <div>Looking For</div>
          <div>Status</div>
          <div className="text-right">Links</div>
        </div>
      </header>

      {/* List */}
      <div ref={listRef} onScroll={handleScroll} className="h-[calc(100vh-130px)] lg:h-[calc(100vh-155px)] overflow-y-auto">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-zinc-500 text-xs">
            <p>No profiles found</p>
            {filterCount > 0 && <button onClick={clearAll} className="mt-2 underline hover:text-white">Clear filters</button>}
          </div>
        ) : (
          <>
            {filtered.slice(0, visibleCount).map((p) => (
              <div key={p.id}>
                {/* Mobile */}
                <div className="lg:hidden">
                  <MobileCard p={p} expanded={expandedId === p.id} onToggle={() => setExpandedId(expandedId === p.id ? null : p.id)} />
                </div>
                {/* Desktop */}
                <DesktopRow p={p} expanded={expandedId === p.id} onToggle={() => setExpandedId(expandedId === p.id ? null : p.id)} />
              </div>
            ))}
            {visibleCount < filtered.length && (
              <div className="flex justify-center py-3">
                <div className="w-4 h-4 border-2 border-sky-500/30 border-t-sky-500 rounded-full animate-spin" />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

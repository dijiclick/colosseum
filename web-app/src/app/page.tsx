"use client";

import { useEffect, useState, useMemo, useCallback, useRef } from "react";
import { createClient, SupabaseClient } from "@supabase/supabase-js";

let supabase: SupabaseClient | null = null;
function getSupabase() {
  if (!supabase) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    if (url && key) supabase = createClient(url, key);
  }
  return supabase;
}

type Profile = {
  id: number; user_id: number | null; username: string | null; display_name: string | null;
  description: string | null; location: string | null; languages: string[] | null;
  github_handle: string | null; linkedin_handle: string | null; twitter_handle: string | null;
  telegram_handle: string | null; i_am_a_roles: string[] | null; interested_in_topics: string[] | null;
  about: string | null; tags: string[] | null; company: string | null; current_position: string | null;
  is_university_student: boolean | null; looking_for_teammates: boolean | null;
  project_description: string | null; looking_for_roles: string[] | null; profile_url: string | null;
  avatar_url: string | null; account_roles: string[] | null; batches: string[] | null;
  source_url: string | null; scraped_at: string | null; created_at: string | null; updated_at: string | null;
};

type SortField = "display_name" | "username" | "location" | "company" | "current_position" | "scraped_at" | "id";
type SortOrder = "asc" | "desc";

function extractCountry(location: string | null): string {
  if (!location) return "";
  const parts = location.split(",").map((p) => p.trim());
  return parts[parts.length - 1] || "";
}

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
}

// Filter Panel
function FilterPanel({ title, options, selected, onChange, isOpen, onToggle }: {
  title: string; options: string[]; selected: string[]; onChange: (v: string[]) => void;
  isOpen: boolean; onToggle: () => void;
}) {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 150);
  const filtered = useMemo(() => options.filter((o) => o.toLowerCase().includes(debouncedSearch.toLowerCase())), [options, debouncedSearch]);
  const toggle = (o: string) => onChange(selected.includes(o) ? selected.filter((s) => s !== o) : [...selected, o]);
  const selectAll = () => onChange([...new Set([...selected, ...filtered])]);
  const clearAll = () => onChange(selected.filter(s => !filtered.includes(s)));

  return (
    <div className="border-b border-zinc-800">
      <button onClick={onToggle} className={`w-full flex items-center justify-between px-3 py-2.5 text-left text-xs font-medium hover:bg-zinc-800/50 ${selected.length > 0 ? "text-sky-400" : "text-zinc-400"}`}>
        <span>{title} {selected.length > 0 && `(${selected.length})`}</span>
        <svg className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
      </button>
      {isOpen && (
        <div className="px-3 pb-3">
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder={`Search ${title.toLowerCase()}...`}
            className="w-full h-8 px-2 mb-2 bg-zinc-800 border border-zinc-700 rounded text-xs text-white placeholder-zinc-500 focus:outline-none" />
          <div className="flex gap-2 mb-2">
            <button onClick={selectAll} className="text-[11px] text-sky-400 hover:text-sky-300">Select all</button>
            <span className="text-zinc-600">|</span>
            <button onClick={clearAll} className="text-[11px] text-zinc-400 hover:text-white">Clear</button>
          </div>
          <div className="max-h-44 overflow-y-auto space-y-0.5">
            {filtered.length === 0 ? <div className="text-xs text-zinc-500 py-2">No results</div> : filtered.map((o) => (
              <label key={o} className={`flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer hover:bg-zinc-800 ${selected.includes(o) ? "bg-sky-500/10" : ""}`}>
                <input type="checkbox" checked={selected.includes(o)} onChange={() => toggle(o)} className="w-3.5 h-3.5 rounded border-zinc-600 bg-zinc-800 text-sky-500 focus:ring-0 cursor-pointer" />
                <span className={`text-xs truncate ${selected.includes(o) ? "text-sky-300" : "text-zinc-300"}`}>{o}</span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ToggleFilter({ label, value, onChange }: { label: string; value: boolean | null; onChange: (v: boolean | null) => void }) {
  return (
    <button onClick={() => onChange(value === null ? true : value === true ? false : null)}
      className={`h-7 px-2.5 rounded text-xs border whitespace-nowrap ${value === true ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300" : value === false ? "bg-rose-500/20 border-rose-500/40 text-rose-300" : "bg-zinc-800 border-zinc-700 text-zinc-400 hover:border-zinc-600"}`}>
      {label}{value !== null && <span className="ml-1">{value ? "✓" : "✗"}</span>}
    </button>
  );
}

function Tags({ items, color = "zinc", max = 3 }: { items: string[] | null; color?: string; max?: number }) {
  const [expanded, setExpanded] = useState(false);
  if (!items || items.length === 0) return <span className="text-zinc-600 text-xs">—</span>;
  const colors: Record<string, string> = {
    zinc: "bg-zinc-700/50 text-zinc-200 border-zinc-600", sky: "bg-sky-500/15 text-sky-300 border-sky-500/40",
    violet: "bg-violet-500/15 text-violet-300 border-violet-500/40", amber: "bg-amber-500/15 text-amber-300 border-amber-500/40",
    emerald: "bg-emerald-500/15 text-emerald-300 border-emerald-500/40", rose: "bg-rose-500/15 text-rose-300 border-rose-500/40",
  };
  const shown = expanded ? items : items.slice(0, max);
  const rest = items.length - max;
  return (
    <div className="flex flex-wrap gap-1 items-center">
      {shown.map((t, i) => <span key={i} className={`px-1.5 py-0.5 rounded border text-[11px] ${colors[color]}`} title={t}>{t.length > 14 ? t.slice(0, 14) + "…" : t}</span>)}
      {!expanded && rest > 0 && <button onClick={(e) => { e.stopPropagation(); setExpanded(true); }} className="px-1 text-[11px] text-sky-400 hover:text-sky-300">+{rest}</button>}
      {expanded && items.length > max && <button onClick={(e) => { e.stopPropagation(); setExpanded(false); }} className="px-1 text-[11px] text-zinc-400 hover:text-zinc-300">less</button>}
    </div>
  );
}

function Socials({ p }: { p: Profile }) {
  const socials = [
    { handle: p.github_handle, url: `https://github.com/${p.github_handle}`, title: "GitHub", icon: <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/> },
    { handle: p.twitter_handle, url: `https://twitter.com/${p.twitter_handle}`, title: "X", icon: <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/> },
    { handle: p.telegram_handle, url: `https://t.me/${p.telegram_handle}`, title: "TG", icon: <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/> },
    { handle: p.linkedin_handle, url: `https://linkedin.com/in/${p.linkedin_handle}`, title: "LI", icon: <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/> },
  ].filter(s => s.handle);
  return (
    <div className="flex items-center gap-1 flex-wrap">
      {socials.map((s, i) => <a key={i} href={s.url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="p-1 text-zinc-500 hover:text-white rounded hover:bg-zinc-700/50" title={s.title}><svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">{s.icon}</svg></a>)}
      {p.profile_url && <a href={p.profile_url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="p-1 text-zinc-500 hover:text-sky-400 rounded hover:bg-zinc-700/50" title="Profile"><svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg></a>}
    </div>
  );
}

function ProfileRow({ p, expanded, onToggle }: { p: Profile; expanded: boolean; onToggle: () => void }) {
  return (
    <>
      <div onClick={onToggle} className={`grid grid-cols-[140px_160px_140px_160px_90px_100px_180px_180px_70px_80px] gap-2 px-3 py-2 border-b border-zinc-800/50 hover:bg-zinc-800/30 cursor-pointer items-center text-xs ${expanded ? "bg-zinc-800/40" : ""}`}>
        <div className="truncate text-zinc-400 font-medium">{p.username || "—"}</div>
        <div className="truncate text-zinc-200">{p.current_position || p.i_am_a_roles?.[0] || "—"}</div>
        <div className="truncate text-zinc-300">{p.company || "—"}</div>
        <div className="truncate text-zinc-400">{p.location || "—"}</div>
        <Tags items={p.languages} color="sky" max={1} />
        <Tags items={p.i_am_a_roles} color="violet" max={1} />
        <Tags items={p.tags} color="emerald" max={3} />
        <Tags items={p.looking_for_roles} color="amber" max={2} />
        <div className="flex gap-1 flex-wrap">
          {p.looking_for_teammates && <span className="px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px]">Team</span>}
          {p.is_university_student && <span className="px-1.5 py-0.5 bg-blue-500/20 text-blue-400 rounded text-[10px]">Edu</span>}
          {!p.looking_for_teammates && !p.is_university_student && <span className="text-zinc-600">—</span>}
        </div>
        <Socials p={p} />
      </div>
      {expanded && (
        <div className="bg-zinc-900/50 border-b border-zinc-800 px-4 py-4">
          <div className="grid grid-cols-3 gap-6 text-xs">
            <div className="space-y-3">
              {p.display_name && <div><span className="text-zinc-500">Name:</span> <span className="text-zinc-200">{p.display_name}</span></div>}
              {p.about && <div><span className="text-zinc-500">About:</span> <span className="text-zinc-300">{p.about}</span></div>}
              {p.project_description && <div><span className="text-zinc-500">Project:</span> <span className="text-zinc-300">{p.project_description}</span></div>}
            </div>
            <div className="space-y-3">
              {p.languages && p.languages.length > 0 && <div><span className="text-zinc-500 block mb-1">Languages:</span><Tags items={p.languages} color="sky" max={10} /></div>}
              {p.interested_in_topics && p.interested_in_topics.length > 0 && <div><span className="text-zinc-500 block mb-1">Interests:</span><Tags items={p.interested_in_topics} color="rose" max={10} /></div>}
              {p.tags && p.tags.length > 0 && <div><span className="text-zinc-500 block mb-1">All Skills:</span><Tags items={p.tags} color="emerald" max={20} /></div>}
            </div>
            <div className="space-y-3">
              {p.looking_for_roles && p.looking_for_roles.length > 0 && <div><span className="text-zinc-500 block mb-1">Looking For:</span><Tags items={p.looking_for_roles} color="amber" max={10} /></div>}
              <div className="text-[11px] text-zinc-500 pt-2">ID: <span className="text-zinc-400">{p.id}</span></div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function MobileCard({ p, expanded, onToggle }: { p: Profile; expanded: boolean; onToggle: () => void }) {
  return (
    <div className="border-b border-zinc-800/50">
      <div onClick={onToggle} className={`p-3 ${expanded ? "bg-zinc-800/40" : "hover:bg-zinc-800/30"} cursor-pointer`}>
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="min-w-0 flex-1">
            <div className="text-xs text-zinc-400">{p.username}</div>
            <div className="text-sm text-zinc-200 font-medium truncate">{p.current_position || p.i_am_a_roles?.[0] || "—"}</div>
          </div>
          <Socials p={p} />
        </div>
        <div className="flex items-center gap-3 text-xs mb-2">
          <span className="text-zinc-300 truncate">{p.company || "—"}</span>
          <span className="text-zinc-500 truncate">{p.location || "—"}</span>
        </div>
        <div className="mb-2"><Tags items={p.tags} color="emerald" max={4} /></div>
        <div className="flex items-center justify-between gap-2">
          <Tags items={p.looking_for_roles} color="amber" max={2} />
          <div className="flex gap-1">
            {p.looking_for_teammates && <span className="px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px]">Team</span>}
            {p.is_university_student && <span className="px-1.5 py-0.5 bg-blue-500/20 text-blue-400 rounded text-[10px]">Edu</span>}
          </div>
        </div>
      </div>
      {expanded && (
        <div className="bg-zinc-900/50 px-3 py-3 space-y-3 text-xs">
          {p.display_name && <div><span className="text-zinc-500">Name:</span> <span className="text-zinc-300">{p.display_name}</span></div>}
          {p.about && <div><span className="text-zinc-500">About:</span> <span className="text-zinc-300">{p.about}</span></div>}
          {p.tags && p.tags.length > 0 && <div><span className="text-zinc-500 block mb-1">All Skills:</span><Tags items={p.tags} color="emerald" max={20} /></div>}
        </div>
      )}
    </div>
  );
}

// Cache for filter options
let filterOptionsCache: { countries: string[]; languages: string[]; locations: string[]; roles: string[]; topics: string[]; tags: string[]; companies: string[]; lookingFor: string[] } | null = null;

export default function Home() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileSidebar, setMobileSidebar] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  const [filterOptions, setFilterOptions] = useState<typeof filterOptionsCache>({ countries: [], languages: [], locations: [], roles: [], topics: [], tags: [], companies: [], lookingFor: [] });
  const [openPanels, setOpenPanels] = useState<Record<string, boolean>>({ country: true, language: true });
  const togglePanel = (key: string) => setOpenPanels((prev) => ({ ...prev, [key]: !prev[key] }));

  const [searchInput, setSearchInput] = useState("");
  const search = useDebounce(searchInput, 300);
  const [selCountries, setSelCountries] = useState<string[]>([]);
  const [selLocations, setSelLocations] = useState<string[]>([]);
  const [selLanguages, setSelLanguages] = useState<string[]>([]);
  const [selRoles, setSelRoles] = useState<string[]>([]);
  const [selTopics, setSelTopics] = useState<string[]>([]);
  const [selTags, setSelTags] = useState<string[]>([]);
  const [selCompanies, setSelCompanies] = useState<string[]>([]);
  const [selLookingFor, setSelLookingFor] = useState<string[]>([]);
  const [lookingTeam, setLookingTeam] = useState<boolean | null>(null);
  const [isStudent, setIsStudent] = useState<boolean | null>(null);
  const [hasGithub, setHasGithub] = useState<boolean | null>(null);
  const [hasTwitter, setHasTwitter] = useState<boolean | null>(null);
  const [hasTelegram, setHasTelegram] = useState<boolean | null>(null);
  const [hasLinkedin, setHasLinkedin] = useState<boolean | null>(null);

  const [sortField, setSortField] = useState<SortField>("id");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const listRef = useRef<HTMLDivElement>(null);
  const PAGE_SIZE = 100;

  // Load filter options once (fast query for distinct values)
  useEffect(() => {
    async function loadFilterOptions() {
      if (filterOptionsCache) {
        setFilterOptions(filterOptionsCache);
        return;
      }
      const client = getSupabase();
      if (!client) return;

      try {
        // Get a sample of data to extract filter options (faster than full scan)
        const { data } = await client.from("colosseum_profiles").select("location,languages,i_am_a_roles,interested_in_topics,tags,company,looking_for_roles").limit(5000);
        
        if (data) {
          const countries = new Set<string>(), locations = new Set<string>(), languages = new Set<string>();
          const roles = new Set<string>(), topics = new Set<string>(), tags = new Set<string>();
          const companies = new Set<string>(), lookingFor = new Set<string>();

          data.forEach((p) => {
            const c = extractCountry(p.location); if (c) countries.add(c);
            if (p.location) locations.add(p.location);
            if (p.company) companies.add(p.company);
            p.languages?.forEach((l: string) => languages.add(l));
            p.i_am_a_roles?.forEach((r: string) => roles.add(r));
            p.interested_in_topics?.forEach((t: string) => topics.add(t));
            p.tags?.forEach((t: string) => tags.add(t));
            p.looking_for_roles?.forEach((r: string) => lookingFor.add(r));
          });

          filterOptionsCache = {
            countries: [...countries].sort(), locations: [...locations].sort(), languages: [...languages].sort(),
            roles: [...roles].sort(), topics: [...topics].sort(), tags: [...tags].sort(),
            companies: [...companies].sort(), lookingFor: [...lookingFor].sort(),
          };
          setFilterOptions(filterOptionsCache);
        }
      } catch (e) {
        console.error("Failed to load filter options", e);
      }
    }
    loadFilterOptions();
  }, []);

  // Build query with filters
  const buildQuery = useCallback((client: SupabaseClient, countOnly = false) => {
    let query = client.from("colosseum_profiles").select(countOnly ? "id" : "*", { count: countOnly ? "exact" : undefined });

    // Text search using ilike
    if (search) {
      query = query.or(`username.ilike.%${search}%,display_name.ilike.%${search}%,company.ilike.%${search}%,current_position.ilike.%${search}%,location.ilike.%${search}%,about.ilike.%${search}%`);
    }

    // Boolean filters
    if (lookingTeam !== null) query = query.eq("looking_for_teammates", lookingTeam);
    if (isStudent !== null) query = query.eq("is_university_student", isStudent);
    if (hasGithub === true) query = query.not("github_handle", "is", null);
    if (hasGithub === false) query = query.is("github_handle", null);
    if (hasTwitter === true) query = query.not("twitter_handle", "is", null);
    if (hasTwitter === false) query = query.is("twitter_handle", null);
    if (hasTelegram === true) query = query.not("telegram_handle", "is", null);
    if (hasTelegram === false) query = query.is("telegram_handle", null);
    if (hasLinkedin === true) query = query.not("linkedin_handle", "is", null);
    if (hasLinkedin === false) query = query.is("linkedin_handle", null);

    // Array contains filters
    if (selLanguages.length) query = query.overlaps("languages", selLanguages);
    if (selRoles.length) query = query.overlaps("i_am_a_roles", selRoles);
    if (selTopics.length) query = query.overlaps("interested_in_topics", selTopics);
    if (selTags.length) query = query.overlaps("tags", selTags);
    if (selLookingFor.length) query = query.overlaps("looking_for_roles", selLookingFor);

    // Company filter
    if (selCompanies.length) query = query.in("company", selCompanies);

    // Location filters (need to handle with ilike for country)
    if (selLocations.length) query = query.in("location", selLocations);

    return query;
  }, [search, lookingTeam, isStudent, hasGithub, hasTwitter, hasTelegram, hasLinkedin, selLanguages, selRoles, selTopics, selTags, selLookingFor, selCompanies, selLocations]);

  // Fetch profiles with pagination
  const fetchProfiles = useCallback(async (reset = false) => {
    const client = getSupabase();
    if (!client) { setError("Supabase not configured"); setLoading(false); return; }

    if (reset) {
      setLoading(true);
      setProfiles([]);
    } else {
      setLoadingMore(true);
    }

    try {
      const offset = reset ? 0 : profiles.length;
      let query = buildQuery(client);
      
      // Sorting
      query = query.order(sortField, { ascending: sortOrder === "asc" });
      
      // Pagination
      query = query.range(offset, offset + PAGE_SIZE - 1);

      const { data, error, count } = await query;
      if (error) throw error;

      // Get total count for display
      if (reset) {
        const countQuery = buildQuery(client, true);
        const { count: total } = await countQuery;
        setTotalCount(total || 0);
      }

      // Apply client-side country filter (Supabase can't filter by extracted country)
      let filteredData = data || [];
      if (selCountries.length) {
        filteredData = filteredData.filter(p => selCountries.includes(extractCountry(p.location)));
      }

      if (reset) {
        setProfiles(filteredData);
      } else {
        setProfiles(prev => [...prev, ...filteredData]);
      }
      
      setHasMore((data?.length || 0) === PAGE_SIZE);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [buildQuery, profiles.length, sortField, sortOrder, selCountries]);

  // Initial load and filter change
  useEffect(() => {
    fetchProfiles(true);
  }, [search, selCountries, selLocations, selLanguages, selRoles, selTopics, selTags, selCompanies, selLookingFor, lookingTeam, isStudent, hasGithub, hasTwitter, hasTelegram, hasLinkedin, sortField, sortOrder]);

  // Infinite scroll
  const handleScroll = useCallback(() => {
    if (!listRef.current || loadingMore || !hasMore) return;
    const { scrollTop, scrollHeight, clientHeight } = listRef.current;
    if (scrollTop + clientHeight >= scrollHeight - 500) {
      fetchProfiles(false);
    }
  }, [fetchProfiles, loadingMore, hasMore]);

  const clearAll = () => {
    setSearchInput(""); setSelCountries([]); setSelLocations([]); setSelLanguages([]); setSelRoles([]);
    setSelTopics([]); setSelTags([]); setSelCompanies([]); setSelLookingFor([]);
    setLookingTeam(null); setIsStudent(null); setHasGithub(null); setHasTwitter(null);
    setHasTelegram(null); setHasLinkedin(null);
  };

  const filterCount = selCountries.length + selLocations.length + selLanguages.length + selRoles.length + selTopics.length +
    selTags.length + selCompanies.length + selLookingFor.length + (lookingTeam !== null ? 1 : 0) + (isStudent !== null ? 1 : 0) +
    (hasGithub !== null ? 1 : 0) + (hasTwitter !== null ? 1 : 0) + (hasTelegram !== null ? 1 : 0) + (hasLinkedin !== null ? 1 : 0);

  const toggleSort = (f: SortField) => { if (sortField === f) setSortOrder(sortOrder === "asc" ? "desc" : "asc"); else { setSortField(f); setSortOrder("asc"); } };
  const SortIcon = ({ f }: { f: SortField }) => sortField === f ? <svg className={`w-3 h-3 ml-0.5 ${sortOrder === "desc" ? "rotate-180" : ""}`} fill="currentColor" viewBox="0 0 20 20"><path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/></svg> : null;

  const SidebarContent = () => (
    <div className="h-full flex flex-col bg-zinc-900">
      <div className="p-3 border-b border-zinc-800">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-white">Filters</span>
          {filterCount > 0 && <button onClick={clearAll} className="text-xs text-sky-400 hover:text-sky-300">Clear all ({filterCount})</button>}
        </div>
        <input type="text" value={searchInput} onChange={(e) => setSearchInput(e.target.value)} placeholder="Search..."
          className="w-full h-8 px-3 bg-zinc-800 border border-zinc-700 rounded text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-600" />
      </div>
      <div className="flex-1 overflow-y-auto">
        <FilterPanel title="Country" options={filterOptions?.countries || []} selected={selCountries} onChange={setSelCountries} isOpen={openPanels.country || false} onToggle={() => togglePanel("country")} />
        <FilterPanel title="Language" options={filterOptions?.languages || []} selected={selLanguages} onChange={setSelLanguages} isOpen={openPanels.language || false} onToggle={() => togglePanel("language")} />
        <FilterPanel title="Location" options={filterOptions?.locations || []} selected={selLocations} onChange={setSelLocations} isOpen={openPanels.location || false} onToggle={() => togglePanel("location")} />
        <FilterPanel title="Role" options={filterOptions?.roles || []} selected={selRoles} onChange={setSelRoles} isOpen={openPanels.role || false} onToggle={() => togglePanel("role")} />
        <FilterPanel title="Interest" options={filterOptions?.topics || []} selected={selTopics} onChange={setSelTopics} isOpen={openPanels.topic || false} onToggle={() => togglePanel("topic")} />
        <FilterPanel title="Skills" options={filterOptions?.tags || []} selected={selTags} onChange={setSelTags} isOpen={openPanels.tag || false} onToggle={() => togglePanel("tag")} />
        <FilterPanel title="Company" options={filterOptions?.companies || []} selected={selCompanies} onChange={setSelCompanies} isOpen={openPanels.company || false} onToggle={() => togglePanel("company")} />
        <FilterPanel title="Looking For" options={filterOptions?.lookingFor || []} selected={selLookingFor} onChange={setSelLookingFor} isOpen={openPanels.lookingFor || false} onToggle={() => togglePanel("lookingFor")} />
        <div className="p-3 border-t border-zinc-800">
          <div className="text-xs text-zinc-500 uppercase mb-2 font-medium">Status</div>
          <div className="flex flex-wrap gap-1.5">
            <ToggleFilter label="Team" value={lookingTeam} onChange={setLookingTeam} />
            <ToggleFilter label="Student" value={isStudent} onChange={setIsStudent} />
          </div>
          <div className="text-xs text-zinc-500 uppercase mt-4 mb-2 font-medium">Socials</div>
          <div className="flex flex-wrap gap-1.5">
            <ToggleFilter label="GitHub" value={hasGithub} onChange={setHasGithub} />
            <ToggleFilter label="Twitter" value={hasTwitter} onChange={setHasTwitter} />
            <ToggleFilter label="Telegram" value={hasTelegram} onChange={setHasTelegram} />
            <ToggleFilter label="LinkedIn" value={hasLinkedin} onChange={setHasLinkedin} />
          </div>
        </div>
      </div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      <div className="bg-red-500/10 border border-red-500/20 rounded p-4 text-red-400 text-sm">{error}</div>
    </div>
  );

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-300 flex">
      <div className={`hidden lg:block ${sidebarOpen ? "w-72" : "w-0"} transition-all duration-300 overflow-hidden border-r border-zinc-800 shrink-0`}>
        <SidebarContent />
      </div>
      {mobileSidebar && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/60" onClick={() => setMobileSidebar(false)} />
          <div className="relative w-80 max-w-[85vw]"><SidebarContent /></div>
        </div>
      )}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-30 bg-zinc-950/95 backdrop-blur border-b border-zinc-800">
          <div className="flex items-center gap-3 px-3 py-2.5">
            <button onClick={() => { if (window.innerWidth >= 1024) setSidebarOpen(!sidebarOpen); else setMobileSidebar(true); }} className="p-1.5 text-zinc-400 hover:text-white rounded hover:bg-zinc-800">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
            <span className="text-base font-semibold text-white">Colosseum</span>
            <span className="text-zinc-600 hidden sm:inline">|</span>
            <span className="text-sm text-zinc-400">
              {loading ? "Loading..." : `${profiles.length.toLocaleString()}${hasMore ? "+" : ""} / ${totalCount.toLocaleString()}`}
            </span>
            {filterCount > 0 && <span className="px-2 py-0.5 bg-sky-500/20 text-sky-400 rounded text-xs">{filterCount} filter{filterCount > 1 ? "s" : ""}</span>}
          </div>
          <div className="hidden lg:grid grid-cols-[140px_160px_140px_160px_90px_100px_180px_180px_70px_80px] gap-2 px-3 py-2 bg-zinc-900/50 border-t border-zinc-800 text-xs font-medium text-zinc-500 uppercase">
            <button onClick={() => toggleSort("username")} className="flex items-center hover:text-zinc-300 text-left">Username<SortIcon f="username" /></button>
            <button onClick={() => toggleSort("current_position")} className="flex items-center hover:text-zinc-300 text-left">Position<SortIcon f="current_position" /></button>
            <button onClick={() => toggleSort("company")} className="flex items-center hover:text-zinc-300 text-left">Company<SortIcon f="company" /></button>
            <button onClick={() => toggleSort("location")} className="flex items-center hover:text-zinc-300 text-left">Location<SortIcon f="location" /></button>
            <div>Lang</div>
            <div>Roles</div>
            <div>Skills</div>
            <div>Looking For</div>
            <div>Status</div>
            <div>Links</div>
          </div>
        </header>
        <div ref={listRef} onScroll={handleScroll} className="flex-1 overflow-y-auto overflow-x-auto">
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <div className="text-center">
                <div className="w-6 h-6 border-2 border-sky-500/30 border-t-sky-500 rounded-full animate-spin mx-auto mb-2" />
                <p className="text-zinc-400 text-sm">Loading profiles...</p>
              </div>
            </div>
          ) : profiles.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-zinc-500 text-sm">
              <p>No profiles found</p>
              {filterCount > 0 && <button onClick={clearAll} className="mt-3 text-sky-400 hover:text-sky-300 underline">Clear filters</button>}
            </div>
          ) : (
            <div className="min-w-[1200px] lg:min-w-0">
              {profiles.map((p) => (
                <div key={p.id}>
                  <div className="lg:hidden"><MobileCard p={p} expanded={expandedId === p.id} onToggle={() => setExpandedId(expandedId === p.id ? null : p.id)} /></div>
                  <div className="hidden lg:block"><ProfileRow p={p} expanded={expandedId === p.id} onToggle={() => setExpandedId(expandedId === p.id ? null : p.id)} /></div>
                </div>
              ))}
              {loadingMore && (
                <div className="flex justify-center py-4"><div className="w-5 h-5 border-2 border-sky-500/30 border-t-sky-500 rounded-full animate-spin" /></div>
              )}
              {!hasMore && profiles.length > 0 && (
                <div className="text-center py-4 text-zinc-500 text-xs">All profiles loaded</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

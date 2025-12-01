import { useEffect, useState } from "react";
import { supabase } from "../lib/supabaseClient";
import type { Profile, ProfilesFilter } from "./types";

type Result = {
  data: Profile[];
  loading: boolean;
  error: string | null;
  total: number;
};

const PAGE_SIZE = 24;

export function useProfilesQuery(filters: ProfilesFilter, page: number): Result {
  const [state, setState] = useState<Result>({
    data: [],
    loading: true,
    error: null,
    total: 0
  });

  useEffect(() => {
    let isCancelled = false;

    async function run() {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      let query = supabase
        .from("colosseum_profiles")
        .select(
          "id, username, display_name, location, languages, github_handle, linkedin_handle, twitter_handle, telegram_handle, i_am_a_roles, interested_in_topics, about, current_position, is_university_student",
          { count: "exact" }
        );

      if (filters.location) {
        query = query.ilike("location", `%${filters.location}%`);
      }

      if (filters.language) {
        query = query.contains("languages", [filters.language]);
      }

      if (filters.role) {
        query = query.contains("i_am_a_roles", [filters.role]);
      }

      if (filters.topic) {
        query = query.contains("interested_in_topics", [filters.topic]);
      }

      if (filters.isUniversityStudent === "yes") {
        query = query.eq("is_university_student", true);
      } else if (filters.isUniversityStudent === "no") {
        query = query.eq("is_university_student", false);
      }

      const search = filters.search.trim();
      if (search) {
        const s = `%${search}%`;
        query = query.or(
          [
            `username.ilike.${s}`,
            `display_name.ilike.${s}`,
            `about.ilike.${s}`,
            `current_position.ilike.${s}`,
            `location.ilike.${s}`
          ].join(",")
        );
      }

      const from = page * PAGE_SIZE;
      const to = from + PAGE_SIZE - 1;
      query = query.range(from, to).order("id", { ascending: true });

      const { data, error, count } = await query;

      if (isCancelled) return;

      if (error) {
        setState({
          data: [],
          loading: false,
          error: error.message,
          total: 0
        });
      } else {
        setState({
          data: (data ?? []) as Profile[],
          loading: false,
          error: null,
          total: count ?? 0
        });
      }
    }

    void run();

    return () => {
      isCancelled = true;
    };
  }, [filters, page]);

  return state;
}



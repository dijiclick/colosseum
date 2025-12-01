import { supabase } from "../../lib/supabaseClient";

// Always fetch fresh data from Supabase on each request (no caching)
export const dynamic = "force-dynamic";

type ProfileRow = {
  id: number;
  username: string | null;
  display_name: string | null;
  location: string | null;
  languages: string[] | null;
  i_am_a_roles: string[] | null;
  interested_in_topics: string[] | null;
  github_handle: string | null;
  twitter_handle: string | null;
  telegram_handle: string | null;
};

async function getData() {
  if (!supabase) {
    return {
      status: {
        ok: false,
        message:
          "NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY is missing in .env.local / Vercel env.",
      },
      profiles: [] as ProfileRow[],
    };
  }

  try {
    const { data, error } = await supabase
      .from("colosseum_profiles")
      .select(
        "id, username, display_name, location, languages, i_am_a_roles, interested_in_topics, github_handle, twitter_handle, telegram_handle",
      )
      .order("id", { ascending: false })
      .limit(30);

    if (error) {
      return {
        status: { ok: false, message: `Supabase error: ${error.message}` },
        profiles: [] as ProfileRow[],
      };
    }

    return {
      status: {
        ok: true,
        message: `Loaded ${data?.length ?? 0} profiles from colosseum_profiles.`,
      },
      profiles: (data ?? []) as ProfileRow[],
    };
  } catch (e: any) {
    return {
      status: { ok: false, message: `Unexpected error: ${e?.message ?? String(e)}` },
      profiles: [] as ProfileRow[],
    };
  }
}

export default async function Home() {
  const { status, profiles } = await getData();

  return (
    <main
      style={{
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        padding: "16px",
      }}
    >
      <h1 style={{ fontSize: "20px", marginBottom: "8px" }}>Colosseum Profiles (live)</h1>
      <p style={{ fontSize: "12px", marginBottom: "12px" }}>
        {status.ok ? "OK: " : "ERROR: "}
        {status.message}
      </p>

      {!profiles.length && (
        <p style={{ fontSize: "13px" }}>
          No rows returned. Either the table is empty or there was an error above.
        </p>
      )}

      {profiles.length > 0 && (
        <table
          style={{
            borderCollapse: "collapse",
            width: "100%",
            fontSize: "12px",
          }}
        >
          <thead>
            <tr>
              <th style={{ border: "1px solid #ddd", padding: "4px" }}>ID</th>
              <th style={{ border: "1px solid #ddd", padding: "4px" }}>Username</th>
              <th style={{ border: "1px solid #ddd", padding: "4px" }}>Name</th>
              <th style={{ border: "1px solid #ddd", padding: "4px" }}>Location</th>
              <th style={{ border: "1px solid #ddd", padding: "4px" }}>Languages</th>
              <th style={{ border: "1px solid #ddd", padding: "4px" }}>I am a</th>
              <th style={{ border: "1px solid #ddd", padding: "4px" }}>Interested in</th>
            </tr>
          </thead>
          <tbody>
            {profiles.map((p) => (
              <tr key={p.id}>
                <td style={{ border: "1px solid #eee", padding: "4px" }}>{p.id}</td>
                <td style={{ border: "1px solid #eee", padding: "4px" }}>{p.username}</td>
                <td style={{ border: "1px solid #eee", padding: "4px" }}>
                  {p.display_name}
                </td>
                <td style={{ border: "1px solid #eee", padding: "4px" }}>
                  {p.location}
                </td>
                <td style={{ border: "1px solid #eee", padding: "4px" }}>
                  {p.languages?.join(", ")}
                </td>
                <td style={{ border: "1px solid #eee", padding: "4px" }}>
                  {p.i_am_a_roles?.join(", ")}
                </td>
                <td style={{ border: "1px solid #eee", padding: "4px" }}>
                  {p.interested_in_topics?.join(", ")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}

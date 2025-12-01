import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Colosseum Profiles Explorer",
  description: "Filter and search Colosseum profiles stored in Supabase"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background text-slate-100 antialiased">
        <div className="flex min-h-screen flex-col">
          <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
              <div className="flex items-center gap-2">
                <span className="h-8 w-8 rounded-xl bg-gradient-to-tr from-emerald-400 to-cyan-500 shadow-lg" />
                <div>
                  <h1 className="text-lg font-semibold tracking-tight">
                    Colosseum Profiles Explorer
                  </h1>
                  <p className="text-xs text-slate-400">
                    Multi-filter and full-text search on your Supabase data
                  </p>
                </div>
              </div>
            </div>
          </header>
          <main className="mx-auto flex w-full max-w-6xl flex-1 px-4 py-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}



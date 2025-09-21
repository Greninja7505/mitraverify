"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Menu } from "lucide-react";

export default function MitraNav() {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    const isDark = typeof window !== "undefined" && localStorage.getItem("theme") === "dark";
    document.documentElement.classList.toggle("dark", isDark);
    setDark(isDark);
  }, []);
  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  const Links = () => (
    <nav className="flex flex-col md:flex-row items-start md:items-center gap-4 md:gap-6">
      <Link href="/" className="text-sm hover:underline">Home</Link>
      <Link href="/results" className="text-sm hover:underline">Results</Link>
      <Link href="/api-playground" className="text-sm hover:underline">API Playground</Link>
      <Link href="/#verify" className="text-sm hover:underline">Verify</Link>
    </nav>
  );

  return (
    <header className="sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">MV</span>
          <span>MitraVerify</span>
        </Link>
        <div className="hidden md:flex items-center gap-6">
          <Links />
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={toggle} aria-label="Toggle theme">{dark ? "Light" : "Dark"}</Button>
          <Link href="/#verify"><Button size="sm">Verify now</Button></Link>
          <div className="md:hidden">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" size="icon" aria-label="Open menu"><Menu className="h-5 w-5" /></Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-64">
                <div className="mt-8 space-y-6">
                  <Links />
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </header>
  );
}
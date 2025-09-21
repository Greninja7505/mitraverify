"use client";

import Link from "next/link";
import MitraNav from "@/components/MitraNav";
import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, CheckCircle2, XCircle, HelpCircle } from "lucide-react";

function VerdictPill({ verdict }: { verdict: "Real" | "Fake" | "Uncertain" | null }) {
  if (!verdict) return <Badge variant="secondary">Pending</Badge>;
  const map = {
    Real: { icon: <CheckCircle2 className="h-4 w-4 text-green-600" />, label: "Real", cls: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300" },
    Fake: { icon: <XCircle className="h-4 w-4 text-red-600" />, label: "Fake", cls: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300" },
    Uncertain: { icon: <HelpCircle className="h-4 w-4 text-amber-600" />, label: "Uncertain", cls: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300" },
  } as const;
  const v = map[verdict];
  return <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${v.cls}`}>{v.icon}{v.label}</span>;
}

export default function ResultsPage() {
  const [result, setResult] = useState<any | null>(null);
  useEffect(() => {
    const raw = localStorage.getItem("mitra:lastResult");
    if (raw) setResult(JSON.parse(raw));
  }, []);

  const risk = useMemo(() => {
    const c = result?.confidence ?? 0;
    return c > 66 ? "Low" : c < 34 ? "High" : "Medium";
  }, [result]);

  const highlighted = useMemo(() => {
    const txt: string = result?.text || "";
    const flagged = ["shocking", "urgent", "exclusive", "वायरल", "तुरंत"]; // toy example
    const parts = txt.split(/(\s+)/);
    return parts.map((p, i) => {
      const hit = flagged.some((w) => p.toLowerCase() === w.toLowerCase());
      return <span key={i} className={hit ? "bg-red-500/20 underline decoration-red-500/60 rounded" : ""}>{p}</span>;
    });
  }, [result]);

  return (
    <div>
      <MitraNav />
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/"><Button variant="ghost" size="sm" className="gap-2"><ArrowLeft className="h-4 w-4" /> Back</Button></Link>
            <h1 className="text-2xl font-semibold">Verification Results</h1>
          </div>
          <div className="text-sm text-muted-foreground">Historical analysis shows similar past claims</div>
        </div>

        {!result ? (
          <Card>
            <CardHeader><CardTitle>No result found</CardTitle><CardDescription>Run an analysis from the homepage first.</CardDescription></CardHeader>
            <CardContent>
              <Link href="/"><Button>Go to Home</Button></Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-3">Verdict <VerdictPill verdict={result.verdict} /></CardTitle>
                <CardDescription>Explainable AI dashboard</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid sm:grid-cols-3 gap-4">
                  <div className="rounded-md border p-4">
                    <div className="text-sm text-muted-foreground">Confidence</div>
                    <div className="flex items-end gap-3"><span className="text-3xl font-bold">{result.confidence}%</span></div>
                    <Progress value={result.confidence} className="mt-2" />
                  </div>
                  <div className="rounded-md border p-4">
                    <div className="text-sm text-muted-foreground">Risk</div>
                    <div className="mt-1"><Badge variant="outline">{risk}</Badge></div>
                  </div>
                  <div className="rounded-md border p-4">
                    <div className="text-sm text-muted-foreground">Language</div>
                    <div className="mt-1 font-medium uppercase">{(result.lang || "EN").toString()}</div>
                  </div>
                </div>

                <Separator />

                <div>
                  <div className="mb-2 text-sm font-medium">Claim text</div>
                  <div className="rounded-md border p-3 leading-relaxed">{highlighted}</div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="rounded-md border p-3">
                    <div className="mb-2 text-sm font-medium">Attention visualization</div>
                    <div className="h-40 w-full bg-gradient-to-r from-red-500/30 via-amber-500/30 to-green-500/30 rounded"></div>
                  </div>
                  <div className="rounded-md border p-3">
                    <div className="mb-2 text-sm font-medium">Decision tree</div>
                    <Accordion type="single" collapsible className="w-full">
                      <AccordionItem value="n1">
                        <AccordionTrigger>Source reliability</AccordionTrigger>
                        <AccordionContent>
                          <Accordion type="single" collapsible>
                            <AccordionItem value="n1-1">
                              <AccordionTrigger>Cross-check (AltNews, PIB)</AccordionTrigger>
                              <AccordionContent>Contradictions found → decreases credibility</AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="n1-2">
                              <AccordionTrigger>Image forensics</AccordionTrigger>
                              <AccordionContent>Reverse search shows earlier unrelated context</AccordionContent>
                            </AccordionItem>
                          </Accordion>
                        </AccordionContent>
                      </AccordionItem>
                      <AccordionItem value="n2">
                        <AccordionTrigger>Language patterns</AccordionTrigger>
                        <AccordionContent>Sensational words increase risk score</AccordionContent>
                      </AccordionItem>
                    </Accordion>
                  </div>
                </div>

                {result.imagePreview && (
                  <div className="rounded-md border p-3">
                    <div className="mb-2 text-sm font-medium">Image heatmap</div>
                    <div className="relative">
                      <img src={result.imagePreview} alt="uploaded" className="max-h-80 w-full object-contain rounded" />
                      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_60%_40%,rgba(255,0,0,.35),transparent_45%),radial-gradient(circle_at_30%_70%,rgba(255,200,0,.25),transparent_35%)]"></div>
                    </div>
                  </div>
                )}

                <div>
                  <div className="mb-2 text-sm font-medium">Evidence comparison</div>
                  <div className="grid md:grid-cols-3 gap-3">
                    {result.evidence?.map((ev: any) => (
                      <a key={ev.source} href={ev.url} target="_blank" rel="noreferrer" className="rounded-md border p-3 hover:bg-accent">
                        <div className="flex items-center justify-between text-sm"><span className="font-medium">{ev.source}</span><Badge variant="secondary">{ev.credibility}%</Badge></div>
                        <p className="text-xs text-muted-foreground mt-1">{ev.excerpt}</p>
                      </a>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="space-y-6">
              <Card>
                <CardHeader><CardTitle>Share</CardTitle><CardDescription>Copy a summary</CardDescription></CardHeader>
                <CardContent>
                  <Button className="w-full" onClick={async () => {
                    const summary = `Verdict: ${result.verdict}\nConfidence: ${result.confidence}%\nRisk: ${risk}`;
                    await navigator.clipboard.writeText(summary);
                    alert("Copied");
                  }}>Copy summary</Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Similar past claims</CardTitle><CardDescription>Historical analysis</CardDescription></CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="rounded-md border p-2">Claim about {new Date(result.ts).toLocaleDateString()} – Marked Uncertain, follow-ups requested.</div>
                  <div className="rounded-md border p-2">Related narrative identified last month – Partly False.</div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
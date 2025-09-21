"use client";

import Link from "next/link";
import MitraNav from "@/components/MitraNav";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Upload,
  Languages,
  Activity,
  ShieldCheck,
  History,
  Share2,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import {
  mitraAPI,
  VerificationResult,
  formatConfidence,
  getVerdictColor,
} from "@/lib/api";

function CircularConfidence({ value }: { value: number }) {
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;
  const color =
    value > 66
      ? "stroke-green-500"
      : value > 33
        ? "stroke-amber-500"
        : "stroke-red-500";
  return (
    <svg viewBox="0 0 100 100" className="h-24 w-24">
      <circle
        cx="50"
        cy="50"
        r={radius}
        className="stroke-muted"
        strokeWidth="8"
        fill="none"
      />
      <circle
        cx="50"
        cy="50"
        r={radius}
        className={`${color} transition-[stroke-dashoffset] duration-500 ease-out`}
        strokeWidth="8"
        fill="none"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
      />
      <text
        x="50"
        y="54"
        textAnchor="middle"
        className="fill-foreground text-sm font-semibold"
      >
        {value}%
      </text>
    </svg>
  );
}

function useAutoDetectLang(text: string) {
  return useMemo(() => {
    if (!text) return "auto" as const;
    // Basic Devanagari detection for Hindi
    const hasDevanagari = /[\u0900-\u097F]/.test(text);
    return hasDevanagari ? ("hi" as const) : ("en" as const);
  }, [text]);
}

type Evidence = {
  source: string;
  credibility: number;
  excerpt: string;
  url: string;
};

export default function HomePage() {
  const [text, setText] = useState("");
  const [lang, setLang] = useState<"auto" | "en" | "hi">("auto");
  const autodetected = useAutoDetectLang(text);
  const [dragActive, setDragActive] = useState(false);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(0);
  const [verdict, setVerdict] = useState<"Real" | "Fake" | "Uncertain" | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [apiResult, setApiResult] = useState<VerificationResult | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    // real-time lightweight analysis as user types
    const t = setTimeout(() => {
      if (!text) {
        setConfidence(0);
        setVerdict(null);
        setEvidence([]);
        return;
      }
      const sensationalWords = [
        "shocking",
        "वायरल",
        "urgent",
        "exclusive",
        "तुरंत",
        "fake",
        "scam",
        "fraud",
      ]; // simple heuristic
      const scoreBoost = sensationalWords.reduce(
        (acc, w) =>
          text.toLowerCase().includes(w.toLowerCase()) ? acc + 12 : acc,
        0
      );
      const base = Math.min(95, Math.max(5, Math.floor(text.length / 4)));
      const conf = Math.min(99, Math.max(1, base + scoreBoost));
      setConfidence(conf);
      const v: "Real" | "Fake" | "Uncertain" =
        conf > 66 ? "Real" : conf < 34 ? "Fake" : "Uncertain";
      setVerdict(v);
      const words = text.split(/\s+/).filter(Boolean).slice(0, 3);
      setEvidence([
        {
          source: "AltNews",
          credibility: 88,
          excerpt: `Analysis of claim mentioning "${words[0] ?? "claim"}"`,
          url: "https://www.altnews.in/",
        },
        {
          source: "PIB Fact Check",
          credibility: 91,
          excerpt: "Government clarification on related topic",
          url: "https://pib.gov.in/factcheck.aspx",
        },
        {
          source: "Factly",
          credibility: 82,
          excerpt: "Data-backed review of the narrative",
          url: "https://factly.in/",
        },
      ]);
    }, 280);
    return () => clearTimeout(t);
  }, [text]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    if (file.type.startsWith("image/")) {
      const url = URL.createObjectURL(file);
      setImagePreview(url);
    } else {
      // read as text for quick analysis
      const reader = new FileReader();
      reader.onload = () => setText(String(reader.result || ""));
      reader.readAsText(file);
    }
  }, []);

  const analyze = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get the uploaded file if any
      let uploadedFile: File | undefined = undefined;
      if (inputRef.current?.files?.[0]) {
        uploadedFile = inputRef.current.files[0];
      }

      // Call the real API
      const result = await mitraAPI.verifyContent(
        text || undefined,
        uploadedFile
      );

      setApiResult(result);

      // Debug logging
      console.log("API Response:", result);

      // Update UI state with API results
      const confidencePercent = Math.round((result.confidence || 0) * 100);
      setConfidence(confidencePercent);

      // Map API verdict to UI verdict with better handling
      let uiVerdict: "Real" | "Fake" | "Uncertain";
      const verdict = result.overall_verdict?.toLowerCase();

      if (verdict === "reliable" || verdict === "real") {
        uiVerdict = "Real";
      } else if (verdict === "misinformation" || verdict === "fake") {
        uiVerdict = "Fake";
      } else {
        uiVerdict = "Uncertain";
      }
      setVerdict(uiVerdict);

      // Update evidence with API results, handling potential missing data
      if (result.evidence && Array.isArray(result.evidence)) {
        setEvidence(
          result.evidence.map((ev) => ({
            source: ev.source || "Unknown Source",
            credibility: ev.credibility || 0,
            excerpt: ev.excerpt || "No excerpt available",
            url: ev.url || "#",
          }))
        );
      } else {
        // Keep existing evidence if API doesn't return any
        console.log("No evidence returned from API");
      }

      // Save to localStorage
      const resultForStorage = {
        text,
        imagePreview,
        confidence: confidencePercent,
        verdict: uiVerdict,
        lang: lang === "auto" ? autodetected : lang,
        evidence: result.evidence,
        apiResult: result,
        ts: Date.now(),
      };
      localStorage.setItem(
        "mitra:lastResult",
        JSON.stringify(resultForStorage)
      );
    } catch (err) {
      console.error("Analysis failed:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Analysis failed";
      setError(errorMessage);

      // Show more detailed error information
      const fileInInput = inputRef.current?.files?.[0];
      console.log("Error details:", {
        error: err,
        text: text?.substring(0, 100),
        hasImage: !!fileInInput,
        imageType: fileInInput?.type,
      });

      // Don't fallback to mock data, let user know there's an issue
      setConfidence(0);
      setVerdict("Uncertain");
      setEvidence([]);
    } finally {
      setLoading(false);
    }
  };

  const resetAll = () => {
    setText("");
    setImagePreview(null);
    setVerdict(null);
    setConfidence(0);
    setEvidence([]);
    setError(null);
    setApiResult(null);
  };

  const share = async () => {
    try {
      const data = { verdict, confidence };
      // @ts-ignore
      if (navigator.share) {
        // @ts-ignore
        await navigator.share({
          title: "MitraVerify Result",
          text: JSON.stringify(data),
          url: window.location.href,
        });
      } else {
        await navigator.clipboard.writeText(JSON.stringify(data));
        alert("Result copied to clipboard");
      }
    } catch (e) {
      console.error(e);
    }
  };

  const t = (en: string, hi: string) =>
    lang === "hi" || autodetected === "hi" ? hi : en;

  return (
    <div className="min-h-screen">
      <MitraNav />
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero */}
        <section className="grid md:grid-cols-2 gap-8 items-center">
          <div className="space-y-4">
            <h1 className="text-3xl sm:text-5xl font-bold">
              {t(
                "AI-powered misinformation detection",
                "एआई संचालित भ्रामक सूचना पहचान"
              )}
            </h1>
            <p className="text-muted-foreground text-lg">
              {t(
                "Verify WhatsApp forwards, posts, and claims in seconds — with transparent reasoning.",
                "व्हाट्सएप फॉरवर्ड, पोस्ट और दावे सेकंडों में सत्यापित करें — पारदर्शी तर्क के साथ।"
              )}
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="#verify">
                <Button size="lg" className="gap-2">
                  <ShieldCheck className="h-4 w-4" />{" "}
                  {t("Start verifying", "सत्यापन शुरू करें")}
                </Button>
              </Link>
              <Link href="/api-playground">
                <Button size="lg" variant="outline" className="gap-2">
                  <Activity className="h-4 w-4" /> API
                </Button>
              </Link>
            </div>
            <div className="flex gap-2 pt-2 text-sm text-muted-foreground">
              <Badge variant="secondary">WCAG AA</Badge>
              <Badge variant="secondary">Mobile-first</Badge>
              <Badge variant="secondary">India-ready</Badge>
            </div>
          </div>
          <div className="relative overflow-hidden rounded-xl,">
            <img
              src="/Fake_News.jpg"
              alt="Fact-checking news with a magnifying glass"
              className="aspect-video w-full rounded-lg object-cover mt-10"
            />
            <div className="absolute inset-0 bg-gradient-to-tr from-background/10 to-transparent pointer-events-none" />
          </div>
        </section>

        {/* Features */}
        <section className="mt-12 grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              icon: <Upload className="h-5 w-5" />,
              title: "Drag & Drop",
              desc: "Images or text files",
            },
            {
              icon: <Languages className="h-5 w-5" />,
              title: "English/Hindi",
              desc: "Auto detect",
            },
            {
              icon: <Sparkles className="h-5 w-5" />,
              title: "Explainable",
              desc: "Transparent evidence",
            },
            {
              icon: <History className="h-5 w-5" />,
              title: "History",
              desc: "Local only",
            },
          ].map((f) => (
            <Card key={f.title}>
              <CardHeader className="flex flex-row items-center gap-3">
                <div className="rounded-md bg-primary/10 p-2 text-primary">
                  {f.icon}
                </div>
                <div>
                  <CardTitle className="text-base">{f.title}</CardTitle>
                  <CardDescription>{f.desc}</CardDescription>
                </div>
              </CardHeader>
            </Card>
          ))}
        </section>

        {/* Verification Interface */}
        <section id="verify" className="mt-12 grid lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>{t("Quick Verification", "त्वरित सत्यापन")}</CardTitle>
              <CardDescription>
                {t(
                  "Paste text or drop an image.",
                  "टेक्स्ट पेस्ट करें या इमेज छोड़ें।"
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragActive(true);
                }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
                className={`flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed p-6 text-center transition-colors ${dragActive ? "border-primary bg-primary/5" : ""}`}
              >
                <Upload className="h-6 w-6 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Drag & drop image or text file here
                </p>
                <div className="flex items-center gap-2">
                  <Input
                    ref={inputRef}
                    type="file"
                    accept="image/*,.txt,.md,.csv"
                    onChange={(e) => {
                      const f = e.target.files?.[0];
                      if (!f) return;
                      if (f.type.startsWith("image/")) {
                        setImagePreview(URL.createObjectURL(f));
                      } else {
                        const reader = new FileReader();
                        reader.onload = () =>
                          setText(String(reader.result || ""));
                        reader.readAsText(f);
                      }
                    }}
                  />
                  <Button
                    variant="outline"
                    onClick={() => inputRef.current?.click()}
                  >
                    Browse
                  </Button>
                </div>
                {imagePreview && (
                  <img
                    src={imagePreview}
                    alt="preview"
                    className="mt-3 max-h-52 rounded-md object-contain"
                  />
                )}
              </div>

              <div className="grid sm:grid-cols-3 gap-3">
                <div className="sm:col-span-2">
                  <Textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder={t(
                      "Paste suspicious text…",
                      "संदिग्ध टेक्स्ट पेस्ट करें…"
                    )}
                    rows={6}
                  />
                  <div className="mt-2 text-xs text-muted-foreground">
                    Auto: {autodetected.toUpperCase()}
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm">{t("Language", "भाषा")}</label>
                    <Select value={lang} onValueChange={(v: any) => setLang(v)}>
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Auto" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="auto">Auto Detect</SelectItem>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="hi">हिन्दी</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="rounded-md border p-3 flex items-center justify-between">
                    <span className="text-sm">
                      {t("Confidence", "विश्वास")}
                    </span>
                    <CircularConfidence value={confidence} />
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <Button
                  onClick={analyze}
                  disabled={loading || (!text && !imagePreview)}
                  className="gap-2"
                >
                  {loading ? "Analyzing…" : t("Analyze", "विश्लेषण करें")}{" "}
                  <ArrowRight className="h-4 w-4" />
                </Button>
                <Link href="/results">
                  <Button variant="secondary" className="gap-2">
                    {t("Open Results", "परिणाम खोलें")}
                    <Activity className="h-4 w-4" />
                  </Button>
                </Link>
                <Button variant="outline" onClick={resetAll}>
                  Reset
                </Button>
                <Button
                  variant="outline"
                  onClick={() =>
                    setText("Breaking: Viral claim debunked by authorities.")
                  }
                >
                  Sample
                </Button>
                <Button variant="outline" onClick={share} className="gap-2">
                  <Share2 className="h-4 w-4" /> Share
                </Button>
              </div>

              {/* Error Display */}
              {error && (
                <div className="mt-4 p-3 rounded-md bg-red-50 border border-red-200">
                  <p className="text-sm text-red-600">
                    <strong>Error:</strong> {error}
                  </p>
                  <p className="text-xs text-red-500 mt-1">
                    Make sure the backend is running on http://localhost:8000
                  </p>
                </div>
              )}

              {/* API Result Display */}
              {apiResult && (
                <div className="mt-4 p-4 rounded-md bg-blue-50 border border-blue-200">
                  <h4 className="text-sm font-semibold text-blue-800 mb-2">
                    Analysis Results
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="font-medium">Processing time:</span>{" "}
                      {(apiResult.processing_time || 0).toFixed(2)}s
                    </div>
                    <div>
                      <span className="font-medium">Verdict:</span>{" "}
                      {apiResult.overall_verdict}
                    </div>
                    <div>
                      <span className="font-medium">Confidence:</span>{" "}
                      {((apiResult.confidence || 0) * 100).toFixed(1)}%
                    </div>
                    <div>
                      <span className="font-medium">Text Analysis:</span>{" "}
                      {apiResult.text_analysis?.prediction || "N/A"}
                    </div>
                  </div>
                  {apiResult.explanation && (
                    <p className="text-xs text-blue-600 mt-2 border-t border-blue-200 pt-2">
                      <strong>Explanation:</strong> {apiResult.explanation}
                    </p>
                  )}
                  {apiResult.text_analysis?.explanation && (
                    <p className="text-xs text-blue-500 mt-1">
                      <strong>Text Details:</strong>{" "}
                      {apiResult.text_analysis.explanation}
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("Live Insights", "तुरंत अंतर्दृष्टि")}</CardTitle>
              <CardDescription>
                {t(
                  "Model signals update as you type.",
                  "जैसे ही आप टाइप करते हैं संकेत अपडेट होते हैं।"
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span>{t("Risk level", "जोखिम स्तर")}</span>
                  <Badge variant="outline">
                    {confidence > 66
                      ? t("Low", "कम")
                      : confidence < 34
                        ? t("High", "उच्च")
                        : t("Medium", "मध्यम")}
                  </Badge>
                </div>
                <Progress value={confidence} />
              </div>
              <div className="space-y-2">
                <div className="text-sm font-medium">
                  {t("Evidence", "साक्ष्य")}
                </div>
                <div className="space-y-2">
                  {evidence.map((ev) => (
                    <a
                      key={ev.source}
                      href={ev.url}
                      target="_blank"
                      rel="noreferrer"
                      className="block rounded-md border p-2 hover:bg-accent"
                    >
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium">{ev.source}</span>
                        <Badge variant="secondary">{ev.credibility}%</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {ev.excerpt}
                      </p>
                    </a>
                  ))}
                </div>
              </div>
              <div className="text-sm text-muted-foreground">
                {t("Verdict", "निर्णय")}:{" "}
                <span className="font-semibold">
                  {verdict ?? t("Pending", "प्रतीक्षारत")}
                </span>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Advanced */}
        <section className="mt-12">
          <Tabs defaultValue="learn">
            <TabsList className="grid grid-cols-2 md:grid-cols-4 w-full">
              <TabsTrigger value="learn">Learning Mode</TabsTrigger>
              <TabsTrigger value="batch">Batch</TabsTrigger>
              <TabsTrigger value="collab">Collaboration</TabsTrigger>
              <TabsTrigger value="ext">Extension</TabsTrigger>
            </TabsList>
            <TabsContent value="learn">
              <Card>
                <CardHeader>
                  <CardTitle>How to spot misinformation</CardTitle>
                  <CardDescription>Common patterns and signals</CardDescription>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground space-y-2">
                  <p>
                    Watch for sensational language, mismatched dates,
                    low-quality images, and unverifiable sources.
                  </p>
                  <p>Cross-check with credible fact-checkers before sharing.</p>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="batch">
              <Card>
                <CardHeader>
                  <CardTitle>Batch Processing</CardTitle>
                  <CardDescription>
                    Upload multiple items for verification
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Input type="file" multiple accept="image/*,.txt" />
                  <div className="mt-2 text-sm text-muted-foreground">
                    Coming soon: queue, progress, and exports.
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="collab">
              <Card>
                <CardHeader>
                  <CardTitle>Real-time Collaboration</CardTitle>
                  <CardDescription>Invite teammates to review</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    onClick={() =>
                      alert(
                        "Shared room created (mock): mv-" +
                          Math.random().toString(36).slice(2, 7)
                      )
                    }
                  >
                    Create shared room
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="ext">
              <Card>
                <CardHeader>
                  <CardTitle>Browser Extension</CardTitle>
                  <CardDescription>Preview</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <img
                    className="rounded-md border"
                    alt="extension preview"
                    src="https://images.unsplash.com/photo-1526378722484-bd91ca387e72?q=80&w=1200&auto=format&fit=crop"
                  />
                  <Button
                    onClick={() =>
                      alert(
                        "We will notify you when the extension is ready (mock)."
                      )
                    }
                  >
                    Get notified
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </section>
      </main>
      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        © {new Date().getFullYear()} MitraVerify
      </footer>
    </div>
  );
}

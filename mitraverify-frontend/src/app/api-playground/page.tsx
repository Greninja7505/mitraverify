"use client";

import { useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import Link from "next/link";
import MitraNav from "@/components/MitraNav";

export default function ApiPlayground() {
  const [text, setText] = useState("");
  const [fileName, setFileName] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any | null>(null);

  const code = useMemo(() => {
    const payload: any = { text };
    if (fileName) payload.file = fileName;
    const json = JSON.stringify(payload, null, 2);
    return {
      curl: `curl -X POST https://api.mitraverify.ai/v1/verify -H 'Content-Type: application/json' -d '${json.replace(/\n/g, " ")}'`,
      js: `const res = await fetch('https://api.mitraverify.ai/v1/verify', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(${json}) });\nconst data = await res.json();`,
      python: `import requests\nresp = requests.post('https://api.mitraverify.ai/v1/verify', json=${json})\nprint(resp.json())`,
    };
  }, [text, fileName]);

  const send = async () => {
    setLoading(true);
    // Mock call
    setTimeout(() => {
      const confidence = Math.min(99, Math.max(1, Math.floor(text.length / 3)));
      setResponse({ verdict: confidence > 66 ? "Real" : confidence < 34 ? "Fake" : "Uncertain", confidence, id: Math.random().toString(36).slice(2) });
      setLoading(false);
    }, 600);
  };

  return (
    <div>
      <MitraNav />
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold">API Playground</h1>
          <Link href="/"><Button variant="ghost">Home</Button></Link>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Request</CardTitle>
              <CardDescription>Test verification API</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Textarea rows={6} value={text} onChange={(e) => setText(e.target.value)} placeholder="Enter text to verify" />
              <div className="flex items-center gap-2">
                <Input type="file" onChange={(e) => setFileName(e.target.files?.[0]?.name || null)} />
                <Button variant="outline" onClick={() => setFileName(null)}>Clear file</Button>
              </div>
              <Button onClick={send} disabled={loading || (!text && !fileName)}>{loading ? "Sending…" : "Send"}</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Response</CardTitle>
              <CardDescription>Live output</CardDescription>
            </CardHeader>
            <CardContent>
              {response ? (
                <pre className="rounded-md border p-3 text-sm overflow-auto">{JSON.stringify(response, null, 2)}</pre>
              ) : (
                <div className="text-sm text-muted-foreground">No response yet</div>
              )}
            </CardContent>
          </Card>
        </div>

        <Separator className="my-8" />

        <Card>
          <CardHeader>
            <CardTitle>Integration Examples</CardTitle>
            <CardDescription>Copy and paste into your app</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="curl">
              <TabsList>
                <TabsTrigger value="curl">cURL</TabsTrigger>
                <TabsTrigger value="js">JavaScript</TabsTrigger>
                <TabsTrigger value="py">Python</TabsTrigger>
              </TabsList>
              <TabsContent value="curl"><pre className="rounded-md border p-3 text-sm overflow-auto">{code.curl}</pre></TabsContent>
              <TabsContent value="js"><pre className="rounded-md border p-3 text-sm overflow-auto">{code.js}</pre></TabsContent>
              <TabsContent value="py"><pre className="rounded-md border p-3 text-sm overflow-auto">{code.python}</pre></TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
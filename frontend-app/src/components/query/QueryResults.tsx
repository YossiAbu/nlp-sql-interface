import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Copy, Check, Database, AlertTriangle } from "lucide-react";

interface Props {
  query: {
    sql_query: string;
    status: "success" | "error";
    execution_time: number;
    results?: Record<string, unknown>[];
    error_message?: string;
  } | null;
  isLoading: boolean;
}

export default function QueryResults({ query, isLoading }: Props) {
  const [copied, setCopied] = useState(false);

  if (!query && !isLoading) return null;

  /* skeleton */
  if (isLoading) {
    return (
      <Card className="bg-surface-card border border-theme animate-pulse">
        <CardContent className="p-6 space-y-4">
          <div className="h-6 w-1/2 bg-surface-input rounded" />
          <div className="h-48 w-full bg-surface-input rounded" />
        </CardContent>
      </Card>
    );
  }

  const copySql = async () => {
    if (!query?.sql_query) return;
    await navigator.clipboard.writeText(query.sql_query);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <>
      {/* SQL card */}
      <Card className="bg-surface-card border border-theme shadow-2xl">
        <CardHeader className="flex flex-row items-center justify-between gap-4 pb-3">
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            Generated SQL&nbsp;({query!.execution_time} ms)
          </CardTitle>
          <Button
            size="sm"
            variant="outline"
            onClick={copySql}
            className="border-theme bg-surface-input hover:bg-surface-input/80 text-muted-body"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 mr-1" /> Copied
              </>
            ) : (
              <>
                <Copy className="w-4 h-4 mr-1" /> Copy
              </>
            )}
          </Button>
        </CardHeader>
        <CardContent>
          <pre className="bg-surface-input border border-theme rounded-xl p-4 font-mono text-sm overflow-x-auto whitespace-pre-wrap">
            {query!.sql_query}
          </pre>
        </CardContent>
      </Card>

      {/* results or error */}
      {query!.status === "success" ? (
        query!.results?.length ? (
          <Card className="bg-surface-card border border-theme shadow-2xl">
            <CardHeader>
              <CardTitle>
                Results&nbsp;({query!.results.length}
                {query!.results.length === 1 ? " row" : " rows"})
              </CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr>
                    {Object.keys(query!.results[0]).map((col) => (
                      <th
                        key={col}
                        className="px-4 py-2 text-left font-semibold border-b border-theme"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {query!.results.map((row, i) => (
                    <tr
                      key={i}
                      className={i % 2 ? "bg-surface-input/50" : undefined}
                    >
                      {Object.values(row).map((val, j) => (
                        <td key={j} className="px-4 py-2 border-b border-theme">
                          {String(val)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        ) : null
      ) : (
        <Card className="bg-surface-card border border-theme shadow-2xl">
          <CardHeader className="flex flex-row items-center gap-2 text-red-600">
            <AlertTriangle className="w-5 h-5" />
            <CardTitle>Error executing query</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{query!.error_message ?? "Unknown error."}</p>
          </CardContent>
        </Card>
      )}
    </>
  );
}

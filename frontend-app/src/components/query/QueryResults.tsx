import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Copy, Check, Database, AlertTriangle, MessageSquare } from "lucide-react";
import { format as formatSql } from "sql-formatter";

interface Props {
  query: {
    sql_query: string;
    status: "success" | "error";
    execution_time: number;
    results?: string; // Natural language result
    raw_rows?: Record<string, unknown>[]; // Actual SQL results
    error_message?: string;
  } | null;
  isLoading: boolean;
  userQuestion?: string;
}

export default function QueryResults({ query, isLoading, userQuestion }: Props) {
  const [copiedQuestion, setCopiedQuestion] = useState(false);
  const [copiedSql, setCopiedSql] = useState(false);

  if (!query && !isLoading) return null;

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

  const copyQuestion = async () => {
    if (!userQuestion) return;
    await navigator.clipboard.writeText(userQuestion);
    setCopiedQuestion(true);
    setTimeout(() => setCopiedQuestion(false), 1500);
  };

  const copySql = async () => {
    if (!query?.sql_query) return;
    await navigator.clipboard.writeText(query.sql_query);
    setCopiedSql(true);
    setTimeout(() => setCopiedSql(false), 1500);
  };

  let formattedSQL = query!.sql_query;
  try {
    if (query!.status === "success" && query!.sql_query) {
      formattedSQL = formatSql(query!.sql_query);
    }
  } catch {
    formattedSQL = query!.sql_query;
  }

  return (
    <>
      {/* SQL card */}
      <Card className="bg-surface-card border-2 border-theme shadow-2xl mt-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            Generated SQL&nbsp;({query!.execution_time} ms)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* User Question */}
          {userQuestion && (
            <div className="mb-4 p-3 bg-surface-input/50 border border-theme/50 rounded-lg relative">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-primary" />
                  <span className="text-sm font-medium text-muted-body">Your Question</span>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={copyQuestion}
                  className="border-theme/50 bg-surface-input/50 hover:bg-surface-input/80 text-muted-body h-7 px-2"
                >
                  {copiedQuestion ? <><Check className="w-3 h-3 mr-1" /> Copied</> : <><Copy className="w-3 h-3 mr-1" /> Copy</>}
                </Button>
              </div>
              <p className="text-body italic">"{userQuestion}"</p>
            </div>
          )}

          {/* SQL Query Display */}
          <div className="relative">
            <div className="flex items-center gap-2 mb-2">
              <Database className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-muted-body">SQL Query</span>
            </div>
            <div className="relative">
              <pre className="bg-surface-input border border-theme rounded-xl p-4 pr-16 font-mono text-sm overflow-x-auto whitespace-pre-wrap">
                {formattedSQL || "No SQL query generated"}
              </pre>
              {query!.sql_query && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={copySql}
                  className="absolute top-3 right-3 border-theme bg-surface-input hover:bg-surface-input/80 text-muted-body h-7 px-2"
                >
                  {copiedSql ? <><Check className="w-3 h-3 mr-1" /> Copied</> : <><Copy className="w-3 h-3 mr-1" /> Copy</>}
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Display */}
      {query!.status === "success" ? (
        <>
          {/* Results Table - showing raw_rows */}
          {query!.raw_rows && query!.raw_rows.length > 0 ? (
            <Card className="bg-surface-card border-2 border-theme shadow-2xl mt-8">
              <CardHeader>
                <CardTitle>Results Table ({query!.raw_rows.length} {query!.raw_rows.length === 1 ? "row" : "rows"})</CardTitle>
              </CardHeader>
              <CardContent className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr>
                      {Object.keys(query!.raw_rows[0]).map((col) => (
                        <th key={col} className="px-4 py-2 text-left font-semibold border-b border-theme">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {query!.raw_rows.map((row, i) => (
                      <tr key={i} className={i % 2 ? "bg-surface-input/50" : undefined}>
                        {Object.values(row).map((val, j) => (
                          <td key={j} className="px-4 py-2 border-b border-theme">
                            {val === null ? 'null' : String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          ) : null}

          {/* Human-readable answer */}
          {query!.results && (
            <Card className="bg-surface-card border-2 border-theme shadow-2xl mt-8">
              <CardHeader>
                <CardTitle>Answer</CardTitle>
              </CardHeader>
              <CardContent>
                <p>{query!.results}</p>
              </CardContent>
            </Card>
          )}
        </>
      ) : (
        <Card className="bg-surface-card border border-theme shadow-2xl mt-8">
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
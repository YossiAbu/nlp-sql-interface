import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Database, Clock, Play, AlertCircle, Check, Copy } from "lucide-react";
import { format as formatDate } from "date-fns";
import { format as formatSql } from "sql-formatter";
import { Query } from "@/entities/Query";

interface Props {
  query: Query;
  onRerun?: (q: Query) => void;
  index: number;
}

export default function HistoryItem({ query, onRerun, index }: Props) {
  const [copiedQuestion, setCopiedQuestion] = useState(false);
  const [copiedSql, setCopiedSql] = useState(false);

  const createdAt = query.created_date
    ? formatDate(new Date(query.created_date), "dd/MM/yyyy 'at' HH:mm")
    : "Unknown";

  const handleRerun = (e: React.MouseEvent) => {
    e.stopPropagation();
    onRerun?.(query);
  };

  const copyQuestion = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await navigator.clipboard.writeText(query.question);
    setCopiedQuestion(true);
    setTimeout(() => setCopiedQuestion(false), 1500);
  };

  const copySql = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (query.sql_query) {
      await navigator.clipboard.writeText(query.sql_query);
      setCopiedSql(true);
      setTimeout(() => setCopiedSql(false), 1500);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }}>
      <Card className="bg-white/5 backdrop-blur-xl border border-white/10 shadow-lg hover:bg-white/10 transition-all duration-200 cursor-pointer group">
        <CardContent className="">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              {/* Question with copy button */}
              <div className="relative mb-2">
                <p className="text-muted-body font-medium pr-10 break-words whitespace-pre-wrap">
                  {query.question}
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={copyQuestion}
                  className="absolute -top-1 right-0 opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-white hover:bg-slate-800/50 h-10 px-2"
                >
                  {copiedQuestion ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                </Button>
              </div>

              <div className="flex items-center gap-2 text-sm dark:text-slate-400 text-slate-600 mb-3">
                <Clock className="w-3 h-3" />
                {createdAt}
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                {query.status === "success" ? (
                  <Badge className="bg-green-500/20 dark:text-green-400 text-green-600 border-green-500/30 text-xs">
                    <Check className="w-3 h-3 mr-1" />
                    Success
                  </Badge>
                ) : (
                  <Badge className="bg-red-500/20 dark:text-red-400 text-red-600 border-red-500/30 text-xs">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    Error
                  </Badge>
                )}
                {query.execution_time !== undefined && (
                  <Badge variant="outline" className="dark:text-slate-400 text-slate-600 border-slate-600 text-xs">
                    {query.execution_time}ms
                  </Badge>
                )}
                {/* ✅ show count from raw_rows (not results string) */}
                {query.raw_rows && query.raw_rows.length > 0 && (
                  <Badge variant="outline" className="dark:text-slate-400 text-slate-600 border-slate-600 text-xs">
                    {query.raw_rows.length} rows
                  </Badge>
                )}
              </div>
            </div>

            {onRerun && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRerun}
                className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-white hover:bg-slate-800/50"
              >
                <Play className="w-4 h-4 mr-1" />
                Rerun
              </Button>
            )}
          </div>

          {query.sql_query && (
            <div className="mt-3 p-3 dark:bg-slate-900/50 bg-slate-100 rounded-lg border border-slate-700/30 relative">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-3 h-3 dark:text-blue-400 text-blue-600" />
                <span className="text-xs dark:text-slate-400 text-slate-600 font-medium">SQL Query</span>
              </div>
              <pre className="text-xs dark:text-blue-300 text-blue-500 font-mono whitespace-pre-wrap break-words pr-8">
                {formatSql(query.sql_query)}
              </pre>
              <Button
                variant="ghost"
                size="sm"
                onClick={copySql}
                className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 h-auto w-auto text-slate-400 hover:text-white hover:bg-slate-800/50"
              >
                {copiedSql ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

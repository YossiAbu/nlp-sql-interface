import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  Copy,
  Check,
  Clock,
  Database,
  AlertCircle,
} from "lucide-react";
import { Query } from "@/entities/Query";

// ✅ Define props interface
interface QueryResultsProps {
  query: Query | null;
  isLoading: boolean;
}

export default function QueryResults({ query, isLoading }: QueryResultsProps) {
  const [copied, setCopied] = useState<boolean>(false);

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="w-full max-w-6xl mx-auto"
      >
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl p-8">
          <div className="flex items-center justify-center space-x-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span className="text-white font-medium">
              Analyzing your question...
            </span>
          </div>
          <div className="mt-4 text-center text-slate-400 text-sm">
            Converting natural language to SQL and executing query
          </div>
        </div>
      </motion.div>
    );
  }

  if (!query) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -30 }}
        className="w-full max-w-6xl mx-auto space-y-6"
      >
        {/* Query Header */}
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl p-6">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Query Results
              </h3>
              <p className="text-slate-300 text-lg">"{query.question}"</p>
            </div>
            <div className="flex items-center gap-3">
              {query.status === "success" ? (
                <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                  <Database className="w-3 h-3 mr-1" />
                  Success
                </Badge>
              ) : (
                <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
                  <AlertCircle className="w-3 h-3 mr-1" />
                  Error
                </Badge>
              )}
              {query.execution_time && (
                <Badge
                  variant="outline"
                  className="text-slate-400 border-slate-600"
                >
                  <Clock className="w-3 h-3 mr-1" />
                  {query.execution_time}ms
                </Badge>
              )}
            </div>
          </div>
        </div>

        {/* SQL Query Display */}
        <Card className="bg-white/5 backdrop-blur-xl border-white/10 shadow-2xl">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-white flex items-center gap-2">
                <Database className="w-5 h-5" />
                Generated SQL Query
              </CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(query.sql_query)}
                className="bg-slate-800/50 border-slate-600/50 text-slate-300 hover:bg-slate-700/50 hover:text-white"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4 mr-2" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4 mr-2" />
                    Copy SQL
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="bg-slate-900/80 rounded-xl p-4 font-mono text-sm border border-slate-700/50">
              <pre className="text-blue-300 whitespace-pre-wrap overflow-x-auto">
                {query.sql_query}
              </pre>
            </div>
          </CardContent>
        </Card>

        {/* Results Table */}
        {query.status === "success" &&
        query.results &&
        query.results.length > 0 ? (
          <Card className="bg-white/5 backdrop-blur-xl border-white/10 shadow-2xl">
            <CardHeader>
              <CardTitle className="text-white">
                Results ({query.results.length}{" "}
                {query.results.length === 1 ? "row" : "rows"})
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-slate-700/50 hover:bg-slate-800/30">
                      {Object.keys(query.results[0]).map((column: string) => (
                        <TableHead
                          key={column}
                          className="text-slate-200 font-semibold"
                        >
                          {column}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {query.results.map(
                      (
                        row: Record<string, any>,
                        index: number
                      ) => (
                        <TableRow
                          key={index}
                          className="border-slate-700/50 hover:bg-slate-800/20 transition-colors"
                        >
                          {Object.values(row).map(
                            (value: any, cellIndex: number) => (
                              <TableCell
                                key={cellIndex}
                                className="text-slate-300"
                              >
                                {value !== null && value !== undefined
                                  ? String(value)
                                  : "-"}
                              </TableCell>
                            )
                          )}
                        </TableRow>
                      )
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        ) : query.status === "error" ? (
          <Card className="bg-red-500/10 backdrop-blur-xl border-red-500/20 shadow-2xl">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 text-red-400">
                <AlertCircle className="w-6 h-6" />
                <div>
                  <h3 className="font-semibold mb-1">Query Error</h3>
                  <p className="text-sm">
                    {query.error_message ||
                      "An error occurred while executing the query"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : query.status === "success" &&
          (!query.results || query.results.length === 0) ? (
          <Card className="bg-white/5 backdrop-blur-xl border-white/10 shadow-2xl">
            <CardContent className="p-6 text-center">
              <Database className="w-12 h-12 text-slate-400 mx-auto mb-3" />
              <h3 className="text-white font-semibold mb-1">No Results Found</h3>
              <p className="text-slate-400 text-sm">
                Your query executed successfully but returned no data.
              </p>
            </CardContent>
          </Card>
        ) : null}
      </motion.div>
    </AnimatePresence>
  );
}

import React from "react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Database, Clock, Play, AlertCircle, Check } from "lucide-react";
import { format } from "date-fns";
import { Query } from "@/entities/Query";

interface HistoryItemProps {
  query: Query;
  onRerun: (query: Query) => void;
  index: number;
}

export default function HistoryItem({ query, onRerun, index }: HistoryItemProps) {

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <Card className="bg-white/5 backdrop-blur-xl border-white/10 shadow-lg hover:bg-white/10 transition-all duration-200 cursor-pointer group">
        <CardContent className="p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium mb-2 line-clamp-2">
                {query.question}
              </p>
              <div className="flex items-center gap-2 text-sm text-slate-400 mb-3">
                <Clock className="w-3 h-3" />
                {format(new Date(query.created_date ?? Date.now()), "MMM d, yyyy 'at' h:mm a")}
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                {query.status === 'success' ? (
                  <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-xs">
                    <Check className="w-3 h-3 mr-1" />
                    Success
                  </Badge>
                ) : (
                  <Badge className="bg-red-500/20 text-red-400 border-red-500/30 text-xs">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    Error
                  </Badge>
                )}
                {query.execution_time && (
                  <Badge variant="outline" className="text-slate-400 border-slate-600 text-xs">
                    {query.execution_time}ms
                  </Badge>
                )}
                {query.results && (
                  <Badge variant="outline" className="text-slate-400 border-slate-600 text-xs">
                    {query.results.length} rows
                  </Badge>
                )}
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onRerun(query);
              }}
              className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-white hover:bg-slate-800/50"
            >
              <Play className="w-4 h-4 mr-1" />
              Rerun
            </Button>
          </div>
          
          {query.sql_query && (
            <div className="mt-3 p-3 bg-slate-900/50 rounded-lg border border-slate-700/30">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-3 h-3 text-blue-400" />
                <span className="text-xs text-slate-400 font-medium">SQL Query</span>
              </div>
              <pre className="text-xs text-blue-300 font-mono truncate">
                {query.sql_query}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}


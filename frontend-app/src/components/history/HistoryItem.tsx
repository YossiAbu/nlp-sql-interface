import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Play, Database } from "lucide-react";
import { Query } from "@/entities/Query";

interface Props {
  query: Query;
  onRerun?: (q: Query) => void;
}

export default function HistoryItem({ query, onRerun }: Props) {
  /** 
   * Safely format the date:
   * - If `created_date` is undefined or unparsable, show “Unknown”.
   * - Otherwise show a locale-formatted timestamp.
   */
  const runAt = (() => {
    if (!query.created_date) return "Unknown";
    const parsed = new Date(query.created_date);
    return isNaN(parsed.getTime())
      ? "Unknown"
      : parsed.toLocaleString();
  })();

  return (
    <motion.div layout>
      <Card className="bg-surface-card border border-theme hover:shadow-xl transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            <CardTitle className="text-sm font-semibold">
              {query.question}
            </CardTitle>
          </div>

          {onRerun && (
            <Button
              size="icon"
              variant="outline"
              className="border-theme bg-surface-input hover:bg-surface-input/80"
              onClick={() => onRerun(query)}
            >
              <Play className="w-4 h-4" />
            </Button>
          )}
        </CardHeader>

        <CardContent className="text-xs text-muted-body">
          Ran&nbsp;on&nbsp;{runAt}
        </CardContent>
      </Card>
    </motion.div>
  );
}

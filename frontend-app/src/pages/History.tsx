import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import HistoryItem from "@/components/history/HistoryItem";
import { History as HistoryIcon } from "lucide-react";
import { Query } from "@/entities/Query";
import { useAuth } from "@/contexts/AuthContext";

export default function History() {
  const { user } = useAuth();
  const [queries, setQueries] = useState<Query[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  /* fetch on mount */
  useEffect(() => {
    if (!user) return;

    const fetchHistory = async () => {
      setIsLoading(true);
      // TODO: replace with real API call
      await new Promise((r) => setTimeout(r, 800));
      setQueries([]); // fill with data
      setIsLoading(false);
    };

    fetchHistory();
  }, [user]);

  if (!user)
    return (
      <div className="min-h-screen bg-surface text-body flex items-center justify-center">
        Please log in to view your history.
      </div>
    );

  if (isLoading)
    return (
      <div className="min-h-screen bg-surface text-body flex items-center justify-center">
        Loading…
      </div>
    );

  return (
    <div className="min-h-screen bg-surface text-body p-4">
      <div className="mx-auto max-w-6xl space-y-6">
        <motion.header
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-[var(--primary)] to-pink-600 flex items-center justify-center">
              <HistoryIcon className="w-6 h-6 text-[var(--primary-foreground)]" />
            </div>
            <h1 className="text-3xl font-bold">My Query History</h1>
          </div>
          <p className="text-lg text-muted-body">
            Review and rerun your past queries
          </p>
        </motion.header>

        <motion.section layout className="space-y-4">
          {queries.length ? (
            queries.map((q) => <HistoryItem key={q.id} query={q} />)
          ) : (
            <p className="text-center text-muted-body">
              You haven’t run any queries yet.
            </p>
          )}
        </motion.section>
      </div>
    </div>
  );
}

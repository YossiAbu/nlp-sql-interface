import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Query as QueryType } from "@/entities/Query";
import { User, UserAPI } from "@/entities/User";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, History as HistoryIcon, Database, Trash2, LogIn } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { createPageUrl } from "@/utils";
import HistoryItem from "../components/history/HistoryItem";

export default function History() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [queries, setQueries] = useState<QueryType[]>([]);
  const [filteredQueries, setFilteredQueries] = useState<QueryType[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      try {
        const currentUser = await UserAPI.me();
        setUser(currentUser);
        if (currentUser)
          await loadQueries(currentUser);
      } catch {
        setUser(null);
      }
      setIsLoading(false);
    };
    init();
  }, []);

  useEffect(() => {
    filterQueries();
  }, [queries, searchTerm, statusFilter]);

  const loadQueries = async (currentUser: User) => {
    if (!currentUser) return;
    try {
      const dummyQueries: QueryType[] = [
        {
          id: "1",
          question: "Show me all users created this month",
          sql_query: "SELECT * FROM users WHERE created_at >= '2024-08-01'",
          results: "",
          status: "success",
          execution_time: 120,
          created_date: new Date().toISOString()
        },
        {
          id: "2",
          question: "List products with no stock",
          sql_query: "SELECT * FROM products WHERE stock = 0",
          results: "",
          status: "error",
          execution_time: 80,
          error_message: "Simulated error",
          created_date: new Date().toISOString()
        },
        {
          id: "3",
          question: "What are the top 5 best-selling products by revenue",
          sql_query: "SELECT p.name, p.price, SUM(oi.quantity) as total_sold, SUM(oi.quantity * p.price) as total_revenue FROM products p JOIN order_items oi ON p.id = oi.product_id GROUP BY p.id ORDER BY total_revenue DESC LIMIT 5;",
          results: "",
          status: "error",
          execution_time: 80,
          error_message: "Simulated error",
          created_date: new Date().toISOString()
        }
      ];
      setQueries(dummyQueries);
    } catch (error) {
      console.error("Error loading queries:", error);
    }
  };

  const filterQueries = () => {
    let filtered = [...queries];
    if (searchTerm) {
      filtered = filtered.filter(q =>
        q.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
        q.sql_query.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (statusFilter !== "all") {
      filtered = filtered.filter(q => q.status === statusFilter);
    }
    setFilteredQueries(filtered);
  };

  /* ------------------------------------------------------------------ */
  /* Handler: Rerun query - Navigate to QueryInterface                  */
  /* ------------------------------------------------------------------ */
  const handleRerunQuery = (query: QueryType) => {
    // Navigate to the interface page with the question parameter
    navigate(`/interface?question=${encodeURIComponent(query.question)}`);
  };

  const clearHistory = async () => {
    alert("This demo does not support real history clearing.");
  };

  const handleLogin = async () => {
    await UserAPI.login();
    location.reload();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface text-body p-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-surface text-body p-4 flex items-center justify-center">
        <div className="text-center">
          <HistoryIcon className="w-16 h-16 text-slate-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">View Your Query History</h2>
          <p className="text-slate-300 mb-6">Log in to access your personal query history.</p>
          <Button onClick={handleLogin} className="bg-brand-gradient hover:bg-brand-gradient-hover text-white">
            <LogIn className="w-4 h-4 mr-2" />
            Login to Continue
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface text-body p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 bg-brand-gradient rounded-xl flex items-center justify-center shadow-lg">
              <HistoryIcon className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-muted-body">My Query History</h1>
          </div>
          <p className="text-muted-body text-lg">
            Review and rerun your previous database queries
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl p-6"
        >
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
            <div className="flex items-center gap-4">
              <Badge className="bg-blue-500/20 dark:text-blue-400 text-blue-600 border-blue-500/30 px-3 py-1">
                <Database className="w-4 h-4 mr-2" />
                {queries.length} Total Queries
              </Badge>
              <Badge className="bg-green-500/20 dark:text-green-400 text-green-600 border-green-500/30 px-3 py-1">
                {queries.filter(q => q.status === 'success').length} Successful
              </Badge>
              <Badge className="bg-red-500/20 dark:text-red-400 text-red-600 border-red-500/30 px-3 py-1">
                {queries.filter(q => q.status === 'error').length} Errors
              </Badge>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={clearHistory}
              className="dark:bg-slate-800/50 bg-slate-100 border-slate-600/50 dark:text-slate-300 text-slate-600 hover:bg-slate-700/50 hover:text-white"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear History
            </Button>
          </div>

          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 dark:text-slate-400 text-slate-600 w-4 h-4" />
              <Input
                placeholder="Search queries or SQL..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 dark:bg-slate-800/50 bg-slate-100 border-slate-600/50 dark:text-white text-gray-950 dark:placeholder:text-slate-400 placeholder:text-slate-600 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="dark:bg-slate-800/50 bg-slate-100 border border-slate-600/50 dark:text-white text-gray-950 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50"
              >
                <option value="all">All Status</option>
                <option value="success">Success Only</option>
                <option value="error">Errors Only</option>
              </select>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          {filteredQueries.length > 0 ? (
            filteredQueries.map((query, index) => (
              <HistoryItem
                key={query.id ?? index}
                query={query}
                onRerun={handleRerunQuery}
                index={index}
              />
            ))
          ) : (
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl p-12 text-center">
              <HistoryIcon className="w-16 h-16 text-slate-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold dark:text-white text-gray-950 mb-2">
                {searchTerm || statusFilter !== "all" ? "No matching queries found" : "No queries yet"}
              </h3>
              <p className="text-slate-400 mb-6">
                {searchTerm || statusFilter !== "all" 
                  ? "Try adjusting your search or filter criteria"
                  : "Start by asking your first question in the Query Interface"
                }
              </p>
              <Button
                onClick={() => navigate("/interface")}
                className="bg-brand-gradient hover:bg-brand-gradient-hover text-white"
              >
                <Database className="w-4 h-4 mr-2" />
                Start Querying
              </Button>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
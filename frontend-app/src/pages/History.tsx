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
          results: [{ id: 1, name: "Alice" }],
          status: "success",
          execution_time: 120,
          created_date: new Date().toISOString()
        },
        {
          id: "2",
          question: "List products with no stock",
          sql_query: "SELECT * FROM products WHERE stock = 0",
          results: [],
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

  const handleRerunQuery = (query: QueryType) => {
    navigate(`${createPageUrl("QueryInterface")}?question=${encodeURIComponent(query.question)}`);
  };

  const clearHistory = async () => {
    alert("This demo does not support real history clearing.");
  };

  const handleLogin = async () => {
    await UserAPI.login();
    location.reload();
  };

  if (isLoading) {
    return <div className="min-h-screen bg-slate-900 p-4 text-white text-center">Loading...</div>;
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 p-4 text-white text-center">
        <div>
          <HistoryIcon className="w-16 h-16 text-slate-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Login to view query history</h2>
          <Button onClick={handleLogin}>
            <LogIn className="w-4 h-4 mr-2" />
            Login
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
              <HistoryIcon className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">My Query History</h1>
          </div>
          <p className="text-slate-300 text-lg">Review and rerun your past queries</p>
        </motion.div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 justify-between items-center mb-6">
          <div className="flex gap-4">
            <Badge className="bg-blue-500/20 text-blue-400">Total: {queries.length}</Badge>
            <Badge className="bg-green-500/20 text-green-400">Success: {queries.filter(q => q.status === 'success').length}</Badge>
            <Badge className="bg-red-500/20 text-red-400">Errors: {queries.filter(q => q.status === 'error').length}</Badge>
          </div>
          <Button onClick={clearHistory} variant="outline">
            <Trash2 className="w-4 h-4 mr-2" />
            Clear History
          </Button>
        </div>

        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 text-slate-400 w-4 h-4" />
            <Input
              placeholder="Search..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="bg-slate-800 text-white rounded-lg px-3 py-2"
            >
              <option value="all">All</option>
              <option value="success">Success</option>
              <option value="error">Error</option>
            </select>
          </div>
        </div>

        {/* Results */}
        <div className="space-y-4">
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
            <div className="text-center text-slate-400 py-12">
              No queries found.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

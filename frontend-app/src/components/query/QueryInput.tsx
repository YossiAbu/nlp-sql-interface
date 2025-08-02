import React, { useState, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Loader2, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

// ✅ Add prop types
interface QueryInputProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
}

export default function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const [question, setQuestion] = useState<string>("");

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (question.trim() && !isLoading) {
      onSubmit(question.trim());
    }
  };

  const placeholderQuestions = [
    "Show me all users who signed up last month",
    "What are the top 5 products by revenue?",
    "Find customers with more than 10 orders",
    "Show monthly sales trends for 2024"
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto"
    >
      <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-xl font-semibold text-white">Ask your database anything</h2>
          </div>

          <div className="relative">
            <Textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Type your question in plain English..."
              className="min-h-[120px] bg-slate-800/50 border-slate-600/50 text-white placeholder:text-slate-400 resize-none text-lg leading-relaxed focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200"
              disabled={isLoading}
            />
          </div>

          <div className="flex justify-between items-center">
            <div className="text-sm text-slate-400">
              Try asking about users, orders, products, or sales data
            </div>
            <Button
              type="submit"
              disabled={!question.trim() || isLoading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5 mr-2" />
                  Ask Database
                </>
              )}
            </Button>
          </div>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-700/50">
          <p className="text-sm text-slate-400 mb-3">Try these example questions:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {placeholderQuestions.map((example, index) => (
              <button
                key={index}
                onClick={() => setQuestion(example)}
                className="text-left p-3 bg-slate-800/30 hover:bg-slate-700/50 rounded-lg text-sm text-slate-300 hover:text-white transition-all duration-200 border border-slate-700/30 hover:border-slate-600/50"
                disabled={isLoading}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

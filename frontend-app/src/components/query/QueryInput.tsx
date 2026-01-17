import { useState, FormEvent } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Sparkles, Loader2, Send } from "lucide-react";
import { cn } from "@/lib/utils";


interface Props {
  onSubmit: (question: string) => void;
  isLoading: boolean;
}

export default function QueryInput({ onSubmit, isLoading }: Props) {
  const [question, setQuestion] = useState("");

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!question.trim() || isLoading) return;
    onSubmit(question.trim());
    setQuestion("");
  };

  const placeholderQuestions = [
    "Show me the top 10 players by overall rating",
    "List all players from Spain in the Premier League",
    "Find the youngest player in the database",
    "Show all goalkeepers with OVR above 85",
    "List the top 5 fastest players by sprint speed",
    "Show all players from Brazil sorted by dribbling",
    "Find all players in LALIGA with OVR above 90",
    "List the tallest players in each position",
    "Show players who play for Manchester City",
    "Find players with both high passing and high dribbling"
];


  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mx-auto w-full max-w-4xl"
    >
      <div className="bg-surface-card backdrop-blur-xl border-2 border-theme rounded-2xl shadow-2xl p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* title */}
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-brand-gradient flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <h2 className="text-xl font-semibold">
              Ask your database anything
            </h2>
          </div>

          {/* textarea */}
          <Textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder='e.g. "Show players who play for Real Madrid"'
            disabled={isLoading}
            className="min-h-[130px] w-full bg-surface-input border-2 border-theme rounded-xl p-4 text-lg leading-relaxed text-body placeholder:text-muted-body resize-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition"
          />

          {/* footer */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-body">
              Tip: reference tables like <em>users</em>, <em>orders</em>, or{" "}
              <em>products</em>.
            </p>

            <Button
              type="submit"
              disabled={!question.trim() || isLoading}
              className="bg-brand-gradient hover:bg-brand-gradient-hover text-white px-6 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Processing
                </>
              ) : (
                <>
                  <Send className="w-5 h-5 mr-2" />
                  Ask&nbsp;Database
                </>
              )}
            </Button>
          </div>
        </form>
        <div className="mt-6 pt-6 border-t border-theme">
          <p className="text-sm text-muted-body mb-3">Try these example questions:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {placeholderQuestions.map((example, index) => (
              <button
                key={index}
                onClick={() => setQuestion(example)}
                className={cn(
                  "text-left p-3 rounded-lg text-sm transition-all duration-200",
                  "bg-surface-card text-body border border-theme",
                  "hover:bg-[rgba(0,0,0,0.05)] dark:hover:bg-white/5",
                  "hover:text-body hover:border-foreground",
                  isLoading && "opacity-50 cursor-not-allowed"
                )}
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

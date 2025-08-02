import React, { useState } from "react";
import { motion } from "framer-motion";
import { Query as QueryType } from "@/entities/Query";
import { InvokeLLM } from "@/integrations/Core";
import QueryInput from "../components/query/QueryInput";
import QueryResults from "../components/query/QueryResults";

export default function QueryInterface() {
  const [currentQuery, setCurrentQuery] = useState<QueryType | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmitQuery = async (question: string) => {
    setIsLoading(true);
    const startTime = Date.now();

    try {
      const response = await InvokeLLM(
        `Convert this natural language question to a SQL query and provide sample results. Question: "${question}". 

        Assume we have a typical e-commerce database with tables like users, orders, products, etc. 
        Provide realistic sample data for the results.

        Return the response in the following JSON format:
        {
          "sql_query": "SELECT * FROM ...",
          "results": [array of sample result objects],
          "status": "success",
          "execution_time": number_in_ms
        }`,
        {
          response_json_schema: {
            type: "object",
            properties: {
              sql_query: { type: "string" },
              results: {
                type: "array",
                items: {
                  type: "object",
                  additionalProperties: true
                }
              },
              status: { type: "string", enum: ["success", "error"] },
              execution_time: { type: "number" },
              error_message: { type: "string" }
            },
            required: ["sql_query", "status"]
          }
        }
      );

      const executionTime = Date.now() - startTime;

      const queryData: QueryType = {
        question,
        sql_query: response.sql_query,
        results: response.results || [],
        execution_time: response.execution_time || executionTime,
        status: response.status || "success",
        error_message: response.error_message
      };

      setCurrentQuery(queryData);
    } catch (error) {
      console.error("Error processing query:", error);
      const errorQuery: QueryType = {
        question,
        sql_query: "",
        results: [],
        execution_time: Date.now() - startTime,
        status: "error",
        error_message: "Failed to process your question. Please try again."
      };

      setCurrentQuery(errorQuery);
    }

    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-12"
        >
          <div className="mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-2xl">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full" />
              </motion.div>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
              Ask Your
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                {" "}Database
              </span>
            </h1>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
              Transform natural language questions into powerful SQL queries instantly.
              No SQL knowledge required.
            </p>
          </div>
        </motion.div>

        {/* Query Input */}
        <QueryInput onSubmit={handleSubmitQuery} isLoading={isLoading} />

        {/* Query Results */}
        {(currentQuery || isLoading) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <QueryResults query={currentQuery} isLoading={isLoading} />
          </motion.div>
        )}

        {/* Feature Highlights */}
        {!currentQuery && !isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="grid md:grid-cols-3 gap-6 pt-12"
          >
            {[
              {
                title: "Natural Language Processing",
                description: "Ask questions in plain English, get precise SQL queries",
                icon: "🧠"
              },
              {
                title: "Instant Results",
                description: "See your data immediately with beautiful table formatting",
                icon: "⚡"
              },
              {
                title: "Query History",
                description: "Access and rerun your previous queries anytime",
                icon: "📚"
              }
            ].map((feature, index) => (
              <div key={index} className="bg-white/5 backdrop-blur-xl rounded-xl border border-white/10 p-6 text-center">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-white font-semibold mb-2">{feature.title}</h3>
                <p className="text-slate-400 text-sm">{feature.description}</p>
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
}

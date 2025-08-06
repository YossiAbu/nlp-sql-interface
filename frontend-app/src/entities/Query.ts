export interface Query {
  question: string;
  sql_query: string;
  results: string; // Human-readable answer from LLM
  raw_rows?: Record<string, unknown>[]; // Actual SQL result rows
  execution_time: number;
  status: "success" | "error";
  error_message?: string;
  created_date: string;
}
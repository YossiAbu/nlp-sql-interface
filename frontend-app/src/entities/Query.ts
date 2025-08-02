export interface Query {
  id?: string;
  question: string;
  sql_query: string;
  results: Record<string, any>[];
  execution_time: number;
  status: "success" | "error";
  error_message?: string;
  created_date?: string; // for display in history
}

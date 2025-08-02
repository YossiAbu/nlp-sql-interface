export const InvokeLLM = async (
  prompt: string,
  options?: {
    response_json_schema?: any
  }
): Promise<any> => {
  // Simulate a fake response matching the schema
  return {
    sql_query: "SELECT * FROM users WHERE created_at >= '2024-01-01'",
    results: [
      { id: 1, name: "Alice", created_at: "2024-01-15" },
      { id: 2, name: "Bob", created_at: "2024-02-10" }
    ],
    status: "success",
    execution_time: 123
  }
}

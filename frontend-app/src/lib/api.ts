export async function fetchQuery(question: string) {
  const reponse = await fetch("http://localhost:8000/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!reponse.ok) throw new Error("Query failed");
  return reponse.json();
}

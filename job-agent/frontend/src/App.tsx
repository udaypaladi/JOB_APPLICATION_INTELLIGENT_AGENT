import { useState } from "react";
import UploadPanel from "./components/UploadPanel";
import ApprovalGate from "./components/ApprovalGate";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [agentState, setAgentState] = useState<any>(null);

  async function handleUpload(resumeFile: File, jdText: string) {
    const form = new FormData();
    form.append("resume", resumeFile);
    form.append("jd_text", jdText);
    const res = await fetch(`${API_BASE}/sessions`, { method: "POST", body: form });
    const data = await res.json();
    setSessionId(data.session_id);
    setAgentState(data.state);
  }

  async function handleDecision(status: "approved" | "edited" | "rejected", edits?: object) {
    if (!sessionId) return;
    const form = new FormData();
    form.append("status", status);
    if (edits) form.append("edits", JSON.stringify(edits));
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/decide`, {
      method: "POST",
      body: form,
    });
    const data = await res.json();
    setAgentState(data.state);
  }

  return (
    <main>
      <h1>Job Application Agent</h1>
      {!agentState && <UploadPanel onSubmit={handleUpload} />}
      {agentState?.errors?.length > 0 && (
        <section role="alert">
          <h2>We could not process this application</h2>
          <ul>
            {agentState.errors.map((error: string) => (
              <li key={error}>{error}</li>
            ))}
          </ul>
        </section>
      )}
      {agentState?.drafts && agentState.approval_status === "pending" && (
        <ApprovalGate state={agentState} onDecide={handleDecision} />
      )}
      {agentState?.approval_status && agentState.approval_status !== "pending" && (
        <p>Application {agentState.approval_status}. Check the exports folder.</p>
      )}
    </main>
  );
}

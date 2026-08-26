import { useState } from "react";

export default function ApprovalGate({
  state,
  onDecide,
}: {
  state: any;
  onDecide: (status: "approved" | "edited" | "rejected", edits?: object) => void;
}) {
  const [coverLetter, setCoverLetter] = useState(state.drafts.cover_letter);
  const edited = coverLetter !== state.drafts.cover_letter;

  return (
    <div>
      <h2>Fit score: {state.fit_score.overall_score}/100</h2>
      <p>{state.fit_score.explanation}</p>

      <h3>Gaps</h3>
      <ul>
        {state.gap_analysis.missing_skills.map((s: string) => (
          <li key={s}>{s}</li>
        ))}
      </ul>

      <h3>Cover letter (editable)</h3>
      <textarea
        rows={12}
        value={coverLetter}
        onChange={(e) => setCoverLetter(e.target.value)}
      />

      <h3>Tailored resume bullets</h3>
      {Object.entries(state.drafts.tailored_resume_bullets).map(([section, bullets]) => (
        <div key={section}>
          <strong>{section}</strong>
          <ul>
            {(bullets as string[]).map((b, i) => (
              <li key={i}>{b}</li>
            ))}
          </ul>
        </div>
      ))}

      <h3>Interview prep</h3>
      <ul>
        {state.drafts.interview_questions.map((q: any, i: number) => (
          <li key={i}>
            <strong>[{q.category}]</strong> {q.question}
          </li>
        ))}
      </ul>

      <div style={{ display: "flex", gap: 8 }}>
        <button onClick={() => onDecide("rejected")}>Reject</button>
        <button
          onClick={() =>
            edited
              ? onDecide("edited", { cover_letter: coverLetter })
              : onDecide("approved")
          }
        >
          {edited ? "Approve with edits" : "Approve & export"}
        </button>
      </div>
    </div>
  );
}

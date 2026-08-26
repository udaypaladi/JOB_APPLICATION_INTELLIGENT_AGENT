import { useState } from "react";

export default function UploadPanel({
  onSubmit,
}: {
  onSubmit: (resume: File, jdText: string) => void;
}) {
  const [resume, setResume] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!resume || !jdText.trim()) return;
    setLoading(true);
    await onSubmit(resume, jdText);
    setLoading(false);
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Resume (PDF/DOCX)
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => setResume(e.target.files?.[0] ?? null)}
        />
      </label>
      <label>
        Job description
        <textarea
          rows={10}
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          placeholder="Paste the job description here"
        />
      </label>
      <button type="submit" disabled={loading || !resume || !jdText.trim()}>
        {loading ? "Researching & scoring..." : "Run agent"}
      </button>
    </form>
  );
}

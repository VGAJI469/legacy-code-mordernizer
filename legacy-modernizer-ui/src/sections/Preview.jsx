import { useState } from "react";

export default function Preview() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");

  const handleModernize = async () => {
    const url =
      import.meta.env.VITE_API_URL != null && import.meta.env.VITE_API_URL !== ""
        ? `${import.meta.env.VITE_API_URL.replace(/\/$/, "")}/modernize`
        : "/api/modernize";

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code: input }),
      });

      const data = await res.json();
      if (res.ok) {
        setOutput(data.output || data.modernized_code);
      } else {
        setOutput("❌ Error: " + (data.detail?.error_msg || JSON.stringify(data.detail) || "Unknown error"));
      }
    } catch (err) {
      console.error(err);
      setOutput("❌ Error connecting to backend");
    }
  };

  return (
    <div className="py-20">

      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <p className="text-gray-500 text-sm tracking-widest">
          LIVE PREVIEW
        </p>

        <button
          onClick={handleModernize}
          className="border border-white/10 px-5 py-2 rounded-lg hover:bg-white/5 transition"
        >
          Modernize →
        </button>
      </div>

      {/* Grid */}
      <div className="grid md:grid-cols-2 gap-6">

        {/* INPUT BOX */}
        <div className="rounded-2xl border border-white/10 bg-[#020617] overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-2 border-b border-white/10">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="ml-3 text-sm text-gray-400">legacy.cbl</span>
          </div>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Paste COBOL / Java code..."
            className="w-full h-64 bg-transparent p-4 text-gray-300 outline-none font-mono text-sm"
          />
        </div>

        {/* OUTPUT BOX */}
        <div className="rounded-2xl border border-white/10 bg-[#020617] overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-2 border-b border-white/10">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="ml-3 text-sm text-gray-400">output.py</span>
          </div>

          <pre className="p-4 text-sm text-green-400 font-mono whitespace-pre-wrap">
            {output || '// Click "Modernize →" to see output'}
          </pre>
        </div>

      </div>
    </div>
  );
}
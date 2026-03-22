import { useState } from "react";

const stepsData = [
  { title: "Ingest", desc: "Upload repository" },
  { title: "Parse", desc: "Analyze dependencies" },
  { title: "Optimize", desc: "Context pruning" },
  { title: "Generate", desc: "Modern code output" },
];

export default function Steps() {
  const [active, setActive] = useState(2);

  return (
    <div className="py-16">
      <p className="text-gray-500 text-sm mb-6 tracking-widest">
        HOW IT WORKS
      </p>

      <div className="grid md:grid-cols-4 gap-6">
        {stepsData.map((step, index) => (
          <div
            key={index}
            onMouseEnter={() => setActive(index)}
            className={`p-6 rounded-2xl border cursor-pointer transition duration-300
            ${
              active === index
                ? "bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-400 shadow-[0_0_30px_rgba(34,197,94,0.2)]"
                : "bg-white/5 border-white/10 hover:border-white/20 hover:bg-white/10"
            }`}
          >
            <p className="text-gray-400 text-sm">Step {index + 1}</p>
            <h3 className="text-lg font-semibold mt-2">{step.title}</h3>
            <p className="text-gray-500 text-sm mt-1">{step.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
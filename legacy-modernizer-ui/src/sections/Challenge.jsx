export default function Challenge() {
  return (
    <div className="mt-24">

      {/* Section title */}
      <p className="text-xs text-gray-500 tracking-widest mb-8">
        THE CHALLENGE
      </p>

      {/* Main container */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-8">

        {/* Main text */}
        <h2 className="text-xl md:text-2xl font-medium text-white leading-relaxed max-w-4xl">
          Develop a developer tool that ingests legacy code repositories and
          suggests modern Python/Go equivalents or documentation.
        </h2>

        {/* Cards */}
        <div className="mt-10 grid md:grid-cols-2 gap-6">

          {/* Card 1 */}
          <div className="bg-green-500/10 border border-green-500 rounded-xl p-6">
            <p className="text-xs text-green-400 mb-2 tracking-wider">
              CONTEXT-AWARE
            </p>

            <h3 className="text-lg font-semibold text-white">
              Multi-file Dependencies
            </h3>

            <p className="text-sm text-gray-400 mt-2">
              Handles cross-file references without exceeding standard LLM
              context windows through smart chunking.
            </p>
          </div>

          {/* Card 2 */}
          <div className="bg-red-500/10 border border-red-500 rounded-xl p-6">
            <p className="text-xs text-red-400 mb-2 tracking-wider">
              ACCURACY-FIRST
            </p>

            <h3 className="text-lg font-semibold text-white">
              Hallucination Minimization
            </h3>

            <p className="text-sm text-gray-400 mt-2">
              Strips dead code and noisy comments before inference, reducing
              incorrect suggestions significantly.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}
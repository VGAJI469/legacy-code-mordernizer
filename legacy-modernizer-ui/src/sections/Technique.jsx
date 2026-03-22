export default function Technique() {
  return (
    <div className="mt-24">

      {/* Section title */}
      <p className="text-xs text-gray-500 tracking-widest mb-8">
        REQUIRED TECHNIQUE
      </p>

      {/* Main container */}
      <div className="bg-green-500/10 border border-green-500 rounded-2xl p-8">

        {/* Tag */}
        <p className="text-xs text-green-400 tracking-wider mb-2">
          TECHNIQUE
        </p>

        {/* Title */}
        <h2 className="text-2xl font-semibold text-white">
          Context Optimization
        </h2>

        {/* Description */}
        <p className="text-gray-400 mt-4 max-w-2xl">
          Feed only the relevant function dependencies to the LLM, reducing
          cognitive load on the model and significantly increasing translation
          accuracy.
        </p>

        {/* Stats */}
        <div className="mt-8 flex gap-12 flex-wrap">

          <div>
            <p className="text-green-400 text-2xl font-bold">↓ 60%</p>
            <p className="text-sm text-gray-400">Context size reduced</p>
          </div>

          <div>
            <p className="text-green-400 text-2xl font-bold">↑ 3x</p>
            <p className="text-sm text-gray-400">Accuracy improvement</p>
          </div>

          <div>
            <p className="text-green-400 text-2xl font-bold">~0</p>
            <p className="text-sm text-gray-400">Dead code passed</p>
          </div>

        </div>

      </div>

    </div>
  );
}
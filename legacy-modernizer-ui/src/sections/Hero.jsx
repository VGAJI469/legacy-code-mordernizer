export default function Hero() {
  return (
    <div className="pt-28 pb-20">
      <div className="max-w-3xl">

        <p className="text-[11px] text-gray-500 tracking-[0.25em] mb-6 uppercase">
          Project 4 • Hackathon Challenge
        </p>

        <h1 className="text-[64px] leading-[1.05] font-semibold tracking-tight text-white">
          Legacy Code <br />
          <span className="bg-gradient-to-r from-emerald-300 via-green-400 to-emerald-500 bg-clip-text text-transparent">
            Modernization
          </span>{" "}
          Engine
        </h1>

        <p className="mt-6 text-[16px] leading-7 text-gray-400 max-w-[650px]">
          An AI-powered developer tool that ingests legacy COBOL & Java
          repositories and generates modern Python/Go equivalents — without
          hallucinating.
        </p>

        <div className="mt-10 flex gap-4">
          <button className="bg-gradient-to-r from-green-400 to-emerald-500 text-black font-medium px-6 py-3 rounded-xl shadow-[0_0_30px_rgba(34,197,94,0.4)] hover:scale-[1.02] transition">
            View Solution →
          </button>

          <button className="border border-white/10 px-6 py-3 rounded-xl text-gray-300 hover:bg-white/5 transition">
            Read Documentation
          </button>
        </div>

      </div>
    </div>
  );
}
import Hero from "./sections/Hero";
import Steps from "./sections/Steps";
import Challenge from "./sections/Challenge";
import Technique from "./sections/Technique";
import Preview from "./sections/Preview";

function App() {
  return (
    <div className="max-w-6xl mx-auto px-6 md:px-12">
      <Hero />
      <Steps />
      <Challenge />
      <Technique />
      <Preview />
    </div>
  );
}

export default App;
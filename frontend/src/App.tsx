import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Daily from "./components/Daily";
import Weekly from "./components/Weekly";
import Monthly from "./components/Monthly";


export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <div className="pt-20">  {/* Space below fixed nav */}
        <Routes>
          <Route path="/" element={<Daily />} />
          <Route path="/daily" element={<Daily />} />
          <Route path="/weekly" element={<Weekly />} />
          <Route path="/monthly" element={<Monthly />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import CollegeGuide from "./components/CollegeGuide";
import Chatbot from "./components/Chatbot";
import About from "./components/About";
import Features from "./components/Features";
import Contact from "./components/Contact";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<CollegeGuide />}>
          <Route index element={<MainContent />} />
          <Route path="about" element={<About />} />
          <Route path="features" element={<Features />} />
          <Route path="contact" element={<Contact />} />
          <Route path="chat" element={<Chatbot />} />
        </Route>
      </Routes>
    </Router>
  );
}

// Since MainContent is defined in CollegeGuide, we'll need to import or define it here
const MainContent = () => {
  // This should match the MainContent in your CollegeGuide component
  return null; // Placeholder - you'll want to copy over the actual implementation
};

export default App;
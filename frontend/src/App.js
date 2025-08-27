import React, { useEffect, useState } from 'react';
import './App.css';

const App = () => {
  const [showSections, setShowSections] = useState([false, false]);

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const windowHeight = window.innerHeight;

      const section1 = document.querySelector(".image-section:nth-of-type(1)");
      const section2 = document.querySelector(".image-section:nth-of-type(2)");

      if (section1 && scrollY + windowHeight > section1.offsetTop) {
        setShowSections((prev) => [true, prev[1]]);
      }
      if (section2 && scrollY + windowHeight > section2.offsetTop) {
        setShowSections((prev) => [prev[0], true]);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="app-container">
      {/* Navbar */}
      <nav className="navbar">
        <a href="#historical-trends">Historical Trends</a>
        <a href="#prediction-model">Prediction Model</a>
      </nav>

      <header className="header">
        <h1>🌊 Sea Level Rising Prediction</h1>
      </header>

      <main className="content">
        {/* Historical Trends */}
        <section id="historical-trends" className={`image-section ${showSections[0] ? 'visible' : ''}`}>
          <h2>📈 Historical Trends</h2>
          <img src="/Figure_1.png" alt="Sea Level Plot" className="plot-img" />
          <img src="/Figure_2.png" alt="Scatter Plot" className="plot-img" />
        </section>

        {/* Prediction Model */}
        <section id="prediction-model" className={`image-section ${showSections[1] ? 'visible' : ''}`}>
          <h2>🔮 Prediction Model</h2>
          <img src="/prediction.png" alt="Prediction Plot" className="plot-img" />
        </section>
      </main>

      <footer className="footer">
        <p>© 2025 Sea Level Analysis Project</p>
      </footer>
    </div>
  );
};

export default App;

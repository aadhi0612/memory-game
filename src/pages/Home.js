import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Home.css';

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <h1>Memory Game</h1>
      <div className="menu-container">
        <button className="menu-button" onClick={() => navigate('/game')}>
          Start New Game
        </button>
      </div>
    </div>
  );
}

export default Home; 
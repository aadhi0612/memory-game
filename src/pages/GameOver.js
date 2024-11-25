import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

function GameOver() {
  const location = useLocation();
  const navigate = useNavigate();
  const { score, moves } = location.state || { score: 0, moves: 0 };

  return (
    <div className="game-over-container">
      <h1>Game Complete!</h1>
      <div className="final-stats">
        <p>Final Score: {score}</p>
        <p>Total Moves: {moves}</p>
      </div>
      <div className="action-buttons">
        <button onClick={() => navigate('/game')}>Play Again</button>
        <button onClick={() => navigate('/')}>Main Menu</button>
      </div>
    </div>
  );
}

export default GameOver; 
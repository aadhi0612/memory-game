import React from 'react';

function GameStats({ moves, score, matchedPairs }) {
  return (
    <div className="game-stats">
      <div className="stat-box">
        <span className="stat-label">Moves</span>
        <span className="stat-value">{moves}</span>
      </div>
      <div className="stat-box">
        <span className="stat-label">Score</span>
        <span className="stat-value">{score}</span>
      </div>
      <div className="stat-box">
        <span className="stat-label">Pairs</span>
        <span className="stat-value">{matchedPairs}</span>
      </div>
    </div>
  );
}

export default GameStats; 
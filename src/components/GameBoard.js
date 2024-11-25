import React from 'react';
import Card from './Card';

function GameBoard({ cards, onCardClick, isLoading, selectedCards }) {
  if (isLoading && cards.length === 0) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Setting up your game...</p>
      </div>
    );
  }

  return (
    <div className="card-grid">
      {cards.map((card) => (
        <Card 
          key={card.id}
          card={card}
          onClick={() => onCardClick(card)}
          isSelected={selectedCards.includes(card)}
        />
      ))}
    </div>
  );
}

export default GameBoard; 
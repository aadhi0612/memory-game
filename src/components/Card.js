import React from 'react';

function Card({ card, onClick, isSelected }) {
  const handleClick = (e) => {
    e.preventDefault();
    onClick();
  };

  return (
    <div
      className={`card ${isSelected ? 'flipped' : ''} ${card.matched ? 'matched' : ''}`}
      onClick={handleClick}
    >
      <div className="card-inner">
        <div className="card-front">
          <div className="card-pattern"></div>
        </div>
        <div className="card-back">
          {card.image_url && (
            <img 
              src={card.image_url} 
              alt={card.theme} 
              loading="lazy"
              onError={(e) => {
                console.error('Image load error:', e);
                e.target.src = 'placeholder.png'; // Add a placeholder image
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default Card; 
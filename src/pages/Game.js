import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import GameBoard from '../components/GameBoard';
import GameStats from '../components/GameStats';
import '../styles/Game.css';

const CARDS_API = 'https://ncccws8p5d.execute-api.us-east-1.amazonaws.com/Dev/cards';
const GAME_API = 'https://ncccws8p5d.execute-api.us-east-1.amazonaws.com/Dev/game';

function Game() {
  const navigate = useNavigate();
  const [gameState, setGameState] = useState({
    cards: [],
    moves: 0,
    score: 0,
    matchedPairs: 0,
    isLoading: false,
    error: null,
    gameId: null,
    selectedCards: []
  });

  const startNewGame = async () => {
    try {
      setGameState(prev => ({ ...prev, isLoading: true, error: null, cards: [] }));
      
      // Step 1: Generate cards
      const cardsResponse = await fetch(CARDS_API, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ number_of_pairs: 4 })
      });

      const cardsData = await cardsResponse.json();
      console.log('Raw cards response:', cardsData);

      // Parse the nested JSON response
      let parsedCards;
      try {
        parsedCards = JSON.parse(cardsData.body).cards;
      } catch (e) {
        console.error('Error parsing cards:', e);
        throw new Error('Invalid card data received');
      }

      console.log('Parsed cards:', parsedCards);

      // Step 2: Start game with generated cards
      const gameResponse = await fetch(GAME_API, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'start_game',
          cards: parsedCards
        })
      });

      const gameData = await gameResponse.json();
      console.log('Game response:', gameData);

      // Update game state with new data
      setGameState({
        cards: parsedCards,
        gameId: gameData.game_id,
        moves: 0,
        score: 0,
        matchedPairs: 0,
        selectedCards: [],
        isLoading: false,
        error: null
      });

    } catch (error) {
      console.error('Error in startNewGame:', error);
      setGameState(prev => ({
        ...prev,
        error: error.message,
        isLoading: false
      }));
    }
  };

  useEffect(() => {
    startNewGame();
  }, []);

  const handleCardClick = async (card) => {
    if (
      gameState.isLoading ||
      gameState.selectedCards.length === 2 ||
      gameState.selectedCards.includes(card) ||
      card.matched
    ) {
      return;
    }

    const newSelectedCards = [...gameState.selectedCards, card];
    setGameState(prev => ({ ...prev, selectedCards: newSelectedCards }));

    if (newSelectedCards.length === 2) {
      setGameState(prev => ({ ...prev, isLoading: true }));
      try {
        const response = await fetch(GAME_API, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            action: 'check_match',
            game_id: gameState.gameId,
            card1_id: newSelectedCards[0].id,
            card2_id: newSelectedCards[1].id
          })
        });

        if (!response.ok) {
          throw new Error('Failed to check match');
        }

        const data = await response.json();
        console.log('Match check response:', data);

        setGameState(prev => ({
          ...prev,
          cards: data.game_state.cards,
          moves: data.game_state.moves,
          matchedPairs: data.game_state.matched_pairs,
          score: prev.score + (data.is_match ? 100 : 0),
          selectedCards: [],
          isLoading: false
        }));

        if (data.game_state.status === 'completed') {
          setTimeout(() => {
            navigate('/game-over', {
              state: {
                score: gameState.score,
                moves: gameState.moves
              }
            });
          }, 1000);
        }
      } catch (error) {
        console.error('Error checking match:', error);
        setGameState(prev => ({
          ...prev,
          error: error.message,
          isLoading: false,
          selectedCards: []
        }));
      }
    }
  };

  return (
    <div className="game-page">
      <div className="game-header">
        <h1>Memory Game</h1>
        <button 
          className="game-button"
          onClick={startNewGame}
          disabled={gameState.isLoading}
        >
          {gameState.isLoading ? 'Loading...' : 'New Game'}
        </button>
      </div>
      <GameStats 
        moves={gameState.moves}
        score={gameState.score}
        matchedPairs={gameState.matchedPairs}
      />
      {gameState.error && (
        <div className="error-message">{gameState.error}</div>
      )}
      {gameState.isLoading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Setting up your game...</p>
        </div>
      ) : (
        <GameBoard 
          cards={gameState.cards}
          onCardClick={handleCardClick}
          isLoading={gameState.isLoading}
          selectedCards={gameState.selectedCards}
        />
      )}
    </div>
  );
}

export default Game; 
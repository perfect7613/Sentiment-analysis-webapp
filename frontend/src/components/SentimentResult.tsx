import React from 'react';

interface LabelScoreType {
  label: string;
  score: number;
}

interface SentimentResultType {
  sentiment: string;
  score: number;
  language: string | null;
  allScores?: LabelScoreType[];
}

interface SentimentResultProps {
  result: SentimentResultType;
}

const SentimentResult: React.FC<SentimentResultProps> = ({ result }) => {
  const getSentimentEmoji = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      default: return '😐';
    }
  };

  const getSentimentClass = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'positive';
      case 'negative': return 'negative';
      default: return 'neutral';
    }
  };

  const confidencePercent = Math.round(result.score * 100);
  const sentimentClass = getSentimentClass(result.sentiment);
  const emoji = getSentimentEmoji(result.sentiment);

  return (
    <div className="result-container">
      <div className="result-title">
        <h2>Analysis Result</h2>
      </div>

      <div className={`sentiment-card ${sentimentClass}`}>
        <div className="sentiment-result">
          <div className="sentiment-label">
            <span>{emoji} {result.sentiment.charAt(0).toUpperCase() + result.sentiment.slice(1)}</span>
          </div>
          <div className="sentiment-score">
            <span>{confidencePercent}% confidence</span>
          </div>
        </div>
        
        <div className="confidence-bar">
          <div 
            className={`confidence-fill ${sentimentClass}`} 
            style={{ width: `${confidencePercent}%` }}
          />
        </div>
      </div>

      {result.language && (
        <div className="language-info">
          <span>Detected Language: <strong>{result.language}</strong></span>
        </div>
      )}

      {result.allScores && result.allScores.length > 0 && (
        <div className="scores-distribution">
          <h3>Label Distribution</h3>
          {result.allScores.map((item, index) => (
            <div key={index} className="score-item">
              <span>{item.label}:</span>
              <div className="score-bar">
                <div 
                  className="score-bar-fill" 
                  style={{ width: `${item.score * 100}%` }}
                />
              </div>
              <span>{(item.score * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SentimentResult;

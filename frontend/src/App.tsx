import React, { useState } from 'react';
import {
  ApolloClient,
  InMemoryCache,
  ApolloProvider,
  gql,
  useMutation,
} from '@apollo/client';
import './App.css';
import LoadingSpinner from './components/LoadingSpinner';
import SentimentResult from './components/SentimentResult';


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

interface AnalyzeSentimentResponse {
  analyzeSentiment: {
    result: SentimentResultType;
  };
}

interface AnalyzeSentimentVariables {
  text: string;
}


const client = new ApolloClient({
  uri: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/graphql',
  cache: new InMemoryCache(),
  headers: {
    'X-API-Key': import.meta.env.VITE_API_KEY ?? 'default_api_key',
  },
});


const ANALYZE_SENTIMENT = gql`
  mutation AnalyzeSentiment($text: String!) {
    analyzeSentiment(text: $text) {
      result {
        sentiment
        score
        language
        allScores {
          label
          score
        }
      }
    }
  }
`;


const App: React.FC = () => {
  return (
    <ApolloProvider client={client}>
      <div className="App">
        <header className="App-header">
          <h1>Multilingual Sentiment Analysis</h1>
          <p>Analyze the sentiment of your text in multiple languages</p>
        </header>
        <SentimentAnalyzer />
      </div>
    </ApolloProvider>
  );
};



const SentimentAnalyzer: React.FC = () => {
  const [text, setText] = useState('');
  const [sentiment, setSentiment] = useState<SentimentResultType | null>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [charCount, setCharCount] = useState(0);

  const [analyzeSentiment] = useMutation<AnalyzeSentimentResponse, AnalyzeSentimentVariables>(
    ANALYZE_SENTIMENT,
    {
      onCompleted: (data) => {
        setSentiment(data.analyzeSentiment.result);
        setIsLoading(false);
      },
      onError: (err) => {
        setError(`Error: ${err.message}`);
        setIsLoading(false);
      },
    }
  );

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }
    setIsLoading(true);
    setError('');
    setSentiment(null);
    analyzeSentiment({ variables: { text } });
  };


  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    setCharCount(e.target.value.length);
  };

  const sampleTexts = [
    'I love using AI-powered tools!',
    'I hate bugs and errors!',
    'मुझे दुःख हो रहा है',
    'I feel so sad today...',
    'This is fine, I guess.',
    'このレストランの料理は本当に美味しいです！'
  ];

  const handleSampleClick = (sample: string) => {
    setText(sample);
    setCharCount(sample.length);
  };

  return (
    <div className="analyzer-container">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="text">Enter text to analyze:</label>
          <textarea
            id="text"
            value={text}
            onChange={handleTextChange}
            rows={5}
            placeholder="Type or paste your text here..."
          />
          <div className="character-count">{charCount} characters</div>
        </div>
        <button type="submit" className="button" disabled={isLoading || !text.trim()}>
          {isLoading ? 'Analyzing...' : 'Analyze Sentiment'}
        </button>
      </form>

      <div className="sample-texts">
        <h3>Try a sample:</h3>
        <div className="samples-grid">
          {sampleTexts.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => handleSampleClick(sample)}
              className="sample-button"
            >
              {sample}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {isLoading && (
        <div className="loading-indicator">
          <LoadingSpinner />
          <span>Analyzing your text...</span>
        </div>
      )}

      {sentiment && <SentimentResult result={sentiment} />}
    </div>
  );
};

export default App;

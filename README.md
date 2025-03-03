Sentiment Analysis Application

A full-stack web application that provides sentiment analysis for text in multiple languages. The application can detect whether text has positive, negative, or neutral sentiment and provides confidence scores for each analysis.

## Features

- Multilingual sentiment analysis using a pre-trained deep learning model
- Support for analyzing text in various languages 
- Real-time sentiment analysis with confidence scores
- Detailed breakdown of label distribution
- Sample texts for quick testing
- History tracking of previously analyzed texts
- Docker containerization for easy deployment
- On-premises deployment ready (no external API calls after setup)

## Architecture

The application consists of two primary components:

1. **Backend (Python/FastAPI)**:
   - GraphQL API built with FastAPI and Graphene
   - Uses a pre-trained Hugging Face model for sentiment analysis
   - Stores analysis history in SQLite database

2. **Frontend (React/TypeScript)**:
   - Modern React application with TypeScript
   - Apollo Client for GraphQL communication
   - Responsive design that works across devices
   - Interactive UI with real-time feedback

## Installation and Setup

### Using Docker (Recommended)

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd sentiment-analysis
   ```

2. Create a `.env` file in the root directory with the following variables:
   ```
   HF_AUTH_TOKEN=your_hugging_face_token
   API_KEY=your_chosen_api_key
   ```

3. Build and start the containers:
   ```sh
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000/graphql

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```sh
   cd backend
   ```

2. Create a virtual environment:
   ```sh
   python -m venv tool
   ```

3. Activate the virtual environment:
   - Windows: `.\tool\Scripts\activate.bat`
   - macOS/Linux: `source tool/Scripts/activate`

4. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

5. Create a `.env` file with:
   ```
   HF_AUTH_TOKEN=your_hugging_face_token
   API_KEY=your_chosen_api_key
   ```

6. Run the backend:
   ```sh
   python main.py
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```

2. Install dependencies:
   ```sh
   npm install
   ```

3. Create a `.env` file with:
   ```
   VITE_API_URL=http://localhost:8000/graphql
   VITE_API_KEY=your_chosen_api_key
   ```

4. Start the development server:
   ```sh
   npm run dev
   ```

## On-Premises Deployment Notes

This application is designed to run in an on-premises environment:

- The Docker setup pre-downloads the Hugging Face model during image build
- All dependencies are included in the Docker images
- No external API calls are made after initial setup
- Data is stored in a local SQLite database


## Project Structure

```
├── backend/                # Python/FastAPI backend
│   ├── main.py             # Main application file
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend Docker configuration
├── frontend/               # React/TypeScript frontend
│   ├── src/                # Source code
│   ├── public/             # Static assets
│   └── Dockerfile          # Frontend Docker configuration
└── docker-compose.yml      # Docker Compose configuration
```

## Usage

1. Enter text in the input area or select a sample text
2. Click "Analyze Sentiment"
3. View the sentiment analysis results, including:
   - Overall sentiment (positive, negative, or neutral)
   - Confidence score
   - Distribution of sentiment scores across labels

The application provides visual indicators (colors and emoji) to help quickly identify the sentiment of the analyzed text.

---

This project uses the [multilingual-sentiment-analysis](https://huggingface.co/tabularisai/multilingual-sentiment-analysis) model from Hugging Face.
# AI Widget Chat

An AI-powered chat application with dynamic widget rendering based on user queries. The application uses Google's VertexAI for intelligent responses and automatically creates relevant widgets for weather, stocks, news, and time information.

## Features

- 🤖 **AI-Powered Chat**: Intelligent responses using Google VertexAI with function calling
- 🎛️ **Dynamic Widgets**: Automatic widget creation based on conversation context
- 🌤️ **Weather Widget**: Current weather information for any location
- 📈 **Stock Widget**: Real-time stock prices and market data
- 📰 **News Widget**: Latest news articles on any topic
- ⏰ **Clock Widget**: Current time for different timezones
- 💬 **Chat Interface**: Modern, responsive chat UI with session management
- 🔄 **Real-time Updates**: Automatic widget data refresh
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Architecture

### Backend (Python + FastAPI)

- **FastAPI**: High-performance async API framework
- **VertexAI**: Google's LLM with function calling capabilities
- **SQLAlchemy**: Database ORM with SQLite
- **Pydantic**: Data validation and serialization
- **External APIs**: Integration with OpenWeatherMap, Alpha Vantage, and NewsAPI

### Frontend (Angular)

- **Angular 17**: Modern web framework with standalone components
- **Angular Material**: UI component library
- **TypeScript**: Type-safe development
- **Responsive Design**: Mobile-first approach

## How to run in local

### Backend:

```bash
 cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frondend

```bash
cd frontend
npm install
npm start
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- Google Cloud Platform account (for VertexAI)
- API keys for external services (optional - mock data available)

### Backend Setup

1. **Clone and navigate to the project:**

   ```bash
   cd AI_WidgetChat/backend
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Start the backend server:**

   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   Or use the startup script:

   ```bash
   python ../start_backend.py
   ```

### Frontend Setup

1. **Navigate to frontend directory:**

   ```bash
   cd ../frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm start
   ```

4. **Open your browser:**
   Navigate to `http://localhost:4200`

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./database/ai_widget_chat.db

# Google Cloud / VertexAI Configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
VERTEX_AI_LOCATION=us-central1

# External API Keys (Optional - mock data available)
OPENWEATHER_API_KEY=your-openweathermap-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
NEWS_API_KEY=your-newsapi-key

# Application Settings
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
CORS_ORIGINS=["http://localhost:4200", "http://127.0.0.1:4200"]

# Widget Settings
WIDGET_CACHE_TTL=300
MAX_WIDGETS_PER_RESPONSE=5
```

### Google Cloud Setup

1. **Create a Google Cloud Project**
2. **Enable the Vertex AI API**
3. **Create a service account** with Vertex AI permissions
4. **Download the service account key** and set the path in `GOOGLE_APPLICATION_CREDENTIALS`

### External API Keys (Optional)

The application works with mock data if API keys are not provided, but for production use, you'll want to set up:

- **OpenWeatherMap**: Free tier available at [openweathermap.org](https://openweathermap.org/api)
- **Alpha Vantage**: Free tier available at [alphavantage.co](https://www.alphavantage.co/support/#api-key)
- **NewsAPI**: Free tier available at [newsapi.org](https://newsapi.org/register)

## Usage

### Chat Interface

1. **Start a conversation**: Type any message in the chat input
2. **Ask about weather**: "What's the weather in New York?"
3. **Check stock prices**: "What's the current price of AAPL?"
4. **Get news**: "Show me the latest technology news"
5. **Check time**: "What time is it in Tokyo?"

### Widget Features

- **Automatic Creation**: Widgets are created automatically based on your questions
- **Interactive Actions**: Each widget has refresh, configure, and fullscreen actions
- **Real-time Updates**: Widget data refreshes automatically
- **Responsive Design**: Widgets adapt to different screen sizes

## API Documentation

Once the backend is running, visit:

- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/v1/chat/message` - Send a chat message
- `GET /api/v1/chat/sessions` - Get chat sessions
- `GET /api/v1/widgets/types` - Get available widget types
- `POST /api/v1/widgets/data` - Get widget data

## Development

### Project Structure

```
AI_WidgetChat/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   ├── widgets/       # Widget implementations
│   │   └── main.py        # FastAPI app
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/  # Angular components
│   │   │   ├── services/    # Angular services
│   │   │   └── models/      # TypeScript interfaces
│   │   └── styles.css
│   └── package.json
└── README.md
```

### Adding New Widgets

1. **Create widget class** in `backend/app/widgets/`
2. **Extend BaseWidget** and implement required methods
3. **Add to WidgetService** registry
4. **Create Angular component** in `frontend/src/app/components/widgets/`
5. **Update widget component** to handle new type

### Backend Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest
```

### Frontend Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Deployment

### Backend Deployment

The FastAPI backend can be deployed to:

- **Heroku**: Use the included `Procfile`
- **Railway**: Connect your GitHub repository
- **Google Cloud Run**: Use the included Dockerfile
- **AWS**: Deploy to ECS or Lambda

### Frontend Deployment

The Angular frontend can be deployed to:

- **Netlify**: Connect your GitHub repository
- **Vercel**: Deploy with `npm run build`
- **AWS S3**: Upload the `dist/` folder
- **Firebase Hosting**: Use Firebase CLI

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -m "Add feature"`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the example configurations

## Roadmap

- [ ] WebSocket support for real-time chat
- [ ] Widget customization interface
- [ ] Additional widget types (maps, charts, etc.)
- [ ] User authentication and personalization
- [ ] Widget sharing and collaboration
- [ ] Mobile app (React Native)
- [ ] Advanced analytics and insights

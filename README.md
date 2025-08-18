# DR Reviewer - AI-Powered Design Review System

An AI-powered system for evaluating Senior Software Engineers aspiring to become Lead Software Engineers, ensuring fair, secure, and efficient assessments while reducing dependency on manual architect reviews.

## 🎯 Business Goals

- **Efficiency**: Reduce architect evaluation time by 60–70%
- **Fairness**: Minimize human bias through AI-driven scoring
- **Standardization**: Ensure consistent evaluation criteria across all candidates
- **Security**: Guarantee compliance with GDPR and organizational data policies
- **Scalability**: Support increasing candidate volume without additional human load

## 🏗️ Current Architecture

### Tech Stack
- **Backend**: Django 5.2.4 + Django REST Framework
- **Database**: SQLite (development)
- **Task Queue**: Celery + Redis
- **AI Engine**: Google Gemini API (gemini-2.0-flash-001)
- **Documentation**: drf-yasg (Swagger/OpenAPI)

### Core Components
- **Candidate Management**: Store candidate information and track progress
- **Design Review Processing**: Upload and analyze PDF documents
- **AI Question Generation**: Generate 5-10 technical questions using Gemini
- **Evaluation System**: Score candidates across 4 key dimensions
- **Background Processing**: Async PDF analysis and evaluation

## 📋 Current Features

### ✅ Implemented
- PDF document upload and storage
- AI-powered question generation (5-10 questions per review)
- Candidate response collection
- Automated evaluation with detailed feedback
- RESTful API with comprehensive endpoints
- Background task processing with Celery
- Structured AI responses using Pydantic models

### ❌ Missing (Per Specification)
- Next.js frontend application
- WebRTC video recording for candidate responses
- Speech-to-text transcription (Google STT/Whisper)
- Authentication system (OAuth2/JWT + MFA)
- File encryption (AES-256)
- Analytics dashboard and reporting
- MongoDB integration option

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Redis server
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dr-reviewer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (CRITICAL)
   ```bash
   # Create .env file or set environment variables
   export SECRET_KEY="your-django-secret-key"
   export GEMINI_API_KEY="your-gemini-api-key"
   export DEBUG=True
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start Redis server**
   ```bash
   redis-server
   ```

7. **Start Celery worker** (new terminal)
   ```bash
   celery -A dr_reviewer worker -l info
   ```

8. **Start Django development server**
   ```bash
   python manage.py runserver
   ```

## 📚 API Documentation

Visit `http://localhost:8000/swagger/` for interactive API documentation.

### Key Endpoints

#### Candidates
- `GET /api/candidates/` - List all candidates
- `POST /api/candidate/` - Create new candidate

#### Design Reviews
- `POST /api/design-review/` - Submit design review with PDFs
- `GET /api/design-review/{id}/` - Get design review details
- `GET /api/design-review/{id}/questions/` - Get generated questions
- `POST /api/design-review/{id}/questions/answer/` - Submit all answers
- `POST /api/question/{id}/answer/` - Answer single question
- `POST /api/design-review/{id}/evaluate/` - Trigger evaluation
- `GET /api/design-review/{id}/evaluation/` - Get evaluation results

## 🔄 System Workflow

1. **Submit Design Review**: Candidate uploads PDF documents with design details
2. **AI Question Generation**: System analyzes documents and generates 5-10 technical questions
3. **Answer Collection**: Candidate provides answers to generated questions
4. **AI Evaluation**: System evaluates responses across 4 dimensions
5. **Results**: Detailed scoring and feedback provided

## 📊 Evaluation Dimensions

The system evaluates candidates across 4 key areas:

1. **Technical Depth** (1-5): Understanding of technical concepts and application
2. **System Design** (1-5): Architecture structure, modularity, and scalability
3. **Tradeoff Reasoning** (1-5): Ability to identify and communicate trade-offs
4. **Ownership & Accountability** (1-5): Taking responsibility and adaptability

## 🗂️ Project Structure

```
dr-reviewer/
├── api/                    # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # API endpoints
│   ├── tasks.py           # Celery background tasks
│   ├── serializers.py     # DRF serializers
│   └── gemini_models.py   # Pydantic models for AI
├── dr_reviewer/           # Django project settings
├── media/                 # Uploaded files (gitignored)
├── staticfiles/          # Static files (gitignored)
├── requirements.txt      # Python dependencies
└── manage.py            # Django management script
```

## 🔧 Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Install development tools
pip install black isort flake8 mypy

# Format code
black .
isort .

# Lint code
flake8 .
```

### Database Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 🚨 Security Notes

**WARNING**: This is a development version with critical security gaps:

- API keys are currently hardcoded (move to environment variables)
- No authentication system implemented
- Files stored unencrypted
- Django secret key exposed

**Before production deployment**:
1. Implement JWT authentication with MFA
2. Add AES-256 file encryption
3. Set up proper environment variable management
4. Enable HTTPS and security headers
5. Configure GDPR-compliant data handling

## 🔮 Future Roadmap

### Phase 1: Security & Authentication
- [ ] JWT authentication system
- [ ] Multi-factor authentication (MFA)
- [ ] File encryption (AES-256)
- [ ] Environment variable management

### Phase 2: User Experience
- [ ] Next.js frontend application
- [ ] WebRTC video recording
- [ ] Real-time speech transcription
- [ ] Responsive design

### Phase 3: Analytics & Reporting
- [ ] Analytics dashboard
- [ ] Trend analysis
- [ ] Performance metrics
- [ ] Admin panel

### Phase 4: Advanced Features
- [ ] MongoDB integration
- [ ] Vector database for semantic search
- [ ] Advanced AI prompting with Langchain
- [ ] Multi-language support

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/swagger/`
2. Review the troubleshooting section below
3. Create an issue in the repository

## 🔍 Troubleshooting

### Common Issues

**Celery not starting**: Ensure Redis is running and accessible
**PDF processing fails**: Check Gemini API key is set correctly
**Database errors**: Run `python manage.py migrate`
**Import errors**: Ensure virtual environment is activated

### Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-django-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
DEBUG=True
REDIS_URL=redis://localhost:6379/0
```

---

**Last Updated**: December 2024  
**Version**: 0.4.0 (MVP - Core Features Implemented)

# Knowledge Base Project

This repository contains a scalable Knowledge Base system that integrates web scraping, data cleaning, categorization, and vector similarity search for machine learning (ML) and artificial intelligence (AI) content. The project uses technologies like Flask, Scrapy, Milvus, and Redis to provide an end-to-end solution for collecting, storing, and querying data.

---

## Features

- **Web Scraping**: Automated article collection from predefined sources using Scrapy.
- **Data Cleaning**: Clean and normalize text data for better analysis.
- **Categorization**: Classify content into predefined ML/AI categories using zero-shot classification models.
- **Vector Similarity Search**: Store and retrieve documents using vector embeddings with Milvus.
- **Interactive Web Interface**: Query and interact with the knowledge base via a user-friendly web app.
- **Microservices Architecture**: Deployed using Docker and Docker Compose for seamless scaling.

---

## Directory Structure

```
artpedro-knowledge_base_project/
├── app/                # Core application code
│   ├── cleaner/        # Text cleaning utilities
│   ├── embeddings/     # Vector embeddings generation
│   ├── milvus_handler/ # Milvus database interaction
│   ├── organizer/      # Content categorization
│   ├── scraper/        # Web scraping using Scrapy
│   ├── worker/         # Asynchronous task processing
│   ├── templates/      # HTML templates for Flask
│   ├── retrieval.py    # Query and retrieval logic
│   ├── routes.py       # API routes for Flask
├── tests/              # Unit tests for all components
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker setup for the Flask app
├── docker-compose.yml  # Multi-container setup
└── run.py              # Flask application entry point
```

---

## Installation

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Redis & Milvus installed (or use the provided `docker-compose.yml`)

### Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/username/knowledge_base_project.git
   cd knowledge_base_project
   ```

2. **Environment Variables**:
   Create a `.env` file in the project root to define your environment variables:
   ```plaintext
   MILVUS_HOST=standalone
   MILVUS_PORT=19530
   REDIS_HOST=redis
   REDIS_PORT=6379
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Services**:
   Run the app and its dependencies using Docker Compose:
   ```bash
   docker-compose up --build
   ```

5. **Access the Application**:
   Visit the web interface at `http://localhost:5000`.

---

## Usage

### Web Interface

- **Home Page**: Displays key functionalities of the application.
- **Health Check**: Verify the application's health and dependencies.
- **Query**: Ask questions or search the knowledge base.
- **Scraper Trigger**: Start the web scraping process for new data.

### API Endpoints

1. **Health Check**: `GET /health`
   - Verify the health of the application.
2. **Trigger Scraper**: `POST /scrape`
   - Trigger a scraping job with an optional `url`.
3. **Query**: `POST /query`
   - Query the knowledge base with JSON payload: `{"query": "Your question"}`.

---

## Testing

Run the unit tests using `unittest`:
```bash
python -m unittest discover -s tests
```

---

## Deployment

### Docker Compose

Use the provided `docker-compose.yml` to deploy the application along with its dependencies:
```bash
docker-compose up -d
```

### Kubernetes (Optional)

For production-grade deployment, you can extend the Docker configuration for Kubernetes using Helm charts or other orchestration tools.

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of your feature"
   ```
4. Push to your branch and open a Pull Request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments

- [Milvus](https://milvus.io/) for vector similarity search.
- [Scrapy](https://scrapy.org/) for powerful web scraping.
- [OpenAI](https://openai.com/) for the GPT API.
- [Redis](https://redis.io/) for job queue management.

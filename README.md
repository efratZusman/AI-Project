# AI Guard – Gmail Communication Risk Analysis System

AI Guard is a production-level AI-assisted system designed to analyze email content before sending, with the goal of preventing miscommunication, escalation, and unprofessional tone. The system integrates rule-based natural language processing with large language model (LLM) capabilities provided by the Google Gemini API. The solution is implemented as a Chrome Extension frontend combined with a FastAPI backend, fully containerized and supported by an automated CI/CD pipeline.

The project was developed as a final academic project and emphasizes real-world engineering practices, responsible AI usage, automated testing, and DevOps principles.

## Project Motivation

Email communication often contains implicit emotional cues, pressure, or unintended escalation that may negatively affect professional interactions. AI Guard addresses this challenge by providing real-time analysis of outgoing email messages and offering actionable feedback before the message is sent. The system is designed to assist users in maintaining clear, respectful, and professional communication.

## System Architecture

The system follows a client–server architecture. The frontend is implemented as a Chrome Extension integrated directly into the Gmail user interface. The extension extracts the email subject and body and sends them to a backend service via HTTP.

The backend, implemented using FastAPI in Python, performs a multi-stage analysis. First, a deterministic lexicon-based analysis is applied to detect pressure, escalation, emotional language, or accusations. Only when predefined risk conditions are met does the system invoke the Gemini API for deeper semantic analysis and message rewriting. If the AI service is unavailable, the system gracefully falls back to rule-based analysis without failure.

## Technology Stack

The backend is developed in Python 3.11 using the FastAPI framework. It is responsible for business logic, validation, AI orchestration, and response generation. Automated testing is implemented using Pytest and pytest-cov. The backend is fully containerized using Docker and orchestrated locally with Docker Compose.

The frontend is implemented as a Chrome Extension using standard web technologies, including HTML, CSS, and Vanilla JavaScript, together with Chrome Extension APIs. This approach follows industry standards for browser extensions and avoids unnecessary complexity introduced by single-page application frameworks.

The CI/CD pipeline is implemented using Jenkins and Docker Hub. Jenkins executes automated tests, generates coverage reports, builds Docker images, and publishes artifacts in a reproducible and deterministic manner.

## Testing Strategy

The project includes a comprehensive automated testing strategy that demonstrates engineering maturity and adherence to best practices.

Unit tests focus on pure business logic and are fully isolated from external dependencies. All interactions with the Gemini API are mocked to ensure deterministic and fast execution. Unit tests validate lexicon-based risk detection, decision flow logic, JSON extraction robustness, and fallback behavior when AI services are unavailable.

Integration tests validate the interaction between FastAPI routes, request validation, and response serialization. These tests use FastAPI’s TestClient and cover core endpoints such as the health check and the message analysis endpoint.

Test coverage is measured using pytest-cov. Coverage reports are generated in XML format and archived as CI artifacts, enabling quality monitoring without introducing instability to the pipeline.

## Containerization and Deployment

The backend service is fully containerized using Docker. A Dockerfile is provided for building the backend image, and Docker Compose is used for local orchestration. This setup ensures reproducible environments and simplifies local development and deployment.

Docker images are built and pushed automatically to Docker Hub as part of the CI pipeline, demonstrating a complete DevOps lifecycle from source code to deployable artifacts.

## Continuous Integration and Delivery

The project includes a declarative Jenkins pipeline defined in a Jenkinsfile located at the repository root. The pipeline performs source code checkout, backend image build, automated test execution inside the container, coverage report generation, Docker image publishing, frontend extension image build, and artifact archiving.

External AI services are not invoked during CI execution, ensuring stable and reliable builds independent of network availability or API quotas.

## Running the Project Locally

The backend can be run locally using Docker Compose:

```bash
docker-compose up --build

---

The backend service will be available at:

```bash
http://localhost:8000
---

Automated tests with coverage can be executed locally using:
```bash
cd backend
pytest --cov=app --cov-report=xml
---

Environment Configuration
The backend supports optional AI integration via environment variables provided in a .env file. If the Gemini API key is not configured, the system automatically operates in lexicon-only mode without failure.

Project Outcomes
This project demonstrates the design and implementation of a production-oriented AI-assisted system, combining responsible AI integration, automated testing, containerization, and CI/CD practices. The solution is suitable for inclusion in a junior developer portfolio and reflects real-world engineering decision-making.

Authors
Efrat Zusman
Shulamit Greensfeld

# 🏛️ CampusBook — Cloud-Based Campus Resource Sharing & Utilization Platform

> A full-stack web application for managing, booking, and tracking campus resources — hosted on **IBM Cloud**.

## 👥 Team

| Name | Registration No | Role |
|------|----------------|------|
| Bharadwaj | 245805090 | Frontend Developer + UI/UX |
| Vishwas H V | 245805014 | Full-Stack Lead + Cloud Architect |
| Navneet Vankadara | 245805426 | Backend Developer + Testing & Docs |

**Supervisor:** School of Computer Engineering  
**Academic Year:** 2026-27 | **Semester:** 5th

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18 + Vite |
| **Backend** | Python FastAPI |
| **Database** | IBM Cloudant (NoSQL) / CouchDB (local) |
| **Hosting** | IBM Cloud Code Engine |
| **Container** | Docker |
| **CI/CD** | GitHub Actions |
| **Monitoring** | IBM Cloud Monitoring |

---

## 📦 Features

- ✅ **User Authentication** — JWT-based signup/login with role-based access (Student, Faculty, Admin)
- ✅ **Resource Catalog** — Browse, search, and filter campus resources by category
- ✅ **Smart Booking** — Real-time availability checking with automatic conflict detection
- ✅ **Approval Workflow** — Faculty/admin approval for booking requests
- ✅ **Utilization Analytics** — Charts showing peak hours, resource utilization, category distribution
- ✅ **Notifications** — In-app notifications for booking status changes
- ✅ **Admin Panel** — Manage resources, approve/reject bookings, view analytics
- ✅ **Auto-scaling** — IBM Cloud Code Engine scales 0-3 instances based on traffic
- ✅ **CI/CD Pipeline** — Automatic testing and deployment on git push

---

## 🛠️ Quick Start (Local Development)

### Prerequisites
- [Docker Desktop](https://docker.com) installed
- [Node.js 18+](https://nodejs.org) installed
- [Python 3.11+](https://python.org) installed

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repo
git clone https://github.com/<your-username>/campus-resource-platform.git
cd campus-resource-platform

# Start all services (CouchDB + Backend + Frontend)
docker compose up --build

# Access the app:
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
# CouchDB: http://localhost:5984/_utils
```

### Option 2: Run Manually

**Terminal 1 — Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start CouchDB via Docker first
docker run -d --name couchdb -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password couchdb:3

# Run the backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Default Login
- **Admin:** `admin@campus.edu` / `admin123` (auto-created on first run)

---

## ☁️ IBM Cloud Deployment

### 1. Create IBM Cloud Services

```bash
# Login to IBM Cloud
ibmcloud login

# Create Cloudant database
ibmcloud resource service-instance-create campus-cloudant cloudantnosqldb lite us-south

# Create service credentials
ibmcloud resource service-key-create campus-cloudant-key Manager --instance-name campus-cloudant
```

### 2. Set GitHub Secrets

In your GitHub repo → Settings → Secrets → Actions, add:

| Secret | Value |
|--------|-------|
| `IBM_CLOUD_API_KEY` | Your IBM Cloud API key |
| `CLOUDANT_URL` | Cloudant instance URL |
| `CLOUDANT_APIKEY` | Cloudant service credential API key |
| `JWT_SECRET_KEY` | A random secure string |

### 3. Push to Deploy

```bash
git push origin main
# GitHub Actions will automatically:
# 1. Run all tests
# 2. Build Docker images
# 3. Push to IBM Container Registry
# 4. Deploy to Code Engine
```

---

## 📂 Project Structure

```
campus-resource-platform/
├── frontend/                    # React + Vite
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API client
│   │   ├── context/             # React context (auth)
│   │   └── index.css            # Complete design system
│   ├── Dockerfile
│   └── nginx.conf
├── backend/                     # Python FastAPI
│   ├── app/
│   │   ├── models/              # Pydantic models
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── middleware/          # Auth middleware
│   │   └── main.py             # App entry point
│   ├── tests/                   # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
├── .github/workflows/
│   └── deploy.yml               # CI/CD pipeline
├── docker-compose.yml           # Local development
└── README.md
```

---

## 🎯 CCD Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| Cloud Deployment | IBM Cloud Code Engine |
| Containerization | Docker (multi-stage builds) |
| CI/CD | GitHub Actions → IBM Cloud |
| Managed Database | IBM Cloudant NoSQL |
| Auto-Scaling | Code Engine (0-3 instances) |
| Load Balancing | Built into Code Engine |
| Cloud Monitoring | IBM Cloud Monitoring |
| Microservices | Separate frontend & backend containers |
| Role-Based Access | JWT + RBAC (student/faculty/admin) |
| Infrastructure as Code | Docker Compose + CI/CD configs |

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/signup` | Register new user | No |
| POST | `/api/auth/login` | Login | No |
| GET | `/api/auth/me` | Get profile | Yes |
| GET | `/api/resources/` | List resources | Yes |
| POST | `/api/resources/` | Create resource | Admin |
| POST | `/api/bookings/` | Create booking | Yes |
| GET | `/api/bookings/` | List my bookings | Yes |
| PUT | `/api/bookings/{id}/approve` | Approve/reject | Faculty/Admin |
| GET | `/api/analytics/dashboard` | Dashboard stats | Yes |
| GET | `/api/analytics/utilization` | Utilization data | Faculty/Admin |
| GET | `/api/health` | Health check | No |

Full API docs available at `/api/docs` (Swagger UI).

---

## 📜 License

This project is developed for academic purposes as part of the Cloud Computing & DevOps (CCD) course, 5th Semester, School of Computer Engineering.

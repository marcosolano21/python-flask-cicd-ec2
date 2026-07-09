# python-flask-cicd-ec2
# CI/CD Pipeline for Flask Application on AWS EC2

This repository features the design, development, and deployment of a fully automated **Continuous Integration (CI)** and **Continuous Deployment (CD)** pipeline for a Python (Flask) web application. The application acts as a resource dashboard, tracking system metrics like CPU and Memory utilization using `psutil`.

The infrastructure is engineered following **high availability** and **Zero-Downtime Deployment (Rolling Update)** principles, utilizing Nginx as a reverse proxy/load balancer and Jenkins as the core automation orchestrator.

---

##  System Architecture

The workflow and infrastructure components are distributed as follows:

1. **Version Control / Local Environment:** Code is managed locally and pushed via Git to GitHub. Every `git push` automatically triggers the Jenkins pipeline utilizing Webhooks.
2. **Automation Server (Jenkins):** Runs the **CI phase** (Linting, SAST Security Scanning, and Unit/Integration Testing) in an isolated local environment inside a Jenkins container.
3. **Production Environment (AWS EC2):** If all CI stages pass successfully, Jenkins establishes a secure SSH connection to execute the **CD phase**. It pulls the latest changes from GitHub via a clean `git reset --hard` and executes a sequential rolling update across two application instances running on ports `8081` and `8082`.
4. **Network / Proxy Layer (Nginx):** Functions as a Reverse Proxy and Load Balancer (using the Round-Robin algorithm), routing public web traffic from Port 80 to the internal Flask application instances.


##  Pipeline Structure (`Jenkinsfile`)

The pipeline is fully automated and designed to fail-safe, protecting the production environment from unstable releases through the following sequential stages:

### Continuous Integration (CI) Phase
* **Check out:** Initializes Git.
* **Prepare Local Environment:** Initializes a virtual environment (`venv`) inside the Jenkins workspace and installs all production and testing dependencies from `requirements.txt`.
* **Code Quality Analysis (Linting):** Runs `flake8` to ensure the Python codebase complies with clean code syntax and style standards.
* **Static Application Security Testing (SAST):** Scans the code using `bandit` to identify common security vulnerabilities or bad configurations before deployment.
* **Unit & Integration Testing:** Executes `pytest` to validate Flask routing logic and ensure the HTML templates render correctly.

### Continuous Deployment (CD) Phase
* **Fetch Changes on EC2:** Connects securely over SSH, updates the production repository using a hard reset to guarantee parity with GitHub, and updates remote dependencies.
* **Zero-Downtime Sequential Deployment:**
  * Kills the process running on **Instance 1 (Port 8081)**, restarts the application in the background using `nohup`, and sleeps for 5 seconds to allow it to stabilize. During this window, user traffic is entirely handled by Instance 2.
  * Restarts **Instance 2 (Port 8082)** following the exact same sequence. By this time, Instance 1 is fully live and serving traffic with the newly deployed code.
* **Live Smoke Test:** Executes an automated `curl` request to the EC2 instance's public IP address. If the server responds with any HTTP status code other than `200 OK` (such as a `502 Bad Gateway` or `500 Internal Server Error`), Jenkins marks the pipeline as **FAILED**, protecting the deployment history and alerting engineers.

---

---

## How to Run & Simulate the Production Deployment

To simulate the production-ready environment on your AWS EC2 instance, the application runs across multiple internal processes managed by the Nginx load balancer:

1. **Launch the backend instances:** Spin up two isolated processes of the application on different ports inside the EC2 instance:
   ```bash
   python3 app.py 8081 &
   python3 app.py 8082 &

To access the app, you need to search on your browser: http://EC2_Public_IP:80
Once running, Nginx automatically listens on port 80 and acts as a load balancer, seamlessly distributing user requests between port 8081 and port 8082.
From this point forward, the environment is fully hands-off. Whenever you make code modifications locally and execute a git push to GitHub, the Jenkins Webhook immediately triggers the CI/CD pipeline—testing, validating, and updating the live EC2 environment with zero downtime.

---

## Prerequisites & EC2 Environment Setup

Before executing the pipeline, the AWS EC2 instance must be provisioned with **Ubuntu Server** and configured with the following baseline dependencies:

1. **System Packages & Git:** Ensure the OS is up to date and Git is installed to handle repository cloning:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install git python3-pip python3-venv -y

Web Server (Nginx): Install Nginx to manage port routing and reverse proxy operations:

sudo apt install nginx -y
Process Management Utilities: Ensure fuser is available. The deployment script relies on fuser to safely identify and terminate old application processes on specific ports before spinning up new ones:

Bash
sudo apt install psmisc -y

Security Group Configuration (AWS Console): * Open port 80 (HTTP) to public traffic so users can access the dashboard.

Open port 22 (SSH) restricted to your Jenkins server IP (and your local machine) to allow secure automation access.

---

---

##  Nginx Server Configuration (`/etc/nginx/sites-available/default`)

To achieve seamless load balancing, Nginx is configured with the following upstream block and reverse proxy headers:

```nginx
upstream mi_app_backend {
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://mi_app_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

---
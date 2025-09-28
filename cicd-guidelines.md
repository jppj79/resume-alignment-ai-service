# 🚀 Local DevOps Lab: From Code to Kubernetes on Windows

Welcome! This guide will walk you through building a complete, automated CI/CD pipeline from scratch. We'll take a Python application, containerize it, and deploy it to a local Kubernetes cluster. The entire process is automated, mirroring a modern, real-world DevOps workflow.

---
## 🤔 Who Is This Lab For?

This hands-on guide is designed to bridge the gap between theory and practice. It's built for motivated individuals who want to understand the complete CI/CD workflow by building it themselves.

#### ✅ This lab is a perfect fit if you are:

* An aspiring **DevOps or Platform Engineer** who wants a practical, real-world project for your portfolio.
* A **Developer** curious about what happens after you `git push` and want to understand the deployment lifecycle.
* A **Student or IT Professional** looking to gain hands-on experience with in-demand tools like Docker, Kubernetes, and GitHub Actions.
* Someone who learns best by **doing, building, and troubleshooting**.

#### 📚 What You'll Need to Know (Prerequisites):

* **Basic Command-Line Skills:** You should be comfortable navigating directories and running commands in a terminal (this guide uses PowerShell).
* **Git & GitHub Fundamentals:** You need to know how to `fork`, `clone`, `add`, `commit`, and `push` changes to a repository.
* **Beginner Python Familiarity:** You don't need to be a Python expert, but you should understand the concept of a web API. You will not be writing any Python code in this lab.
* **No Docker or Kubernetes Expertise Required!** This lab is specifically designed to teach you the practical application of these tools from the ground up.

---
### 💡 A Note on the Approach (The "Why" Behind the Tools)

You might be thinking, "Isn't deploying a simple API to a full Kubernetes cluster a classic case of over-engineering?"

**You are absolutely right.** For a project of this small scale, a simpler deployment method would suffice in a real-world scenario.

However, the **goal of this lab is to learn and demonstrate a production-grade *workflow***. While **Minikube** is a fantastic tool for local development and not production itself, the concepts and artifacts you are building—the multi-stage `Dockerfile`, the Kubernetes manifests, the `kubectl` commands, and the automated CI/CD pipeline—are **exactly the same** as those used to manage large-scale applications in the cloud.

We are using a safe, local sandbox (Minikube) to master a professional-grade toolchain and process from end to end.

---
## 🎯 Task 0: Prepare Your DevOps Workshop

**The Problem:** We can't build a powerful pipeline without the right tools, a clean workspace, and the project code to work on.

**Your Goal:** To fully configure your Windows 11 machine with all the necessary command-line tools and to prepare the application's source code for the tasks ahead.

### ✅ Prerequisites

Before you begin, ensure you have the following installed. If you don't, the next section will guide you through the installation.

* **Git:** For version control.
* **Docker Desktop for Windows:** For building and running our containers.
* **PowerShell:** The command-line shell we'll be using.
* **Chocolatey:** A package manager for Windows that will simplify our setup.
* **Minikube:** The tool to run a local Kubernetes cluster.
* **kubectl:** The command-line tool to interact with our Kubernetes cluster.

---
### ⚙️ Step 1: Install Your Command-Line Tools

We will use the Chocolatey package manager to easily install our Kubernetes tools.

#### **Install Chocolatey**
If you don't have it, open **PowerShell as an Administrator** and run the following command:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
> **Note:** After the script finishes, you must close and reopen your PowerShell window for the changes to take effect.

#### **Install Minikube and kubectl**
With Chocolatey ready, open a new **administrator PowerShell** window and run this single command to install both Minikube and the Kubernetes CLI:

```powershell
choco install minikube kubernetes-cli -y
```

---
### 📂 Step 2: Set Up the Application Repository

Now, let's get the application's source code.

1.  **Fork the Repository**
    * Navigate to the application repository here: **[https://github.com/jppj79/resume-alignment-ai-service](https://github.com/jppj79/resume-alignment-ai-service)**
    * Click the **Fork** button in the top-right corner to create your own copy under your GitHub account.

2.  **Clone Your Fork**
    * Open a standard PowerShell window in your preferred development directory. Clone your forked repository, making sure to **replace `YOUR-USERNAME`** with your actual GitHub username.

    ```powershell
    git clone https://github.com/YOUR-USERNAME/resume-alignment-ai-service.git
    ```

3.  **Switch to the `start` Branch**
    * This is the most important step. The `start` branch contains only the application code, which is our clean starting point for this lab.

    ```powershell
    cd resume-alignment-ai-service
    git checkout start
    ```

Your workshop is now ready! You have all the tools and the initial code. In the next task, we'll solve our first problem: making the application portable.

---
## 🎯 Task 1: Make the Application Portable

Your workshop is now fully equipped! You have the tools and the source code. However, our application has a major limitation: it only works on your machine because it depends on your specific Python version and libraries. This is fragile and difficult to share.

**The Problem:** How can we package our application so it runs reliably on any developer's machine, or any server, without complex setup?

**Your Goal:** To containerize the application using Docker. We will create a `Dockerfile` to serve as a blueprint and a `docker-compose.yml` file to make it easy to run locally. The final result will be a self-contained, portable application.

### 🐳 The Blueprint: Understanding the Dockerfile

The `Dockerfile` is the most important file for containerization. It contains the step-by-step instructions Docker follows to build our application image. The one we are using is an excellent example of a modern, optimized file.

```dockerfile
# --- Stage 1: Builder ---
# Use a specific Python version for reproducibility
FROM python:3.13.7-slim AS builder

# Install minimal build tools (in case a package requires compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pip tools for building wheels
RUN pip install --no-cache-dir wheel

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Build wheels for all dependencies into /wheels directory
RUN pip wheel --no-cache-dir -r requirements.txt -w /wheels

# --- Stage 2: Runtime ---
# Use a clean Python image for the runtime
FROM python:3.13.7-slim

# Set working directory
WORKDIR /app

# Create a non-root user for better security
RUN useradd -m appuser

# Copy wheels from builder and install dependencies from local wheels only
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy application source code
COPY ./app /app/app

# Switch to non-root user
USER appuser

# Internal FastAPI port
ENV PORT=8000
EXPOSE $PORT

# Default command to run the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
```

#### Key Practices Explained
* **The Two-Stage Build:** This is the most critical concept. Stage 1 (`builder`) is a "workshop" where we install tools (`gcc`, `wheel`) and pre-compile our dependencies. Stage 2 is the final, clean "showroom." We only copy the finished application and its pre-compiled dependencies from the workshop. This results in a final image that is significantly **smaller and more secure**, as it contains no unnecessary build tools.
* **Leveraging Layer Caching:** Notice `COPY requirements.txt .` happens before `COPY ./app ...`. If we change our app code but not the dependencies, Docker reuses the existing dependency layer, making our builds much faster.
* **Installing Health Check Dependencies:** The `healthcheck` in Docker Compose needs a tool to verify the application is responsive from inside the container. We install `curl` for this specific purpose and clean up the package cache in the same command, a best practice for enabling reliable health checks while keeping the image small.
* **Running as a Non-Root User:** By default, containers run as `root`, which is a security risk. We create a dedicated, unprivileged user (`appuser`) and switch to it with the `USER` command. This is a vital security best practice.

### 🎼 The Conductor: Understanding Docker Compose

While we could run our container with a long `docker run` command, using Docker Compose is a best practice for local development. It allows us to define our application's configuration in a simple, declarative YAML file.

```yaml
version: '3.9'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    # Map host port to container port
    ports:
      - "${HOST_PORT}:${PORT}"
    # Pass environment variables to the container
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PORT=${PORT}  # Internal container port
    restart: unless-stopped
    # Healthcheck to ensure FastAPI is running
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${PORT}/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

#### Key Practices Explained
* **Using Variables (`${...}`):** Hardcoding values like ports or API keys is inflexible. By using variables, we can define all our configuration in a separate `.env` file. This allows anyone to run the project without modifying the compose file.
* **Managing Secrets (`environment`):** The `environment` section pulls values from our `.env` file (which should never be committed to git) and injects them securely into the container at runtime.
* **Health Checks (`healthcheck`):** This is a powerful feature. It tells Docker to not just check if the container *process* is running, but to check if the *application inside* is actually healthy by hitting its `/health` endpoint.

### 🚀 Your Turn: Run the Application

Now, let's put this all together and run the application.

1.  **Create the `Dockerfile` and `docker-compose.yml` files** in the root of your project directory and paste the content from the sections above into them.

2.  **Create a `.env` file**, also in the project root. This file will securely store our configuration and secrets.

```env
# The port on your local machine to access the application
HOST_PORT=8000

# The internal port the FastAPI application runs on (should match the Dockerfile)
PORT=8000

# Your OpenAI API key
OPENAI_API_KEY=sk-YourSecretKeyGoesHere
```

3.  **Build and Run with One Command.** Open your PowerShell terminal in the project root and run:
```powershell
docker-compose up --build
```

4.  **Verify It's Working.** After the build completes and the logs show the Uvicorn server has started, open your web browser to **[http://localhost:8000/health](http://localhost:8000/health)**. You should see the following JSON.

```json
{
    "status": "ok",
    "service": "alignment-service"
}
```

5.  **Stop the application** by returning to your terminal and pressing `Ctrl + C`, then running:
```powershell
docker-compose down
```

Success! You have now successfully containerized the application and have an easy, repeatable way to run it locally. It is now a truly portable artifact, ready for the next task.

---
## 🎯 Task 2: Launch in a Production-like Environment

So far, we have a portable container image and an easy way to run it with Docker Compose. However, `docker-compose` is designed for local development, not for production.

**The Problem:** How do we run our application in a way that is resilient, scalable, and manageable, just like in a real production environment?

**Your Goal:** To deploy our containerized application to Kubernetes. We will use **Minikube** to create a local, single-node Kubernetes cluster that mimics a cloud environment. You will learn to define your application's state using declarative manifest files and manage secrets securely.

### ⚙️ The Blueprints: Kubernetes Manifests

In Kubernetes, we don't tell the cluster *how* to do things; we give it a YAML file that describes the **desired state**, and Kubernetes figures out how to make it happen. We need two blueprints (or "manifests") for our application.

#### **`deployment.yaml`**
This file tells Kubernetes *what* to run. It defines things like the container image to use, how many replicas (copies) of the application to run for high availability, and how to inject our secrets.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resume-service-deployment
  labels:
    app: resume-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: resume-service
  template:
    metadata:
      labels:
        app: resume-service
    spec:
      containers:
      - name: resume-service-container
        image: resume-service:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 8000
        env:
          - name: OPENAI_API_KEY
            valueFrom:
              secretKeyRef:
                name: openai-secret
                key: OPENAI_API_KEY
```

> **Key Concepts:**
> * `replicas: 2`: We are telling Kubernetes to always run two identical copies (pods) of our application. If one crashes, Kubernetes will automatically restart it to maintain the desired state.
> * `imagePullPolicy: Never`: This tells Kubernetes to *not* try to download the image from the internet. It will use the image we build locally inside Minikube's environment.
> * `env: ... valueFrom: secretKeyRef:`: This is the secure way to manage secrets. It tells the container to get the value for the `OPENAI_API_KEY` environment variable from the Kubernetes Secret named `openai-secret`.

#### **`service.yaml`**
This file tells Kubernetes *how to access* our application. It creates a stable network endpoint to expose our running pods to traffic.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: resume-service
spec:
  type: NodePort
  selector:
    app: resume-service
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
```

> **Key Concept:** `type: NodePort` is an easy way to expose our service to the outside world in a local environment like Minikube. It opens a specific port on the cluster's node and forwards traffic to our application's pods.

### 🚀 Your Turn: Deploy to Kubernetes

1.  **Create the Manifests:** Inside your project, create a new folder named `k8s`. Inside `k8s`, create the `deployment.yaml` and `service.yaml` files and paste the content from above into them.

2.  **Start Minikube:** Open PowerShell and start your local Kubernetes cluster. This command prepares your Docker Desktop environment to host the cluster.

    ```powershell
    minikube start --driver=docker
    ```

3.  **Create the Secret:** Securely create the API key secret within the Kubernetes cluster itself. The application pods will later request this secret by name. **Remember to use your real key.**

    ```powershell
    kubectl create secret generic openai-secret --from-literal=OPENAI_API_KEY='sk-YourSecretKeyGoesHere'
    ```

    > **IMPORTANT:** By default, Kubernetes Secrets are **encoded** using Base64, not **encrypted**. This means anyone with access to view the Secret object can easily decode its value. The true purpose of a Secret is to decouple sensitive data (like API keys) from your application's source code and deployment files, which is a critical security practice.
    ```powershell
    # This command gets the encoded secret
    kubectl get secret openai-secret -o yaml
    ```

4.  **Build the Image Inside Minikube:** This is a critical step where we build our container image in a place the Kubernetes cluster can find it without needing an external registry.

    **4a. Connect to Minikube's Docker Environment:** The following command reconfigures your current PowerShell terminal. After running it, any `docker` command you type will be sent to the Docker engine running *inside* your Minikube cluster, not your main Docker Desktop.

    ```powershell
    minikube -p minikube docker-env | Invoke-Expression
    ```

    **4b. Build the Image:** Now, run the standard build command. Because of the previous step, the resulting image (`resume-service:latest`) will be built and stored directly within your Minikube cluster's private image cache.

    ```powershell
    docker build -t resume-service:latest .
    ```

    **4c. Verify the Image (Optional but Recommended):** To prove the image exists inside Minikube, run this command in the same terminal. You should see `resume-service` with the `latest` tag in the list of images returned. This list is from *Minikube's* Docker daemon.

    ```powershell
    docker images
    ```

    **4d. Delete the Image (For Troubleshooting):** If you need to do a clean rebuild, you can delete the image from Minikube's cache with this command.

    ```powershell
    docker rmi resume-service:latest
    ```
    > **Important:** Your terminal is now connected to Minikube's Docker for this session. To go back to controlling your standard Docker Desktop daemon (for other projects), you must **open a new PowerShell terminal**.

5.  **Apply the Manifests:** This command tells `kubectl` to send your YAML files to the Kubernetes API server. Kubernetes reads your "desired state" (a Deployment with 2 replicas and a Service) and works to make it a reality.

    ```powershell
    kubectl apply -f k8s/
    ```

6.  **Verify and Access:** Now we confirm that Kubernetes has successfully created the resources.

    **6a. Check the Pods:** Use this command to see the status of your application pods. Wait until you see two pods with a `STATUS` of `Running`. This confirms Kubernetes has successfully started your containers using the image we built.
    
    ```powershell
    kubectl get pods
    ```

    **6b. Access the Service via Tunnel:** This command creates a network tunnel from your local Windows machine to the service running inside the isolated Minikube cluster. It will print the URL in your terminal and automatically open it in your default web browser. **Leave this terminal running** to keep the tunnel active.

    ```powershell
    minikube service resume-service
    ```
    > You will see output like:
    >
    > | NAMESPACE |      NAME      | TARGET PORT |            URL            |
    > |-----------|----------------|-------------|---------------------------|
    > | default   | resume-service |        8000 | http://127.0.0.1:51234    |

    **6c. Test the Health Endpoint:** The URL provided in the step above (e.g., `http://127.0.0.1:51234`) is the base URL for your application. To test the health endpoint, open a **new PowerShell terminal** (leaving the one with the tunnel running) and use `curl` with that base URL.
    
    ```powershell
    # Replace the URL with the one provided by the 'minikube service' command
    curl http://127.0.0.1:51234/health
    ```
    > You should receive a healthy response, like: `{"version":"0.1.0", "status":"ok", "service": "alignment-service"}`.

Congratulations! You have successfully deployed your application to a Kubernetes cluster and verified its endpoints. The final task is to make this entire process happen automatically.

## 🎯 Task 3: Automate Your Deployments

We have successfully deployed our application to Kubernetes, but the process was entirely manual. This is slow, prone to human error, and not a sustainable practice.

**The Problem:** How do we automate this entire workflow so that any change to our code is automatically built and deployed to our cluster?

**Your Goal:** To build a complete, end-to-end CI/CD (Continuous Integration / Continuous Deployment) pipeline using **GitHub Actions**. This pipeline will automatically trigger on a `git push`, building and deploying our application without any manual intervention.

### 📜 The Workflow File: Your Automation Blueprint (Best Practice Edition)

This is the heart of our automation. It's a YAML file that tells GitHub Actions exactly what steps to run. The following workflow uses the industry best practice of **unique image tagging** for traceability and declarative deployments.

Create the folder structure `.github/workflows/` in the root of your project, and inside it, create a file named `main.yml`.

```yaml
name: Local Lab CI/CD Pipeline

on:
  push:
    branches:
      - 'feature/local-cicd-pipeline'

jobs:
  build-and-deploy:
    runs-on: self-hosted

    steps:
      - name: 1. Checkout Code
        uses: actions/checkout@v4

      - name: 2. Generate Unique Image Tag
        id: generate_tag
        shell: powershell
        # Use .Substring() to get the first 7 characters of the Git SHA in PowerShell
        run: echo "IMAGE_TAG=$($env:GITHUB_SHA.Substring(0, 7))" | Out-File -FilePath $env:GITHUB_OUTPUT -Append

      - name: 3. Build and Tag Image Inside Minikube
        shell: powershell
        run: |
          minikube -p minikube docker-env | Invoke-Expression
          # We now reference the output from the 'generate_tag' step
          docker build -t resume-service:${{ steps.generate_tag.outputs.IMAGE_TAG }} .

      - name: 4. Update Kubernetes Manifest with New Image Tag
        shell: powershell
        run: |
          # We also use the step output here for the replacement
          (Get-Content -Path k8s\deployment.yaml -Raw) -replace 'resume-service:latest', 'resume-service:${{ steps.generate_tag.outputs.IMAGE_TAG }}' | Set-Content -Path k8s\deployment.yaml

      - name: 5. Deploy to Kubernetes
        run: kubectl apply -f k8s/
```

#### Key Concepts Explained
* **Step 2: Generate Unique Image Tag:** We use a PowerShell command `.Substring(0, 7)` to get a short, unique ID from the Git commit that triggered the pipeline. This creates a perfect, traceable link between our code and the container image.
* **Step 3: Build and Tag Image:** The `docker build` command now uses our unique `${{ steps.generate_tag.outputs.IMAGE_TAG }}` to tag the new image.
* **Step 4: Update Kubernetes Manifest:** This is the crucial declarative step. Before deploying, we use a PowerShell command to find and replace `resume-service:latest` with our new unique tag (e.g., `resume-service:a1b2c3d`) directly in the `deployment.yaml` file.
* **Step 5: Deploy to Kubernetes:** When `kubectl apply` runs, it sends the *updated* manifest to Kubernetes. Kubernetes sees that the `image:` spec has changed and automatically triggers a safe, rolling update to the new version.

### 🚀 Your Turn: Run the Pipeline

1.  **Configure the GitHub Self-Hosted Runner:**
    This agent is the crucial link between GitHub's cloud platform and your local machine.

    * **a. Navigate to the Runners Page:** In your forked GitHub repository, go to **Settings > Actions > Runners**.
    * **b. Create a New Runner:** Click the **"New self-hosted runner"** button and select **Windows** as the operating system.
    * **c. Follow GitHub's Instructions:** GitHub will now display a set of commands unique to your repository. You will run these in an **administrator PowerShell** window. The process will be:
        1.  **Create a folder:** It's a good practice to create a dedicated directory for the runner.
            ```powershell
            mkdir C:\actions-runner; cd C:\actions-runner
            ```
        2.  **Download:** Run the `Invoke-WebRequest` command provided by GitHub to download the runner software.
        3.  **Extract:** Run the command to unzip the downloaded file.
        4.  **Configure:** Run the `config.cmd` command provided by GitHub. This is the most important step, as it securely registers your runner with your repository using a **unique token**.
            > **Important:** You must copy the `config.cmd ...` command directly from your browser. The token is temporary and secret.
        5.  **Run the Agent:** Finally, run the `.\run.cmd` command. Your PowerShell terminal will now show that the runner is connected and `Listening for jobs...`.

            > **Leave this PowerShell window open!** It must stay running in the background to process your pipeline.


2.  **Create the Workflow File:** Create the `.github/workflows/main.yml` file in your project and paste the corrected content from above.

3.  **Trigger the Pipeline:** Commit and push your changes to trigger the pipeline.
    ```powershell
    git add .
    git commit -m "Feat: Implement best-practice CI/CD pipeline"
    git push origin feature/local-cicd-pipeline
    ```

4.  **Watch the Magic:**
    * Watch your **runner's terminal** as it executes the job.
    * Watch the live logs in the **"Actions" tab** of your GitHub repository.

### ✅ Verify the Automated Deployment

1.  **Check for New Pods:** Run `kubectl get pods`. You will see that the `AGE` of the pods is very recent, proving the pipeline successfully deployed the new version.

    ```powershell
    kubectl get pods
    ```

2.  **Test the Endpoint (Using the Existing Tunnel):**
    This is where the magic of Kubernetes Services comes in. The tunnel you opened with `minikube service` connects to the stable **Service**, not directly to the individual pods. The Service acts like a smart signpost that automatically redirects traffic to the new pods as soon as they are ready.

    **This means if you already have a tunnel running, you do not need to restart it.**

    * Simply go back to **Postman** and re-run the exact same request to the same URL (e.g., `http://127.0.0.1:55123/health`).
    * You should immediately see the new response reflecting your code changes (e.g., `"version": "0.4.0"`).

    If you had previously closed the tunnel, you can just open a new one by running the command again:

    ```powershell
    minikube service resume-service
    ```

3.  **Test with Postman:**
    * Use the new URL provided by the command above in Postman to test the `/health` endpoint. You should now see the changes you made to the code.

## 🎉 Lab Complete! 🎉

Congratulations! You have successfully built a complete, end-to-end local CI/CD pipeline using professional best practices. You now have hands-on experience with the fundamental workflow that powers modern software development.

---
### 🎓 Bonus Challenge: The "Day After" Simulation

In the real world, you shut down your computer at the end of the day. What happens to our lab environment when you do? Let's find out.

**Your Final Task:** Go ahead and **restart your computer**.

Once you're back in Windows, you'll notice that nothing from our lab works anymore. The `minikube service` tunnel is gone, the self-hosted runner is offline, and even `kubectl get pods` will likely fail. This is not a bug; it's by design. These components don't start automatically.

Your challenge is to bring the entire DevOps environment back to life.

#### ✅ Your Recovery Checklist:

Prove you've mastered the lab by re-initializing the environment in the correct order.

1.  🐳 **Start Docker Desktop:** Ensure the engine is running.
2.  🚢 **Restart the Kubernetes Cluster:** The Minikube virtual machine/container needs to be started again.
    ```powershell
    minikube start --driver=docker
    ```
3.  🏃 **Relaunch the Self-Hosted Runner:** Navigate to your runner's directory and start the agent so it can listen for jobs from GitHub again.
    ```powershell
    cd C:\actions-runner
    .\run.cmd
    ```
4.  🔗 **Re-establish the Network Tunnel:** Open a new tunnel to your running service so you can access it from your browser or Postman.
    ```powershell
    minikube service resume-service
    ```

By successfully completing this checklist, you've demonstrated a true understanding of how all the pieces of this environment depend on each other. Congratulations on completing the lab!

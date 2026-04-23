# hng14-stage2-devops

This project has 4 parts:

- frontend
- api
- worker
- redis

The easiest way to run everything is with Docker Compose.

## What you need first

Please install these before you start:

- Git
- Docker Desktop

If you already have both, you do not need to install Python, Node.js, or Redis on your machine.

## Step 1: Clone the project

Open your terminal and run:

```bash
git clone https://github.com/YOUR-USERNAME/hng14-stage2-devops.git
cd hng14-stage2-devops
```

If you already downloaded the project, just move into the folder:

```bash
cd hng14-stage2-devops
```

## Step 2: Start the stack

You do not need a root `.env` file for normal startup.

Just run this from the root of the project:

```bash
docker compose up --build
```

## Step 3: Wait for the containers to start

The first run may take a few minutes because Docker will build the images.

## Step 4: Open the app

When the containers are up, open these in your browser:

- Frontend: http://localhost:3000
- API health check: http://localhost:8000/healthz

## What a successful startup looks like

If everything starts well:

- Docker finishes building the images
- the frontend opens on port 3000
- the API health check returns this:

```json
{"status":"ok"}
```

- running this command in another terminal shows the containers up:

```bash
docker compose ps
```

You should see these services running:

- redis
- api
- frontend
- worker

The redis, api, frontend, and worker containers should stay up and should not keep restarting.

## How to test that it works

1. Open http://localhost:3000
2. Submit a job from the frontend
3. Wait a few seconds
4. Check the job status
5. The final status should become `completed`

## How to stop everything

When you are done, stop the stack with:

```bash
docker compose down
```

If you want to remove volumes too, run:

```bash
docker compose down -v
```

## If it does not start

Try these simple checks:

1. Make sure Docker Desktop is open.
2. Make sure you are inside the project root folder.
3. Make sure ports `3000` and `8000` are not already being used.
4. Run the build again:

```bash
docker compose up --build
```

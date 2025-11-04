# Install No Code Architect Toolkit with Docker

Installation of No Code Architect Toolkit with Docker offers the following advantages:
- Install No Code Architect Toolkit in a clean environment.
- Simplify the setup process.
- Avoid compatibility issues across different operating systems with Docker's consistent environment.

> **Info**  
> If your domain/subdomain is already pointed to the server, start at step 2.  
> If you have already installed Docker and Docker-Compose, start at step 3.

---

## 1. DNS Setup

Point your domain/subdomain to the server. Add an A record to route the domain/subdomain accordingly:

- **Type**: A  
- **Name**: The desired domain/subdomain  
- **IP Address**: `<IP_OF_YOUR_SERVER>`  

---

## 2. Install Docker

This can vary depending on the Linux distribution used. Below are instructions for Ubuntu:

### Set up Docker's APT Repository

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to APT sources:
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

### Install the Docker Packages

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---

## 3. Create Docker Compose File

Create a `docker-compose.yml` file and paste the following configuration:

### With SSL Support
Enables SSL/TLS for secure, encrypted communications. Ideal for those wanting a hands-off approach to SSL setup.

```yaml
services:
  traefik:
    image: "traefik"
    restart: unless-stopped
    command:
      - "--api=true"
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.web.http.redirections.entryPoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.mytlschallenge.acme.tlschallenge=true"
      - "--certificatesresolvers.mytlschallenge.acme.email=${SSL_EMAIL}"
      - "--certificatesresolvers.mytlschallenge.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - traefik_data:/letsencrypt
      - /var/run/docker.sock:/var/run/docker.sock:ro
  ncat:
    image: stephengpope/no-code-architects-toolkit:latest
    env_file:
      - .env
    labels:
      - traefik.enable=true
      - traefik.http.routers.ncat.rule=Host(`${APP_DOMAIN}`)
      - traefik.http.routers.ncat.tls=true
      - traefik.http.routers.ncat.entrypoints=web,websecure
      - traefik.http.routers.ncat.tls.certresolver=mytlschallenge
    volumes:
      - storage:/var/www/html/storage/app
      - logs:/var/www/html/storage/logs
    restart: unless-stopped

volumes:
  traefik_data:
    driver: local
  storage:
    driver: local
  logs:
    driver: local
```

---

## 4. Create `.env` File

Create an `.env` file and configure it accordingly:

```env
# The name of your application.
APP_NAME=NCAToolkit

# Debug mode setting. Set to `false` for production environments.
APP_DEBUG=false

# Your app's domain or subdomain, without the 'http://' or 'https://' prefix.
APP_DOMAIN=example.com

# Full application URL is automatically configured; no modification required.
APP_URL=https://${APP_DOMAIN}

# SSL settings
SSL_EMAIL=user@example.com

# API_KEY
# Purpose: Used for API authentication.
# Requirement: Mandatory.
API_KEY=your_api_key_here

# Cloud Storage Configuration (choose one)
#
# OPTION 1: Cloudflare R2 (Recommended - zero egress fees)
# Important: Use S3_* variable names, NOT AWS_*
#
#S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
#S3_ACCESS_KEY=your_r2_access_key
#S3_SECRET_KEY=your_r2_secret_key
#S3_BUCKET_NAME=your-bucket-name
#S3_REGION=auto
#
# For custom domain setup (optional):
# S3_ENDPOINT_URL=https://cdn.example.com
# S3_REGION=auto
#
# See docs/R2_MIGRATION.md for complete R2 setup guide

# OPTION 2: DigitalOcean Spaces / MinIO / Generic S3
#
#S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
#S3_ACCESS_KEY=your_access_key
#S3_SECRET_KEY=your_secret_key
#S3_BUCKET_NAME=your-bucket-name
#S3_REGION=nyc3

# OPTION 3: Google Cloud Storage Env Variables
#
# GCP_SA_CREDENTIALS
# Purpose: The JSON credentials for the GCP Service Account.
# Requirement: Mandatory if using GCP storage.
#GCP_SA_CREDENTIALS=/path/to/your/gcp/service_account.json

# GCP_BUCKET_NAME
# Purpose: The name of the GCP storage bucket.
# Requirement: Mandatory if using GCP storage.
#GCP_BUCKET_NAME=your_gcp_bucket_name

# STORAGE_PATH
# Purpose: The base path for storage operations.
# Default: GCP
# Requirement: Optional.
#STORAGE_PATH=GCP

```

---

## 5. Advanced Configuration Options

### Using an Existing Traefik Instance

If you already have Traefik running on your server, you can integrate the NCA Toolkit into your existing setup:

1. **Remove the Traefik service** from your `docker-compose.yml`
2. **Connect to your existing Traefik network**:
   ```yaml
   services:
     ncat:
       image: stephengpope/no-code-architects-toolkit:latest
       env_file:
         - .env
       labels:
         - traefik.enable=true
         - traefik.http.routers.ncat.rule=Host(`${APP_DOMAIN}`)
         - traefik.http.routers.ncat.tls=true
         - traefik.http.routers.ncat.entrypoints=web,websecure
         - traefik.http.routers.ncat.tls.certresolver=mytlschallenge
       networks:
         - your-existing-traefik-network
       restart: unless-stopped

   networks:
     your-existing-traefik-network:
       external: true
   ```

3. **Adjust labels** to match your Traefik configuration (entry points, cert resolver name, etc.)

### Building Locally vs Using Pre-built Image

The default `docker-compose.yml` uses the pre-built image: `stephengpope/no-code-architects-toolkit:latest`

**When to build locally:**
- You've made code changes
- You need a specific version not yet published
- You're developing or testing features

**To build locally**, modify your `docker-compose.yml`:

```yaml
services:
  ncat:
    build: .  # Build from local Dockerfile
    # image: stephengpope/no-code-architects-toolkit:latest  # Comment this out
    env_file:
      - .env
    # ... rest of configuration
```

Then build and start:
```bash
docker compose build
docker compose up -d
```

**Pre-built image advantages:**
- Faster deployment (no build time)
- Tested and verified releases
- Automatic updates with `docker compose pull`

---

## 6. Start Docker Compose

Start No Code Architect Toolkit  using the following command:

```bash
docker compose up -d
```

To view logs in real time:

```bash
docker compose logs -f
```

To stop the containers:

```bash
docker compose stop
```

To restart and reload env vars

# First update your .env file with the correct values
# Then run:

```bash
docker compose up -d --force-recreate ncat
```

---

## 7. Done

No Code Architect Toolkit is now accessible through the specified APP_URL. For example:  
[https://example.com](https://example.com)

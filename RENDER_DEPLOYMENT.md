# Deploying to Render.com

This guide walks through hosting the Pokemon Scouter web app on [render.com](https://render.com).

## Prerequisites

1. A GitHub account with the pokemon_scouter repository pushed to it
2. A Render.com account (sign up at https://render.com)

## Step 1: Prepare Your Repository

1. Ensure your GitHub repository includes:
   - `web_app.py` (Flask entry point)
   - `Dockerfile`
   - `.dockerignore`
   - `requirements.txt` (with `flask` and `requests`)
   - All source code (`src/`, `config/`, `web/`)

2. Push all changes to your GitHub repository:
   ```bash
   git add .
   git commit -m "Add Docker and Render configuration"
   git push origin main
   ```

## Step 2: Create a New Web Service on Render

1. Log in to [render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Select **Build and deploy from a Git repository**
4. Click **Connect** next to your GitHub account (if not already connected)
5. Select your `pokemon_scouter` repository
6. Click **Connect**

## Step 3: Configure the Service

In the deployment configuration form:

| Field | Value |
|-------|-------|
| **Name** | `pokemon-scouter` (or any name you prefer) |
| **Environment** | `Docker` |
| **Region** | Choose closest to you (e.g., `Oregon`) |
| **Branch** | `main` |
| **Dockerfile path** | (leave empty — uses root `Dockerfile`) |

## Step 4: Add Environment Variables (Optional)

If needed in the future, add environment variables:
1. Scroll to **Environment** section
2. Click **Add Environment Variable**
3. Example: `FLASK_ENV=production`

## Step 5: Configure Build & Deploy

1. Scroll to **Advanced** section
2. Set **Auto-deploy** to `Yes` (auto-deploys on git push)
3. Leave other settings as default

## Step 6: Deploy

1. Click **Create Web Service**
2. Render will:
   - Build the Docker image
   - Push to its container registry
   - Deploy the service
   - Assign you a `.onrender.com` URL

3. Wait for the build to complete (2-5 minutes)
4. Once live, you'll see a green checkmark and a URL like:
   ```
   https://pokemon-scouter-xxxxx.onrender.com
   ```

## Step 7: Access Your App

Open the assigned URL in your browser. The scout generator is now live!

## Monitoring & Management

### View Logs
1. Go to your service dashboard
2. Click the **Logs** tab
3. See real-time Flask output and errors

### Redeploy Manually
1. Click **Manual Deploy** → **Deploy latest commit**
2. Or push a new commit to trigger auto-deploy

### Scale the Service
1. Go to **Settings**
2. Adjust **Instance Type** if needed (free tier available)

## Notes

- **Free Tier**: Render offers free services with the limitation that they spin down after 15 minutes of inactivity. Upgrade to a paid plan for always-on service.
- **Build Time**: Initial build takes 2-5 minutes. Subsequent deploys are faster.
- **Requests**: The app makes live requests to Pokémon Showdown replays, so internet access is required.

## Troubleshooting

**Build fails with "requirements.txt not found"**
- Ensure `requirements.txt` is in the repository root

**Port binding error**
- The `web_app.py` now reads the `PORT` environment variable set by Render

**App times out on request**
- Large replay logs may take time to process; increase the request timeout in Render settings if needed

**Build succeeds but app won't start**
- Check **Logs** tab for Flask startup errors
- Verify all imports in Python files are correct

## Local Testing (Optional)

Before pushing to Render, test locally:

```bash
# Build Docker image
docker build -t pokemon-scouter .

# Run container
docker run -p 5000:5000 pokemon-scouter

# Visit http://localhost:5000
```

## Support

For Render-specific help, visit [render.com/docs](https://render.com/docs).

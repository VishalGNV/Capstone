# Deployment Guide for Render

## Quick Setup

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create Web Service on Render

1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Connect your GitHub repository: `VishalGNV/Capstone`

### 3. Configure Service

**Basic Settings:**
- **Name**: `secure-vault` (or your choice)
- **Environment**: `Python 3`
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn secure_vault.wsgi:application --bind 0.0.0.0:$PORT`

### 4. Environment Variables

Add these in the Render dashboard under **Environment**:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | (generate below) | **Required** |
| `DEBUG` | `0` | Production mode |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` | Replace with actual URL |
| `PYTHON_VERSION` | `3.10.12` | Python version |
| `ENCRYPTED_FILES_ROOT` | `/opt/render/project/src/encrypted_files` | Persistent storage path |

**Generate SECRET_KEY:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. Add PostgreSQL Database

1. In your Web Service → **Environment** tab
2. Scroll to **Add Database**
3. Click **New Database** → Create PostgreSQL
4. Render automatically sets `DATABASE_URL` environment variable

### 6. Add Persistent Disk (Critical for encrypted files)

1. Go to **Settings** → **Disks**
2. Click **Add Disk**
   - **Name**: `encrypted-files`
   - **Mount Path**: `/opt/render/project/src/encrypted_files`
   - **Size**: 1GB or more (adjust based on needs)

### 7. Deploy

- Click **Create Web Service**
- Render will automatically deploy
- Monitor build logs for any errors

### 8. Post-Deployment

#### Create Superuser
1. In Render dashboard → **Shell** tab
2. Run:
```bash
python manage.py createsuperuser
```

#### Access Your App
- Main URL: `https://your-app-name.onrender.com`
- Admin: `https://your-app-name.onrender.com/admin`

## Important Notes

✅ **Free Tier**: Spins down after 15 min inactivity (cold starts ~30s)
✅ **HTTPS**: Automatic SSL certificate
✅ **Auto-Deploy**: Pushes to `main` trigger automatic redeploys
⚠️ **Persistent Disk Required**: Without it, encrypted files are lost on each deploy
⚠️ **Database Backups**: Available on paid PostgreSQL plans

## Custom Domain (Optional)

1. Go to **Settings** → **Custom Domain**
2. Add your domain
3. Update DNS records as instructed
4. Update `ALLOWED_HOSTS` environment variable

## Troubleshooting

**Build Fails:**
- Check build logs in Render dashboard
- Verify all dependencies in `requirements.txt`
- `dlib` may take time to install

**App Crashes:**
- Check application logs
- Verify all environment variables are set
- Ensure `DATABASE_URL` is connected
- Check disk is mounted correctly

**Files Not Persisting:**
- Verify persistent disk is added
- Check `ENCRYPTED_FILES_ROOT` matches mount path
- Ensure disk has sufficient space

## Scaling

- **Starter Plan** ($7/mo): No sleep, better performance
- **Standard Plan**: More RAM/CPU for production
- **Upgrade Database**: For more storage and automatic backups

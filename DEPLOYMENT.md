# Samsung Promo Portal — Deployment Guide

## Project Overview

Django 6.0.3 promotion portal with 6 apps: core, accounts, dashboard, promotions, payments, support.

---

## Quick Local Setup

```bash
# 1. Clone & enter project
cd "Promos Project"

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create admin superuser
python manage.py createsuperuser

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Run development server
python manage.py runserver
```

---

## Production Deployment

### Option A: Render.com (Recommended — Free Tier Available)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Samsung Promo Portal"
   git remote add origin https://github.com/YOUR_USERNAME/samsung-promo.git
   git push -u origin main
   ```

2. **Create Render Web Service**
   - Go to [render.com](https://render.com) → New → Web Service
   - Connect your GitHub repo
   - Settings:
     - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
     - **Start Command:** `gunicorn samsung_promo.wsgi`
     - **Environment:** Python 3

3. **Set Environment Variables** on Render:
   ```
   DJANGO_SETTINGS_MODULE = samsung_promo.settings_prod
   SECRET_KEY = <generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
   ALLOWED_HOSTS = your-app.onrender.com
   DATABASE_URL = <auto-provided if you add Render PostgreSQL>
   DEBUG = False
   ```

4. **Add PostgreSQL** → Render Dashboard → New → PostgreSQL → Link to your service

---

### Option B: Railway.app

1. Push to GitHub (same as above)
2. Create new project on [railway.app](https://railway.app)
3. Add PostgreSQL plugin
4. Set environment variables (same as Render)
5. Deploy settings:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn samsung_promo.wsgi`

---

### Option C: Heroku

```bash
# Install Heroku CLI, then:
heroku create samsung-promo-portal
heroku addons:create heroku-postgresql:essential-0

heroku config:set DJANGO_SETTINGS_MODULE=samsung_promo.settings_prod
heroku config:set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
heroku config:set ALLOWED_HOSTS=samsung-promo-portal.herokuapp.com
heroku config:set DEBUG=False

git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

---

### Option D: VPS (DigitalOcean / AWS EC2 / Linode)

```bash
# 1. SSH into your server
ssh user@your-server-ip

# 2. Install system dependencies
sudo apt update && sudo apt install python3-pip python3-venv nginx postgresql

# 3. Clone project
git clone https://github.com/YOUR_USERNAME/samsung-promo.git
cd samsung-promo

# 4. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 5. Create .env from template
cp .env.example .env
nano .env  # Fill in production values

# 6. Set production settings
export DJANGO_SETTINGS_MODULE=samsung_promo.settings_prod

# 7. Migrate & collect static
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 8. Test gunicorn
gunicorn samsung_promo.wsgi --bind 0.0.0.0:8000

# 9. Setup systemd service (see below)
# 10. Setup Nginx reverse proxy (see below)
```

#### Systemd Service (`/etc/systemd/system/samsung-promo.service`):
```ini
[Unit]
Description=Samsung Promo Portal
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/samsung-promo
EnvironmentFile=/path/to/samsung-promo/.env
ExecStart=/path/to/samsung-promo/.venv/bin/gunicorn samsung_promo.wsgi --workers 3 --bind unix:/tmp/samsung-promo.sock
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Nginx Config (`/etc/nginx/sites-available/samsung-promo`):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /static/ {
        alias /path/to/samsung-promo/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/samsung-promo/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://unix:/tmp/samsung-promo.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then:
```bash
sudo ln -s /etc/nginx/sites-available/samsung-promo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable samsung-promo
sudo systemctl start samsung-promo

# SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key (50+ random chars) |
| `DEBUG` | Yes | `False` for production |
| `ALLOWED_HOSTS` | Yes | Comma-separated domain names |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `DJANGO_SETTINGS_MODULE` | Yes | `samsung_promo.settings_prod` |
| `PAYSTACK_SECRET_KEY` | No | Paystack live secret key |
| `PAYSTACK_PUBLIC_KEY` | No | Paystack live public key |
| `EMAIL_HOST` | No | SMTP host (default: smtp.gmail.com) |
| `EMAIL_HOST_USER` | No | SMTP username |
| `EMAIL_HOST_PASSWORD` | No | SMTP password / app password |
| `SECURE_SSL_REDIRECT` | No | `True` (default) for HTTPS redirect |

---

## Post-Deployment Checklist

- [ ] Run `python manage.py migrate` on production
- [ ] Run `python manage.py createsuperuser` to create admin
- [ ] Run `python manage.py collectstatic --noinput`
- [ ] Verify all pages load at your domain
- [ ] Test registration + email verification flow
- [ ] Test login/logout
- [ ] Check admin panel at `/admin/`
- [ ] Configure Paystack live keys for payments
- [ ] Set up SMTP email for OTP delivery
- [ ] Optional: Seed data with `python manage.py shell < seed_data.py`

---

## Running Tests

```bash
python manage.py test --verbosity=2
```

115 tests across all 6 apps covering:
- Models (creation, validation, properties)
- Views (page loads, forms, authentication, redirects)
- Business logic (OTP verification, referrals, task completion, payments)

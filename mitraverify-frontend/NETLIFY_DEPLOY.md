# Netlify Deployment Guide for MitraVerify Frontend

## 🚀 Quick Deploy to Netlify

### Option 1: Deploy from GitHub (Recommended)

1. **Connect Repository**
   - Go to [Netlify Dashboard](https://app.netlify.com/)
   - Click "New site from Git"
   - Choose GitHub and authorize Netlify
   - Select `ChirayuMarathe/Mitra_Verify-2.0` repository

2. **Configure Build Settings**
   ```
   Build command: npm run build
   Publish directory: out
   Base directory: mitraverify-frontend
   ```

3. **Set Environment Variables**
   - Go to Site settings > Environment variables
   - Add the following variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api-url.com
   NEXT_PUBLIC_APP_NAME=MitraVerify
   NEXT_PUBLIC_APP_VERSION=2.0
   NODE_ENV=production
   ```

4. **Deploy**
   - Click "Deploy site"
   - Netlify will automatically build and deploy your site

### Option 2: Manual Deploy

1. **Build Locally**
   ```bash
   cd mitraverify-frontend
   npm install
   npm run build
   ```

2. **Deploy Build Folder**
   - Go to Netlify Dashboard
   - Drag and drop the `out` folder to deploy

## 🔧 Configuration Details

### Build Settings
- **Build Command**: `npm run build`
- **Publish Directory**: `out`
- **Node Version**: 18.x
- **Package Manager**: npm

### Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://api.mitraverify.com` |
| `NEXT_PUBLIC_APP_NAME` | Application name | `MitraVerify` |
| `NEXT_PUBLIC_APP_VERSION` | App version | `2.0` |
| `NODE_ENV` | Environment | `production` |

### Custom Domain (Optional)
1. Go to Site settings > Domain management
2. Add your custom domain
3. Configure DNS settings

### HTTPS & Security
- Netlify automatically provides HTTPS
- Security headers are configured in `netlify.toml`

## 🐛 Troubleshooting

### Build Fails
- Check Node.js version (should be 18.x)
- Verify all dependencies are installed
- Check environment variables

### API Connection Issues
- Ensure `NEXT_PUBLIC_API_URL` is set correctly
- Backend must support CORS for your domain
- Check API endpoint accessibility

### Static Export Issues
- Ensure no server-side features are used
- Check for dynamic routes that need static generation
- Verify image optimization is disabled

## 📝 Post-Deployment Checklist

- [ ] Site loads correctly
- [ ] All pages are accessible
- [ ] API connections work (if backend is deployed)
- [ ] Images and assets load properly
- [ ] Mobile responsiveness works
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate is active

## 🔄 Continuous Deployment

Netlify automatically redeploys when you push to your GitHub repository:

1. Make changes to your code
2. Commit and push to GitHub
3. Netlify detects changes and rebuilds automatically

## 📊 Analytics & Monitoring

Add these environment variables for monitoring:
```
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=your-ga-id
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

## 🚀 Production URLs

After deployment, your site will be available at:
- **Netlify URL**: `https://your-site-name.netlify.app`
- **Custom Domain**: `https://your-domain.com` (if configured)

---

**Need help?** Check [Netlify Documentation](https://docs.netlify.com/) or [MitraVerify GitHub Issues](https://github.com/ChirayuMarathe/Mitra_Verify-2.0/issues)
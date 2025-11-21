# GitHub Publishing Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `tagfix` (or your preferred name)
3. Description: "Modern Material You web interface for audio metadata editing"
4. Choose Public or Private
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

## Step 2: Push Your Code

After creating the repository, run these commands:

```bash
cd /home/zuke/tagfix-1

# Commit your files
git commit -m "Initial commit: TagFix Material You web interface"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/tagfix.git

# Push to GitHub
git push -u origin main
```

## Step 3: Add Screenshots (Optional but Recommended)

1. Run the app: `python3 app.py`
2. Take screenshots of:
   - Light mode interface
   - Dark mode interface
   - Editing metadata
3. Save them in a `screenshots/` folder
4. Update README.md to point to actual screenshots instead of placeholders

```bash
mkdir screenshots
# Add your screenshot files
git add screenshots/
git commit -m "Add screenshots"
git push
```

## Step 4: Customize

Update these in README.md:
- Replace `yourusername` with your GitHub username
- Add your contact information
- Update the placeholder screenshots

## Step 5: Share!

Your repository URL will be:
`https://github.com/YOUR_USERNAME/tagfix`

Users can now install with:
```bash
git clone https://github.com/YOUR_USERNAME/tagfix.git
cd tagfix
pip install -r requirements.txt
python3 app.py
```

## Optional Enhancements

### Add GitHub Topics
In your repository settings, add topics:
- `audio`
- `metadata`
- `music`
- `material-design`
- `flask`
- `python`

### Add a Badge
Add this to the top of README.md:
```markdown
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

### Enable GitHub Pages (for documentation)
Settings → Pages → Deploy from branch `main`

---

**You're all set! 🚀**

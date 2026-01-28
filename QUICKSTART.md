# 🚀 Quick Start Guide - Face Attendance System

## Installation (Choose One Method)

### Method 1: Automated Setup (Recommended)

**Linux/Mac:**
```bash
cd face_attendance_system
chmod +x setup.sh
./setup.sh
```

**Windows:**
```batch
cd face_attendance_system
setup.bat
```

### Method 2: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create directories
mkdir -p data/faces data/attendance models

# 3. Run application
python app.py
```

## Running the Application

```bash
python app.py
```

Open browser: **http://localhost:5000**

## First Time Use

1. **Register a User**
   - Go to Register page
   - Enter name and ID
   - Capture face
   - Click Register

2. **Mark Attendance**
   - Go to Attendance page
   - Select Punch-in or Punch-out
   - Capture face
   - System identifies and marks attendance

3. **View Records**
   - Go to Records page
   - See all attendance entries
   - Filter and export as needed

## Troubleshooting

**Camera not working?**
- Check browser permissions
- Try Chrome browser

**Installation fails?**
- Install build tools (see README.md)
- Check Python version (3.8+)

**Face not detected?**
- Improve lighting
- Position face clearly in center

## Project Files

- `README.md` - Complete user guide
- `DOCUMENTATION.md` - Technical details
- `PROJECT_SUMMARY.md` - Assignment overview
- `app.py` - Main application
- `requirements.txt` - Dependencies

## Support

For detailed help, see README.md and DOCUMENTATION.md files.

---
**Ready to start? Run: `python app.py`**

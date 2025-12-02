# MongoDB Setup Guide

## Option 1: Use Without MongoDB (Faster Setup)

The system now works **without MongoDB**! It will:
- Store items in memory + local files (FAISS index + pickle)
- Persist data between restarts using local cache
- Fall back gracefully if MongoDB is not available

**No installation needed - just start the backend!**

## Option 2: Install MongoDB (Recommended for Production)

### Windows Installation

1. **Download MongoDB Community Server**
   - Visit: https://www.mongodb.com/try/download/community
   - Select: Windows, MSI installer
   - Download and run installer

2. **Install as a Service**
   - Choose "Complete" installation
   - Check "Install MongoDB as a Service"
   - Use default data directory: `C:\Program Files\MongoDB\Server\7.0\data`

3. **Verify Installation**
   ```powershell
   mongod --version
   ```

4. **MongoDB will auto-start on Windows startup**

### Alternative: MongoDB Docker (Easier)

```powershell
# Pull MongoDB image
docker pull mongo:latest

# Run MongoDB container
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Verify it's running
docker ps
```

## Configuration

1. **Copy environment file**
   ```powershell
   cd ai-sementic-machine
   cp .env.example .env
   ```

2. **Edit .env if needed** (optional)
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=lost_and_found
   ```

## Benefits of Using MongoDB

✅ **Persistent Storage**: Data survives server restarts  
✅ **Fast Queries**: Indexed lookups for categories, dates  
✅ **Scalability**: Handle millions of items  
✅ **Backup**: Easy database backups  
✅ **Analytics**: Query item statistics  

## System Behavior

### With MongoDB:
- Items saved to database immediately
- FAISS index synced with MongoDB
- Load all items on startup
- Full persistence

### Without MongoDB:
- Items saved to local files (FAISS + pickle)
- Data persists between restarts
- Slightly slower initial load
- Still fully functional

## Verify MongoDB Connection

After starting the backend, check logs:
```
✅ Connected to MongoDB: lost_and_found
📥 Loading items from MongoDB...
✅ Loaded X items from MongoDB
```

If MongoDB not available:
```
⚠️ Could not connect to MongoDB
⚠️ Falling back to in-memory storage
```

Both modes work perfectly!

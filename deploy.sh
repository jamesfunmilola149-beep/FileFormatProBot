#!/bin/bash

echo "🚀 Starting deployment of FileFormatProBot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if token exists
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ Error: TELEGRAM_BOT_TOKEN not set${NC}"
    echo -e "${YELLOW}Please set it using: export TELEGRAM_BOT_TOKEN=your_token${NC}"
    exit 1
fi

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed successfully${NC}"

# Run the application
echo -e "${YELLOW}🚀 Starting application...${NC}"
gunicorn app:app --bind 0.0.0.0:8080 --workers 4 --threads 2 --timeout 120

echo -e "${GREEN}✅ Deployment complete!${NC}"

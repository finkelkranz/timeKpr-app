#!/bin/bash

# Git Sync Script for timeKpr-app
# Purpose: Sync local changes with GitHub remote
# Usage: ./scripts/sync.sh [pull|push|status|full]
# Author: Scrum Master
# Date: 22.08.2026

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo -e "${RED}ERROR: Not in a git repository!${NC}"
    echo "Please run this script from the project root."
    exit 1
fi

# Check if .env exists and warn
if [ -f ".env" ]; then
    echo -e "${YELLOW}WARNING: .env file exists locally but is in .gitignore${NC}"
    echo "This file will NOT be committed (correct behavior)."
fi

# Main sync logic
ACTION="${1:-full}"

case $ACTION in
    pull)
        echo -e "${GREEN}=== Pulling latest changes from GitHub ===${NC}"
        git pull origin main
        echo -e "${GREEN}✅ Pull completed${NC}"
        ;;
    push)
        echo -e "${GREEN}=== Pushing local changes to GitHub ===${NC}"
        # Check for uncommitted changes
        if [ -n "$(git status --porcelain)" ]; then
            echo -e "${YELLOW}Uncommitted changes detected. Adding and committing...${NC}"
            git add .
            git commit -m "Auto-commit from sync.sh: $(date +'%Y-%m-%d %H:%M:%S')"
        fi
        git push origin main
        echo -e "${GREEN}✅ Push completed${NC}"
        ;;
    status)
        echo -e "${GREEN}=== Git Status ===${NC}"
        git status
        echo -e "${GREEN}=== Remote Info ===${NC}"
        git remote -v
        ;;
    full)
        echo -e "${GREEN}=== Full Sync: Pull + Push ===${NC}"
        # First pull to avoid conflicts
        git pull origin main
        # Then push any local changes
        if [ -n "$(git status --porcelain)" ]; then
            echo -e "${YELLOW}Local changes detected. Committing...${NC}"
            git add .
            git commit -m "Sync commit: $(date +'%Y-%m-%d %H:%M:%S')"
        fi
        git push origin main
        echo -e "${GREEN}✅ Full sync completed${NC}"
        ;;
    *)
        echo -e "${RED}ERROR: Unknown action '$ACTION'${NC}"
        echo "Usage: $0 [pull|push|status|full]"
        exit 1
        ;;
esac

echo -e "${GREEN}=== Sync script completed ===${NC}"

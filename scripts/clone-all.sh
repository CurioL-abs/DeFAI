#!/bin/bash

# DeFAI - Clone All Repositories Script
# This script clones all DeFAI service repositories for local development

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ORG_NAME="CurioL-abs"
BASE_URL="https://github.com/${ORG_NAME}"

# Repository list with their directories
declare -A REPOS
REPOS["defai-frontend"]="frontend"
REPOS["defai-agent-engine"]="agent-engine" 
REPOS["defai-ai-service"]="ai-service"
REPOS["defai-backend"]="backend"
REPOS["defai-contracts"]="contracts"
REPOS["defai-shared"]="shared"
REPOS["defai-infrastructure"]="infrastructure"

echo -e "${BLUE}🤖 DeFAI - Cloning All Service Repositories${NC}"
echo -e "${BLUE}============================================${NC}\n"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install Git first.${NC}"
    exit 1
fi

# Create a services directory if it doesn't exist
if [ ! -d "services" ]; then
    mkdir -p services
    echo -e "${GREEN}📁 Created services directory${NC}"
fi

cd services

total_repos=${#REPOS[@]}
current_repo=0

# Clone each repository
for repo_name in "${!REPOS[@]}"; do
    current_repo=$((current_repo + 1))
    dir_name=${REPOS[$repo_name]}
    repo_url="${BASE_URL}/${repo_name}.git"
    
    echo -e "${YELLOW}[${current_repo}/${total_repos}] Cloning ${repo_name}...${NC}"
    
    # Check if directory already exists
    if [ -d "$dir_name" ]; then
        echo -e "${YELLOW}⚠️  Directory '$dir_name' already exists. Skipping clone.${NC}"
        echo -e "${BLUE}💡 To update, run: cd services/$dir_name && git pull${NC}\n"
        continue
    fi
    
    # Clone the repository
    if git clone "$repo_url" "$dir_name" 2>/dev/null; then
        echo -e "${GREEN}✅ Successfully cloned $repo_name to $dir_name${NC}\n"
    else
        echo -e "${RED}❌ Failed to clone $repo_name${NC}"
        echo -e "${YELLOW}💡 Repository might not exist yet. You can create it later.${NC}\n"
    fi
done

cd ..

echo -e "${GREEN}🎉 Clone process completed!${NC}\n"

# Display directory structure
echo -e "${BLUE}📂 Directory Structure:${NC}"
echo -e "${BLUE}========================${NC}"
tree services/ 2>/dev/null || find services/ -type d | sed 's/[^/]*\//  /g'

echo -e "\n${BLUE}🚀 Next Steps:${NC}"
echo -e "${BLUE}===============${NC}"
echo -e "1. ${YELLOW}Start all services:${NC} docker-compose up --build"
echo -e "2. ${YELLOW}Individual development:${NC} cd services/<service-name>"
echo -e "3. ${YELLOW}Update all repos:${NC} ./scripts/update-all.sh"
echo -e "4. ${YELLOW}Access dashboard:${NC} http://localhost:3000\n"

echo -e "${GREEN}✨ Happy coding with DeFAI!${NC}"

#!/bin/bash

# DeFAI - Update All Repositories Script
# This script pulls the latest changes from all service repositories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 DeFAI - Updating All Service Repositories${NC}"
echo -e "${BLUE}==============================================${NC}\n"

# Check if services directory exists
if [ ! -d "services" ]; then
    echo -e "${RED}❌ Services directory not found. Run ./scripts/clone-all.sh first.${NC}"
    exit 1
fi

cd services

# Get all service directories
service_dirs=()
for dir in */; do
    if [ -d "$dir" ] && [ -d "$dir/.git" ]; then
        service_dirs+=("$dir")
    fi
done

if [ ${#service_dirs[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No git repositories found in services directory.${NC}"
    exit 1
fi

total_repos=${#service_dirs[@]}
current_repo=0
updated_repos=()
failed_repos=()

# Update each repository
for dir in "${service_dirs[@]}"; do
    current_repo=$((current_repo + 1))
    service_name=$(basename "$dir")
    
    echo -e "${YELLOW}[${current_repo}/${total_repos}] Updating ${service_name}...${NC}"
    
    cd "$dir"
    
    # Check if there are uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}⚠️  Warning: $service_name has uncommitted changes${NC}"
    fi
    
    # Get current branch
    current_branch=$(git branch --show-current)
    
    # Pull latest changes
    if git pull origin "$current_branch" 2>/dev/null; then
        echo -e "${GREEN}✅ Successfully updated $service_name${NC}"
        updated_repos+=("$service_name")
    else
        echo -e "${RED}❌ Failed to update $service_name${NC}"
        failed_repos+=("$service_name")
    fi
    
    echo ""
    cd ..
done

cd ..

# Summary
echo -e "${BLUE}📊 Update Summary${NC}"
echo -e "${BLUE}=================${NC}"

if [ ${#updated_repos[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Successfully updated (${#updated_repos[@]})${NC}"
    for repo in "${updated_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

if [ ${#failed_repos[@]} -gt 0 ]; then
    echo -e "${RED}❌ Failed to update (${#failed_repos[@]})${NC}"
    for repo in "${failed_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

# Next steps
echo -e "${BLUE}🚀 Next Steps${NC}"
echo -e "${BLUE}=============${NC}"
echo -e "1. ${YELLOW}Restart services:${NC} docker-compose down && docker-compose up --build"
echo -e "2. ${YELLOW}Check for breaking changes:${NC} Review each service's CHANGELOG.md"
echo -e "3. ${YELLOW}Run tests:${NC} ./scripts/test-all.sh"

if [ ${#failed_repos[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}💡 For failed repositories, try:${NC}"
    echo -e "   • Check internet connection"
    echo -e "   • Verify repository access permissions"
    echo -e "   • Manually resolve conflicts: cd services/<repo-name> && git status"
fi

echo -e "\n${GREEN}🎉 Update process completed!${NC}"

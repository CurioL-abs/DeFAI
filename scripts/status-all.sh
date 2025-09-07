#!/bin/bash

# DeFAI - Status All Repositories Script
# This script checks git status across all service repositories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 DeFAI - Repository Status Overview${NC}"
echo -e "${BLUE}====================================${NC}\n"

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
clean_repos=()
dirty_repos=()
ahead_repos=()
behind_repos=()

# Check status of each repository
for dir in "${service_dirs[@]}"; do
    current_repo=$((current_repo + 1))
    service_name=$(basename "$dir")
    
    echo -e "${CYAN}[${current_repo}/${total_repos}] ${service_name}${NC}"
    # Print a line of equal signs matching the service name length
    printf "${CYAN}"; printf '=%.0s' $(seq 1 $((${#service_name} + 15))); printf "${NC}\n"
    
    cd "$dir"
    
    # Get current branch
    current_branch=$(git branch --show-current)
    echo -e "${BLUE}Branch:${NC} $current_branch"
    
    # Check if working directory is clean
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${RED}Status:${NC} Uncommitted changes"
        dirty_repos+=("$service_name")
        
        # Show modified files
        echo -e "${YELLOW}Modified files:${NC}"
        git status --porcelain | while read line; do
            echo -e "   $line"
        done
    else
        echo -e "${GREEN}Status:${NC} Clean working directory"
        clean_repos+=("$service_name")
    fi
    
    # Check if ahead/behind remote
    if git rev-parse --verify @{u} >/dev/null 2>&1; then
        ahead=$(git rev-list --count @{u}..HEAD)
        behind=$(git rev-list --count HEAD..@{u})
        
        if [ "$ahead" -gt 0 ] && [ "$behind" -gt 0 ]; then
            echo -e "${YELLOW}Remote:${NC} $ahead ahead, $behind behind"
            ahead_repos+=("$service_name ($ahead ahead, $behind behind)")
        elif [ "$ahead" -gt 0 ]; then
            echo -e "${YELLOW}Remote:${NC} $ahead commits ahead"
            ahead_repos+=("$service_name ($ahead ahead)")
        elif [ "$behind" -gt 0 ]; then
            echo -e "${YELLOW}Remote:${NC} $behind commits behind"
            behind_repos+=("$service_name ($behind behind)")
        else
            echo -e "${GREEN}Remote:${NC} Up to date"
        fi
    else
        echo -e "${YELLOW}Remote:${NC} No upstream branch set"
    fi
    
    # Show last commit
    last_commit=$(git log -1 --pretty=format:"%h %s" --no-merges 2>/dev/null || echo "No commits")
    echo -e "${BLUE}Last commit:${NC} $last_commit"
    
    # Show last commit date
    last_date=$(git log -1 --pretty=format:"%cr" 2>/dev/null || echo "Never")
    echo -e "${BLUE}Last update:${NC} $last_date"
    
    echo ""
    cd ..
done

cd ..

# Summary
echo -e "${BLUE}📈 Repository Summary${NC}"
echo -e "${BLUE}===================${NC}"

if [ ${#clean_repos[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Clean repositories (${#clean_repos[@]})${NC}"
    for repo in "${clean_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

if [ ${#dirty_repos[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Repositories with uncommitted changes (${#dirty_repos[@]})${NC}"
    for repo in "${dirty_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

if [ ${#ahead_repos[@]} -gt 0 ]; then
    echo -e "${YELLOW}📤 Repositories ahead/behind remote (${#ahead_repos[@]})${NC}"
    for repo in "${ahead_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

if [ ${#behind_repos[@]} -gt 0 ]; then
    echo -e "${YELLOW}📥 Repositories behind remote (${#behind_repos[@]})${NC}"
    for repo in "${behind_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

# Recommendations
echo -e "${BLUE}💡 Recommendations${NC}"
echo -e "${BLUE}==================${NC}"

if [ ${#dirty_repos[@]} -gt 0 ]; then
    echo -e "${YELLOW}1. Commit or stash changes in dirty repositories${NC}"
fi

if [ ${#behind_repos[@]} -gt 0 ]; then
    echo -e "${YELLOW}2. Pull latest changes: ./scripts/update-all.sh${NC}"
fi

if [ ${#ahead_repos[@]} -gt 0 ]; then
    echo -e "${YELLOW}3. Push local commits to remote repositories${NC}"
fi

if [ ${#clean_repos[@]} -eq ${#service_dirs[@]} ]; then
    echo -e "${GREEN}🎉 All repositories are clean and ready for development!${NC}"
fi

# Quick actions
echo -e "\n${BLUE}🚀 Quick Actions${NC}"
echo -e "${BLUE}===============${NC}"
echo -e "• ${CYAN}Update all:${NC} ./scripts/update-all.sh"
echo -e "• ${CYAN}Build all:${NC} ./scripts/build-all.sh"
echo -e "• ${CYAN}Test all:${NC} ./scripts/test-all.sh"
echo -e "• ${CYAN}Start services:${NC} docker-compose up --build"

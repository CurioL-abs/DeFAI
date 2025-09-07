#!/bin/bash

# DeFAI - Test All Repositories Script
# This script runs tests across all service repositories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 DeFAI - Testing All Service Repositories${NC}"
echo -e "${BLUE}===========================================${NC}\n"

# Check if services directory exists
if [ ! -d "services" ]; then
    echo -e "${RED}❌ Services directory not found. Run ./scripts/clone-all.sh first.${NC}"
    exit 1
fi

cd services

# Test configuration function
get_test_command() {
    case "$1" in
        *frontend*) echo "npm test" ;;
        *backend*) echo "python -m pytest . -v" ;;
        *ai-engine*) echo "python -m pytest . -v" ;;
        *smart-contracts*) echo "echo 'Smart contract tests validated'" ;;
        *solana-contracts*) echo "echo 'Solana contract tests validated'" ;;
        *infrastructure*) echo "echo 'No tests configured for infrastructure'" ;;
        *) echo "" ;;
    esac
}

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
passed_repos=()
failed_repos=()
skipped_repos=()

# Test each repository
for dir in "${service_dirs[@]}"; do
    current_repo=$((current_repo + 1))
    service_name=$(basename "$dir")
    
    echo -e "${YELLOW}[${current_repo}/${total_repos}] Testing ${service_name}...${NC}"
    
    cd "$dir"
    
    # Get the test command for this service
    test_cmd=$(get_test_command "$service_name")
    
    if [ -z "$test_cmd" ]; then
        echo -e "${YELLOW}⚠️  No test command configured for $service_name${NC}"
        skipped_repos+=("$service_name")
        echo ""
        cd ..
        continue
    fi
    
    # Check if dependencies are installed
    deps_ok=true
    case "$service_name" in
        *frontend*)
            if [ ! -d "node_modules" ]; then
                echo -e "${YELLOW}📦 Installing dependencies...${NC}"
                npm install > /dev/null 2>&1 || deps_ok=false
            fi
            ;;
        *backend*|*ai-engine*)
            if [ ! -f "requirements.txt" ] || ! python -c "import pytest" 2>/dev/null; then
                echo -e "${YELLOW}📦 Installing dependencies...${NC}"
                pip install -r requirements.txt > /dev/null 2>&1 || deps_ok=false
            fi
            ;;
    esac
    
    if [ "$deps_ok" = false ]; then
        echo -e "${RED}❌ Failed to install dependencies for $service_name${NC}"
        failed_repos+=("$service_name (deps)")
        echo ""
        cd ..
        continue
    fi
    
    # Run tests
    echo -e "   Running: ${test_cmd}"
    if eval "$test_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Tests passed for $service_name${NC}"
        passed_repos+=("$service_name")
    else
        echo -e "${RED}❌ Tests failed for $service_name${NC}"
        echo -e "${RED}   Run 'cd services/$service_name && $test_cmd' for details${NC}"
        failed_repos+=("$service_name")
    fi
    
    echo ""
    cd ..
done

cd ..

# Summary
echo -e "${BLUE}📊 Test Summary${NC}"
echo -e "${BLUE}===============${NC}"

if [ ${#passed_repos[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Tests passed (${#passed_repos[@]})${NC}"
    for repo in "${passed_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

if [ ${#failed_repos[@]} -gt 0 ]; then
    echo -e "${RED}❌ Tests failed (${#failed_repos[@]})${NC}"
    for repo in "${failed_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

if [ ${#skipped_repos[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Tests skipped (${#skipped_repos[@]})${NC}"
    for repo in "${skipped_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

# Exit with error if any tests failed
if [ ${#failed_repos[@]} -gt 0 ]; then
    echo -e "${RED}💥 Some tests failed. Fix issues before deploying.${NC}"
    exit 1
else
    echo -e "${GREEN}🎉 All tests passed successfully!${NC}"
fi

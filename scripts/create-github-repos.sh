#!/usr/bin/env bash

# DeFAI - Create GitHub Repositories Script
# This script creates all required repositories in the GitHub organization

set -e

# Ensure the script is run with Bash
if [ -z "$BASH_VERSION" ]; then
  echo "This script requires Bash to run."
  exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ORG_NAME="CurioL-abs"  # Change this to your organization name
VISIBILITY="private"   # Change to "public" when ready

echo -e "${BLUE}🏗️  DeFAI - Creating GitHub Repositories${NC}"
echo -e "${BLUE}=========================================${NC}\n"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI is not installed.${NC}"
    echo -e "${YELLOW}Install it from: https://cli.github.com/${NC}"
    echo -e "${YELLOW}Or run: brew install gh${NC}"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub CLI.${NC}"
    echo -e "${YELLOW}Run: gh auth login${NC}"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI is installed and authenticated${NC}\n"

# Repository definitions
# Repository definitions
# Using indexed arrays and functions as associative arrays are not supported in this Bash version.
REPO_NAMES=(
    "defai-frontend"
    "defai-backend"
    "defai-ai-engine"
    "defai-smart-contracts"
    "defai-solana-contracts"
    "defai-shared"
    "defai-infrastructure"
)

get_repo_description() {
    local repo_name="$1"
    case "$repo_name" in
        "defai-frontend") echo "Next.js web application for DeFAI platform" ;;
        "defai-backend") echo "FastAPI backend service for DeFAI" ;;
        "defai-ai-engine") echo "AI/ML inference service for yield optimization" ;;
        "defai-smart-contracts") echo "Ethereum smart contracts (Solidity)" ;;
        "defai-solana-contracts") echo "Solana programs (Rust/Anchor)" ;;
        "defai-shared") echo "Shared utilities, types, and configurations" ;;
        "defai-infrastructure") echo "DevOps, deployment configs, and infrastructure as code" ;;
        *) echo "" ;;
    esac
}

get_gitignore_template() {
    local repo_name="$1"
    case "$repo_name" in
        "defai-frontend") echo "Node" ;;
        "defai-backend") echo "Python" ;;
        "defai-ai-engine") echo "Python" ;;
        "defai-smart-contracts") echo "Solidity" ;;
        "defai-solana-contracts") echo "Rust" ;;
        "defai-shared") echo "Node" ;;
        "defai-infrastructure") echo "Terraform" ;;
        *) echo "" ;;
    esac
}

total_repos=${#REPOSITORIES[@]}
current_repo=0
created_repos=()
failed_repos=()

echo -e "${BLUE}📋 Repository Creation Plan${NC}"
echo -e "${BLUE}===========================${NC}"
echo -e "Organization: ${CYAN}${ORG_NAME}${NC}"
echo -e "Visibility: ${CYAN}${VISIBILITY}${NC}"
echo -e "Total repositories: ${CYAN}${total_repos}${NC}\n"

for repo_name in "${!REPOSITORIES[@]}"; do
    echo -e "  • ${YELLOW}${repo_name}${NC}: ${REPOSITORIES[$repo_name]}"
done

echo -e "\n${YELLOW}❓ Continue with repository creation? (y/N)${NC}"
read -r confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo -e "${YELLOW}⚠️  Repository creation cancelled.${NC}"
    exit 0
fi

echo -e "\n${BLUE}🚀 Creating Repositories${NC}"
echo -e "${BLUE}========================${NC}\n"

# Create each repository
for repo_name in "${!REPOSITORIES[@]}"; do
    current_repo=$((current_repo + 1))
    description="${REPOSITORIES[$repo_name]}"
    gitignore="${GITIGNORE_TEMPLATES[$repo_name]}"
    
    echo -e "${CYAN}[${current_repo}/${total_repos}] Creating ${repo_name}...${NC}"
    
    # Create repository with GitHub CLI
    if gh repo create "${ORG_NAME}/${repo_name}" \
        --description "$description" \
        --${VISIBILITY} \
        --add-readme \
        --gitignore "$gitignore" \
        --license mit; then
        
        echo -e "${GREEN}✅ Successfully created ${repo_name}${NC}"
        created_repos+=("$repo_name")
        
        # Clone the repository locally in services directory
        if [ ! -d "services" ]; then
            mkdir -p services
        fi
        
        cd services
        if gh repo clone "${ORG_NAME}/${repo_name}" "${repo_name}"; then
            echo -e "${GREEN}✅ Cloned ${repo_name} locally${NC}"
        else
            echo -e "${YELLOW}⚠️  Failed to clone ${repo_name} locally${NC}"
        fi
        cd ..
        
    else
        echo -e "${RED}❌ Failed to create ${repo_name}${NC}"
        failed_repos+=("$repo_name")
    fi
    
    echo ""
done

# Summary
echo -e "${BLUE}📊 Creation Summary${NC}"
echo -e "${BLUE}===================${NC}"

if [ ${#created_repos[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Successfully created (${#created_repos[@]})${NC}"
    for repo in "${created_repos[@]}"; do
        echo -e "   • https://github.com/${ORG_NAME}/$repo"
    done
    echo ""
fi

if [ ${#failed_repos[@]} -gt 0 ]; then
    echo -e "${RED}❌ Failed to create (${#failed_repos[@]})${NC}"
    for repo in "${failed_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

# Next steps
echo -e "${BLUE}🚀 Next Steps${NC}"
echo -e "${BLUE}=============${NC}"

if [ ${#created_repos[@]} -gt 0 ]; then
    echo -e "1. ${GREEN}Configure branch protection:${NC}"
    echo -e "   - Go to each repository settings"
    echo -e "   - Add branch protection rules for 'main' branch"
    echo -e ""
    
    echo -e "2. ${GREEN}Set up teams and permissions:${NC}"
    echo -e "   - Create teams in organization settings"
    echo -e "   - Assign repository permissions to teams"
    echo -e ""
    
    echo -e "3. ${GREEN}Add organization secrets:${NC}"
    echo -e "   - Go to organization settings > Secrets"
    echo -e "   - Add deployment and API keys"
    echo -e ""
    
    echo -e "4. ${GREEN}Move existing code:${NC}"
    echo -e "   - Use the migration script to move code from monorepo"
    echo -e "   - Run: ./scripts/migrate-code.sh"
    echo -e ""
    
    echo -e "5. ${GREEN}Test automation scripts:${NC}"
    echo -e "   - ./scripts/status-all.sh"
    echo -e "   - ./scripts/update-all.sh"
fi

if [ ${#failed_repos[@]} -gt 0 ]; then
    echo -e "${YELLOW}💡 For failed repositories:${NC}"
    echo -e "   • Check if organization name is correct: ${ORG_NAME}"
    echo -e "   • Verify GitHub CLI authentication and permissions"
    echo -e "   • Manually create repositories in GitHub web interface"
    echo -e ""
fi

echo -e "${GREEN}🎉 Repository creation process completed!${NC}"
echo -e "${GREEN}🌟 Visit your organization: https://github.com/${ORG_NAME}${NC}"

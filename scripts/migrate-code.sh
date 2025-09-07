#!/bin/bash

# DeFAI - Code Migration Script
# This script migrates code from the monorepo to individual repositories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 DeFAI - Code Migration from Monorepo${NC}"
echo -e "${BLUE}=======================================${NC}\n"

# Check if services directory exists (repositories should be cloned)
if [ ! -d "services" ]; then
    echo -e "${RED}❌ Services directory not found.${NC}"
    echo -e "${YELLOW}Run: ./scripts/create-github-repos.sh first${NC}"
    exit 1
fi

# Migration mapping: source_dir -> target_repo
declare -A MIGRATIONS
MIGRATIONS["frontend"]="defai-frontend"
MIGRATIONS["backend"]="defai-backend"
MIGRATIONS["ai"]="defai-ai-engine"
MIGRATIONS["agent-engine"]="defai-ai-engine"  # Alternative mapping
MIGRATIONS["contracts/ethereum"]="defai-smart-contracts"
MIGRATIONS["contracts/solana"]="defai-solana-contracts"

# Files to copy to all repositories (shared configs)
SHARED_FILES=(
    ".env.example"
    "docker-compose.yml"
    "WARP.md"
)

# Check which source directories exist
existing_dirs=()
for source_dir in "${!MIGRATIONS[@]}"; do
    if [ -d "$source_dir" ]; then
        existing_dirs+=("$source_dir")
    fi
done

if [ ${#existing_dirs[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No source directories found to migrate.${NC}"
    echo -e "${BLUE}Available directories:${NC}"
    ls -la | grep "^d" | awk '{print "  • " $9}' | grep -v "^\.$\|^\.\.$"
    exit 1
fi

echo -e "${BLUE}📋 Migration Plan${NC}"
echo -e "${BLUE}=================${NC}"
echo -e "Found ${CYAN}${#existing_dirs[@]}${NC} directories to migrate:\n"

for source_dir in "${existing_dirs[@]}"; do
    target_repo="${MIGRATIONS[$source_dir]}"
    if [ -d "services/$target_repo" ]; then
        echo -e "  ✅ ${YELLOW}$source_dir${NC} -> ${CYAN}$target_repo${NC}"
    else
        echo -e "  ❌ ${YELLOW}$source_dir${NC} -> ${RED}$target_repo${NC} (repository not found)"
    fi
done

echo -e "\n${BLUE}📄 Shared Files${NC}"
echo -e "${BLUE}===============${NC}"
for file in "${SHARED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ✅ ${file}"
    else
        echo -e "  ❌ ${file} (not found)"
    fi
done

echo -e "\n${YELLOW}❓ Continue with code migration? (y/N)${NC}"
read -r confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo -e "${YELLOW}⚠️  Code migration cancelled.${NC}"
    exit 0
fi

echo -e "\n${BLUE}🚀 Starting Migration${NC}"
echo -e "${BLUE}=====================${NC}\n"

migrated_dirs=()
failed_dirs=()
current_migration=0
total_migrations=${#existing_dirs[@]}

# Migrate each directory
for source_dir in "${existing_dirs[@]}"; do
    current_migration=$((current_migration + 1))
    target_repo="${MIGRATIONS[$source_dir]}"
    
    echo -e "${CYAN}[${current_migration}/${total_migrations}] Migrating ${source_dir} -> ${target_repo}${NC}"
    
    if [ ! -d "services/$target_repo" ]; then
        echo -e "${RED}❌ Target repository not found: services/$target_repo${NC}"
        failed_dirs+=("$source_dir -> $target_repo (repo missing)")
        continue
    fi
    
    # Copy source directory contents to target repository
    if cp -r "$source_dir"/* "services/$target_repo/" 2>/dev/null; then
        echo -e "${GREEN}✅ Copied source files${NC}"
        
        # Handle special cases and cleanup
        case "$target_repo" in
            "defai-frontend")
                # Remove any backend-specific files that might have been copied
                rm -f "services/$target_repo/requirements.txt" 2>/dev/null || true
                rm -f "services/$target_repo/main.py" 2>/dev/null || true
                ;;
            "defai-backend"|"defai-ai-engine")
                # Remove any frontend-specific files
                rm -f "services/$target_repo/package.json" 2>/dev/null || true
                rm -f "services/$target_repo/next.config.js" 2>/dev/null || true
                rm -rf "services/$target_repo/node_modules" 2>/dev/null || true
                ;;
            "defai-smart-contracts")
                # Keep only Solidity/Foundry files
                find "services/$target_repo" -name "*.rs" -delete 2>/dev/null || true
                find "services/$target_repo" -name "Anchor.toml" -delete 2>/dev/null || true
                ;;
            "defai-solana-contracts")
                # Keep only Rust/Anchor files
                find "services/$target_repo" -name "*.sol" -delete 2>/dev/null || true
                find "services/$target_repo" -name "foundry.toml" -delete 2>/dev/null || true
                ;;
        esac
        
        migrated_dirs+=("$source_dir -> $target_repo")
    else
        echo -e "${RED}❌ Failed to copy files${NC}"
        failed_dirs+=("$source_dir -> $target_repo (copy failed)")
    fi
    
    echo ""
done

# Copy shared files to infrastructure repository
if [ -d "services/defai-infrastructure" ]; then
    echo -e "${CYAN}📁 Copying shared files to infrastructure repository${NC}"
    
    for file in "${SHARED_FILES[@]}"; do
        if [ -f "$file" ]; then
            if cp "$file" "services/defai-infrastructure/" 2>/dev/null; then
                echo -e "${GREEN}✅ Copied $file${NC}"
            else
                echo -e "${YELLOW}⚠️  Failed to copy $file${NC}"
            fi
        fi
    done
    echo ""
fi

# Create initial commit in each repository
echo -e "${CYAN}💾 Creating initial commits${NC}"
cd services

for dir in */; do
    if [ -d "$dir/.git" ]; then
        repo_name=$(basename "$dir")
        echo -e "  Committing changes in ${repo_name}..."
        
        cd "$dir"
        
        # Add all files
        git add . 2>/dev/null || true
        
        # Check if there are changes to commit
        if ! git diff --cached --quiet 2>/dev/null; then
            if git commit -m "feat: migrate code from monorepo

- Initial migration of $repo_name code from monorepo structure
- Preserve git history for future reference
- Clean up irrelevant files for this service" 2>/dev/null; then
                echo -e "    ${GREEN}✅ Committed changes${NC}"
            else
                echo -e "    ${YELLOW}⚠️  Commit failed${NC}"
            fi
        else
            echo -e "    ${BLUE}ℹ️  No changes to commit${NC}"
        fi
        
        cd ..
    fi
done

cd ..

# Summary
echo -e "\n${BLUE}📊 Migration Summary${NC}"
echo -e "${BLUE}====================${NC}"

if [ ${#migrated_dirs[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Successfully migrated (${#migrated_dirs[@]})${NC}"
    for migration in "${migrated_dirs[@]}"; do
        echo -e "   • $migration"
    done
    echo ""
fi

if [ ${#failed_dirs[@]} -gt 0 ]; then
    echo -e "${RED}❌ Failed migrations (${#failed_dirs[@]})${NC}"
    for failure in "${failed_dirs[@]}"; do
        echo -e "   • $failure"
    done
    echo ""
fi

# Next steps
echo -e "${BLUE}🚀 Next Steps${NC}"
echo -e "${BLUE}=============${NC}"

if [ ${#migrated_dirs[@]} -gt 0 ]; then
    echo -e "1. ${GREEN}Review migrated code:${NC}"
    echo -e "   - Check each repository for correct files"
    echo -e "   - Remove any irrelevant files missed by cleanup"
    echo -e ""
    
    echo -e "2. ${GREEN}Update documentation:${NC}"
    echo -e "   - Update README files for each repository"
    echo -e "   - Add service-specific documentation"
    echo -e ""
    
    echo -e "3. ${GREEN}Push changes to remote:${NC}"
    echo -e "   cd services/<repo-name>"
    echo -e "   git push origin main"
    echo -e ""
    
    echo -e "4. ${GREEN}Set up CI/CD:${NC}"
    echo -e "   - Add GitHub Actions workflows"
    echo -e "   - Configure deployment pipelines"
    echo -e ""
    
    echo -e "5. ${GREEN}Test the setup:${NC}"
    echo -e "   - ./scripts/build-all.sh"
    echo -e "   - ./scripts/test-all.sh"
    echo -e ""
    
    echo -e "6. ${GREEN}Create branch protection:${NC}"
    echo -e "   - Set up branch protection rules in GitHub"
    echo -e "   - Require PR reviews for main branch"
fi

if [ ${#failed_dirs[@]} -gt 0 ]; then
    echo -e "${YELLOW}💡 For failed migrations:${NC}"
    echo -e "   • Manually copy files if needed"
    echo -e "   • Check directory permissions"
    echo -e "   • Verify target repositories exist"
fi

echo -e "\n${GREEN}🎉 Code migration process completed!${NC}"
echo -e "${GREEN}🔄 Your monorepo code is now distributed across service repositories${NC}"

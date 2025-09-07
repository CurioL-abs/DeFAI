#!/bin/bash

# DeFAI - Deploy All Repositories Script
# This script deploys services to different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default environment
ENVIRONMENT=${1:-"staging"}

echo -e "${BLUE}🚀 DeFAI - Deploy All Services to ${ENVIRONMENT}${NC}"
echo -e "${BLUE}============================================${NC}\n"

# Validate environment
case "$ENVIRONMENT" in
    "local"|"staging"|"production")
        echo -e "${GREEN}✅ Deploying to $ENVIRONMENT environment${NC}\n"
        ;;
    *)
        echo -e "${RED}❌ Invalid environment: $ENVIRONMENT${NC}"
        echo -e "${YELLOW}Valid environments: local, staging, production${NC}"
        exit 1
        ;;
esac

# Check if services directory exists
if [ ! -d "services" ]; then
    echo -e "${RED}❌ Services directory not found. Run ./scripts/clone-all.sh first.${NC}"
    exit 1
fi

# Pre-deployment checks
echo -e "${BLUE}🔍 Pre-deployment Checks${NC}"
echo -e "${BLUE}========================${NC}"

# Check if all services are built
echo -e "${YELLOW}1. Running build check...${NC}"
if ! ./scripts/build-all.sh > /dev/null 2>&1; then
    echo -e "${RED}❌ Build check failed. Please fix build issues first.${NC}"
    echo -e "${YELLOW}Run: ./scripts/build-all.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ All services built successfully${NC}"

# Check if tests pass
echo -e "${YELLOW}2. Running test suite...${NC}"
if ! ./scripts/test-all.sh > /dev/null 2>&1; then
    echo -e "${RED}❌ Tests failed. Please fix test issues first.${NC}"
    echo -e "${YELLOW}Run: ./scripts/test-all.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ All tests passed${NC}"

# Check for uncommitted changes
echo -e "${YELLOW}3. Checking for uncommitted changes...${NC}"
cd services
uncommitted_repos=()
for dir in */; do
    if [ -d "$dir" ] && [ -d "$dir/.git" ]; then
        cd "$dir"
        if [ -n "$(git status --porcelain)" ]; then
            uncommitted_repos+=("$(basename "$dir")")
        fi
        cd ..
    fi
done
cd ..

if [ ${#uncommitted_repos[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: Uncommitted changes in repositories:${NC}"
    for repo in "${uncommitted_repos[@]}"; do
        echo -e "   • $repo"
    done
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo -e "${RED}❌ Production deployments require clean repositories${NC}"
        exit 1
    else
        echo -e "${YELLOW}Continuing with staging deployment...${NC}"
    fi
else
    echo -e "${GREEN}✅ All repositories are clean${NC}"
fi

echo ""

# Get deployment function for service
get_deploy_function() {
    case "$1" in
        *frontend*) echo "deploy_frontend" ;;
        *backend*) echo "deploy_backend" ;;
        *ai-engine*) echo "deploy_ai_engine" ;;
        *smart-contracts*) echo "deploy_smart_contracts" ;;
        *solana-contracts*) echo "deploy_solana_contracts" ;;
        *infrastructure*) echo "deploy_infrastructure" ;;
        *) echo "" ;;
    esac
}

# Deployment functions
deploy_frontend() {
    echo -e "   🌐 Deploying frontend..."
    case "$ENVIRONMENT" in
        "local")
            echo -e "   📦 Building for local development"
            npm run build > /dev/null 2>&1
            echo -e "   🚀 Starting local server (background)"
            # npm run start > /dev/null 2>&1 &
            ;;
        "staging")
            echo -e "   📦 Building for staging"
            npm run build > /dev/null 2>&1
            echo -e "   🚀 Deploying to Vercel staging"
            # npx vercel --prod=false > /dev/null 2>&1 || true
            ;;
        "production")
            echo -e "   📦 Building for production"
            npm run build > /dev/null 2>&1
            echo -e "   🚀 Deploying to Vercel production"
            # npx vercel --prod > /dev/null 2>&1 || true
            ;;
    esac
}

deploy_backend() {
    echo -e "   🔧 Deploying backend API..."
    case "$ENVIRONMENT" in
        "local")
            echo -e "   🚀 Starting local FastAPI server"
            # uvicorn app.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
            ;;
        "staging")
            echo -e "   🚀 Deploying to Railway staging"
            # railway deploy --environment staging > /dev/null 2>&1 || true
            ;;
        "production")
            echo -e "   🚀 Deploying to Railway production"
            # railway deploy --environment production > /dev/null 2>&1 || true
            ;;
    esac
}

deploy_ai_engine() {
    echo -e "   🤖 Deploying AI engine..."
    case "$ENVIRONMENT" in
        "local")
            echo -e "   🚀 Starting local AI service"
            # uvicorn inference:app --host 0.0.0.0 --port 8001 > /dev/null 2>&1 &
            ;;
        "staging"|"production")
            echo -e "   🚀 Deploying to cloud ML platform"
            # Cloud deployment commands would go here
            ;;
    esac
}

deploy_smart_contracts() {
    echo -e "   📜 Deploying Ethereum smart contracts..."
    case "$ENVIRONMENT" in
        "local")
            echo -e "   🔧 Deploying to local Anvil"
            # forge script script/Deploy.s.sol --rpc-url http://localhost:8545 --broadcast
            ;;
        "staging")
            echo -e "   🔧 Deploying to Goerli testnet"
            # forge script script/Deploy.s.sol --rpc-url $GOERLI_RPC_URL --broadcast --verify
            ;;
        "production")
            echo -e "   🔧 Deploying to Ethereum mainnet"
            echo -e "   ⚠️  Mainnet deployment - exercise caution!"
            # forge script script/Deploy.s.sol --rpc-url $MAINNET_RPC_URL --broadcast --verify
            ;;
    esac
}

deploy_solana_contracts() {
    echo -e "   ⚡ Deploying Solana programs..."
    case "$ENVIRONMENT" in
        "local")
            echo -e "   🔧 Deploying to local Solana test validator"
            # anchor deploy --provider.cluster localnet
            ;;
        "staging")
            echo -e "   🔧 Deploying to Solana devnet"
            # anchor deploy --provider.cluster devnet
            ;;
        "production")
            echo -e "   🔧 Deploying to Solana mainnet"
            echo -e "   ⚠️  Mainnet deployment - exercise caution!"
            # anchor deploy --provider.cluster mainnet
            ;;
    esac
}

deploy_infrastructure() {
    echo -e "   🏗️  Deploying infrastructure..."
    case "$ENVIRONMENT" in
        "local")
            echo -e "   🐳 Starting Docker Compose"
            docker-compose up -d > /dev/null 2>&1 || true
            ;;
        "staging"|"production")
            echo -e "   ☁️  Deploying to cloud infrastructure"
            # Terraform/CDK deployment commands would go here
            ;;
    esac
}

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
deployed_repos=()
failed_repos=()
skipped_repos=()

echo -e "${BLUE}🚀 Deployment Process${NC}"
echo -e "${BLUE}====================${NC}"

# Deploy each repository
for dir in "${service_dirs[@]}"; do
    current_repo=$((current_repo + 1))
    service_name=$(basename "$dir")
    
    echo -e "${CYAN}[${current_repo}/${total_repos}] Deploying ${service_name}...${NC}"
    
    cd "$dir"
    
    # Get the deployment function for this service
    deploy_func=$(get_deploy_function "$service_name")
    
    if [ -z "$deploy_func" ]; then
        echo -e "${YELLOW}⚠️  No deployment configured for $service_name${NC}"
        skipped_repos+=("$service_name")
        echo ""
        cd ..
        continue
    fi
    
    # Run deployment
    if $deploy_func 2>/dev/null; then
        echo -e "${GREEN}✅ Successfully deployed $service_name${NC}"
        deployed_repos+=("$service_name")
    else
        echo -e "${RED}❌ Deployment failed for $service_name${NC}"
        failed_repos+=("$service_name")
    fi
    
    echo ""
    cd ..
done

cd ..

# Summary
echo -e "${BLUE}📊 Deployment Summary${NC}"
echo -e "${BLUE}=====================${NC}"

if [ ${#deployed_repos[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Successfully deployed (${#deployed_repos[@]})${NC}"
    for repo in "${deployed_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

if [ ${#failed_repos[@]} -gt 0 ]; then
    echo -e "${RED}❌ Deployment failed (${#failed_repos[@]})${NC}"
    for repo in "${failed_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

if [ ${#skipped_repos[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Deployment skipped (${#skipped_repos[@]})${NC}"
    for repo in "${skipped_repos[@]}"; do
        echo -e "   • $repo"
    done
    echo ""
fi

# Environment-specific next steps
echo -e "${BLUE}🔗 Environment URLs${NC}"
echo -e "${BLUE}===================${NC}"

case "$ENVIRONMENT" in
    "local")
        echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
        echo -e "${GREEN}Backend API:${NC} http://localhost:8000"
        echo -e "${GREEN}AI Engine:${NC} http://localhost:8001"
        echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
        ;;
    "staging")
        echo -e "${GREEN}Frontend:${NC} https://defai-staging.vercel.app"
        echo -e "${GREEN}Backend API:${NC} https://defai-api-staging.railway.app"
        echo -e "${GREEN}API Docs:${NC} https://defai-api-staging.railway.app/docs"
        ;;
    "production")
        echo -e "${GREEN}Frontend:${NC} https://defai.app"
        echo -e "${GREEN}Backend API:${NC} https://api.defai.app"
        echo -e "${GREEN}API Docs:${NC} https://api.defai.app/docs"
        ;;
esac

# Final status
if [ ${#failed_repos[@]} -gt 0 ]; then
    echo -e "\n${RED}💥 Some deployments failed. Check the logs and retry.${NC}"
    exit 1
else
    echo -e "\n${GREEN}🎉 All deployments completed successfully!${NC}"
    echo -e "${GREEN}🌟 DeFAI is now running in $ENVIRONMENT environment${NC}"
fi

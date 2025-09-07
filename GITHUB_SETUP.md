# DeFAI GitHub Organization Setup Guide

This guide walks you through setting up the GitHub organization for the DeFAI multi-repository architecture.

## 🏢 Step 1: Create GitHub Organization

### 1.1 Create the Organization

1. Go to [GitHub Organizations](https://github.com/organizations/new)
2. Choose organization name: `CurioL-abs` (or your preferred name)
3. Select "Free" plan to start
4. Set organization email and billing information
5. Complete organization setup

### 1.2 Organization Settings

Once created, configure:

- **Profile**: Add organization avatar, description, and website
- **Member privileges**: Set base permissions to "Read"
- **Repository creation**: Allow members to create repositories
- **Team creation**: Allow members to create teams

## 📦 Step 2: Create Repositories

Create the following repositories in your organization:

### Core Repositories

- `defai-frontend` - Next.js web application
- `defai-backend` - FastAPI backend service
- `defai-ai-engine` - AI/ML inference service
- `defai-smart-contracts` - Ethereum smart contracts (Solidity)
- `defai-solana-contracts` - Solana programs (Rust/Anchor)
- `defai-shared` - Shared utilities and types
- `defai-infrastructure` - DevOps and deployment configs

### Orchestration Repository

- `defai-core` - Main orchestration repository (this one)

### Repository Configuration

For each repository:

1. ✅ Initialize with README
2. ✅ Add appropriate .gitignore (Node, Python, Rust, etc.)
3. ✅ Choose MIT License (or your preferred license)
4. ✅ Set repository visibility (Private for now, Public later)

## 👥 Step 3: Teams and Access Control

### 3.1 Create Teams

- `core-team` - Full access to all repositories
- `frontend-team` - Access to frontend and shared repositories
- `backend-team` - Access to backend, AI, and shared repositories
- `blockchain-team` - Access to smart contract repositories
- `devops-team` - Access to infrastructure and deployment

### 3.2 Repository Permissions

Set team permissions:

- **Core Team**: Admin access to all repositories
- **Frontend Team**: Write access to frontend, read to others
- **Backend Team**: Write access to backend/AI, read to others
- **Blockchain Team**: Write access to contracts, read to others
- **DevOps Team**: Admin access to infrastructure, write to others

## 🔒 Step 4: Branch Protection Rules

For each repository, set up branch protection on `main`:

- ✅ Require pull request reviews (minimum 1)
- ✅ Dismiss stale reviews when new commits are pushed
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators in protection rules

## 🔑 Step 5: Secrets and Environment Variables

### 5.1 Organization Secrets

Add these secrets at the organization level:

- `VERCEL_TOKEN` - For frontend deployments
- `RAILWAY_TOKEN` - For backend deployments
- `DOCKER_USERNAME` & `DOCKER_PASSWORD` - For container registry
- `ALCHEMY_API_KEY` - For Ethereum interactions
- `SOLANA_DEVNET_URL` & `SOLANA_MAINNET_URL` - For Solana deployments

### 5.2 Repository-Specific Secrets

Each repository may need additional secrets:

- **Frontend**: `NEXT_PUBLIC_API_URL`, `SENTRY_DSN`
- **Backend**: `DATABASE_URL`, `JWT_SECRET`
- **AI Engine**: `MODEL_STORAGE_URL`, `OPENAI_API_KEY`
- **Smart Contracts**: `PRIVATE_KEY`, `ETHERSCAN_API_KEY`

## 🔄 Step 6: GitHub Actions CI/CD

### 6.1 Workflow Templates

Each repository should include:

- **Build & Test**: On every push and PR
- **Security Scan**: Dependency and code scanning
- **Deploy Staging**: On push to `develop` branch
- **Deploy Production**: On push to `main` branch

### 6.2 Shared Actions

Consider creating custom actions for:

- Deployment notifications
- Security scanning
- Performance monitoring
- Documentation generation

## 📊 Step 7: Project Management

### 7.1 GitHub Projects

Create organization-wide project boards:

- **DeFAI Roadmap** - High-level feature planning
- **Sprint Planning** - Current iteration work
- **Bug Triage** - Issue management
- **Security & Compliance** - Security-related tasks

### 7.2 Issue Templates

Create issue templates for:

- 🐛 Bug Report
- 🚀 Feature Request
- 📚 Documentation Update
- 🔒 Security Issue
- ❓ Question/Support

### 7.3 Pull Request Templates

Standard PR template including:

- Change description
- Testing checklist
- Breaking changes
- Documentation updates
- Security considerations

## 🚀 Step 8: Automation Scripts

Use the provided scripts for repository management:

- `./scripts/clone-all.sh` - Clone all repositories
- `./scripts/update-all.sh` - Update all repositories
- `./scripts/status-all.sh` - Check status across all repos
- `./scripts/build-all.sh` - Build all services
- `./scripts/test-all.sh` - Run all tests
- `./scripts/deploy-all.sh` - Deploy to environments

## 📋 Setup Checklist

### GitHub Organization Setup

- [ ] Create `CurioL-abs` organization
- [ ] Configure organization settings and profile
- [ ] Set up teams and permissions
- [ ] Add organization secrets

### Repository Creation

- [ ] `defai-frontend` repository
- [ ] `defai-backend` repository
- [ ] `defai-ai-engine` repository
- [ ] `defai-smart-contracts` repository
- [ ] `defai-solana-contracts` repository
- [ ] `defai-shared` repository
- [ ] `defai-infrastructure` repository
- [ ] Configure branch protection rules

### CI/CD Setup

- [ ] Create GitHub Actions workflows
- [ ] Set up environment-specific deployments
- [ ] Configure security scanning
- [ ] Test deployment pipelines

### Project Management

- [ ] Create project boards
- [ ] Set up issue templates
- [ ] Create PR templates
- [ ] Document contribution guidelines

### Documentation

- [ ] Update README files for each repository
- [ ] Create architecture documentation
- [ ] Write deployment guides
- [ ] Document API specifications

## 🔧 Quick Start Commands

After setting up the organization and repositories:

```bash
# Clone all repositories
./scripts/clone-all.sh

# Check status of all repositories
./scripts/status-all.sh

# Update all repositories
./scripts/update-all.sh

# Build and test everything
./scripts/build-all.sh
./scripts/test-all.sh

# Deploy to local environment
./scripts/deploy-all.sh local
```

## 📚 Next Steps

1. **Move existing code**: Migrate code from monorepo to individual repositories
2. **Set up CI/CD**: Implement GitHub Actions workflows
3. **Configure monitoring**: Add logging, metrics, and alerting
4. **Document APIs**: Generate and maintain API documentation
5. **Security audit**: Implement security scanning and best practices

## 🔗 Useful Resources

- [GitHub Organization Best Practices](https://docs.github.com/en/organizations)
- [Branch Protection Rules Guide](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Security Best Practices](https://docs.github.com/en/code-security)

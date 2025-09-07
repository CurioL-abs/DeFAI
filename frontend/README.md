# DeFAI Frontend

A modern, beautiful React dashboard for managing autonomous DeFi AI agents on Solana.

## ✨ Features

### 🎨 Modern UI/UX
- **Dark Theme**: Sleek dark mode interface with gradient accents
- **Responsive Design**: Mobile-first design that works on all devices
- **Smooth Animations**: Framer Motion powered micro-interactions
- **Beautiful Charts**: Interactive Recharts for performance visualization

### 🤖 AI Agent Management
- **Dashboard Overview**: Real-time stats and performance metrics
- **Agent Cards**: Detailed agent information with status indicators
- **Create Agent Modal**: Multi-step wizard for configuring new agents
- **Strategy Selection**: Choose from yield farming, arbitrage, and lending strategies
- **Risk Management**: Configure risk levels, stop losses, and profit thresholds

### 📊 Analytics & Monitoring
- **Performance Charts**: Track profits and trading activity over time
- **Portfolio Value**: Monitor your total portfolio value across all agents
- **Success Metrics**: View win rates, total trades, and ROI statistics
- **Real-time Updates**: Live data from the agent-engine API

### 🔧 Technical Features
- **TypeScript**: Full type safety throughout the application
- **Modern React**: React 19 with latest features and patterns
- **Tailwind CSS**: Utility-first styling with custom design system
- **API Integration**: Seamless connection to the agent-engine service
- **Error Handling**: Robust error states and loading indicators

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- DeFAI agent-engine service running on port 8002

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The frontend will be available at `http://localhost:3001`

## 🏗️ Architecture

```
frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles and Tailwind
│   ├── layout.tsx         # Root layout with theme
│   └── page.tsx           # Main dashboard page
├── components/            # Reusable UI components
│   ├── ui/               # Base UI components (buttons, cards, etc.)
│   ├── navbar.tsx        # Navigation bar with wallet info
│   ├── dashboard-stats.tsx # Performance statistics cards
│   ├── agent-card.tsx    # Individual agent display card
│   └── create-agent-modal.tsx # Agent creation wizard
├── lib/                  # Utilities and API client
│   ├── api.ts           # API client for agent-engine
│   └── utils.ts         # Utility functions and formatters
└── tailwind.config.ts   # Tailwind configuration
```

## 🎨 Design System

### Color Palette
- **Primary**: Purple gradient (`hsl(267, 84%, 64%)`)
- **Secondary**: Cyan accent (`hsl(192, 95%, 52%)`)
- **Success**: Green (`hsl(142, 76%, 36%)`)
- **Warning**: Amber (`hsl(38, 92%, 50%)`)
- **Error**: Red (`hsl(0, 84%, 60%)`)

### Components
- **Cards**: Elevated surfaces with hover effects and glow
- **Buttons**: Multiple variants (defi gradient, outline, ghost)
- **Badges**: Status indicators with color-coded states
- **Charts**: Interactive charts with gradient fills and tooltips

### Animations
- **Fade In**: Smooth entry animations for content
- **Slide In**: Staggered animations for lists and grids
- **Pulse Glow**: Attention-grabbing glow effects
- **Card Hover**: Subtle elevation and shadow changes

## 🔌 API Integration

The frontend connects to the agent-engine service running on port 8002:

### Endpoints Used
- `GET /agents/` - Fetch all user agents
- `POST /agents/` - Create new agent
- `GET /health` - Service health check
- `POST /agents/{id}/start` - Start agent (planned)
- `POST /agents/{id}/stop` - Stop agent (planned)
- `POST /agents/{id}/pause` - Pause agent (planned)

### Configuration
Set the API URL via environment variable:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8002
```

## 🛠️ Development

### Adding New Components
1. Create component in appropriate directory
2. Export from `index.ts` if needed
3. Add TypeScript interfaces
4. Include error boundaries for robustness

### Styling Guidelines
- Use Tailwind utility classes
- Leverage design tokens from config
- Add responsive breakpoints: `sm:`, `md:`, `lg:`, `xl:`
- Use semantic color names: `text-success`, `bg-defi-primary`

### State Management
- React hooks for local state
- API client with error handling
- Loading and error states for all async operations

## 🎯 Future Enhancements

### Planned Features
- **Real-time WebSocket Updates**: Live agent status and performance
- **Advanced Analytics**: More detailed charts and metrics
- **Agent Templates**: Pre-configured strategy templates
- **Portfolio Management**: Multi-agent portfolio optimization
- **Notification System**: Real-time alerts and notifications
- **Mobile App**: React Native companion app

### Technical Improvements
- **State Management**: Redux Toolkit or Zustand for complex state
- **Testing**: Jest and React Testing Library
- **Performance**: Code splitting and lazy loading
- **PWA**: Progressive Web App capabilities
- **i18n**: Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📱 Screenshots

The DeFAI frontend features:
- **Modern Dashboard**: Clean, dark interface with gradient accents
- **Agent Cards**: Beautiful cards showing agent status and performance
- **Interactive Charts**: Real-time performance visualization
- **Create Agent Wizard**: Step-by-step agent configuration
- **Responsive Design**: Works perfectly on mobile and desktop

## 🎨 Design Philosophy

The DeFAI frontend embodies the cutting-edge nature of DeFi and AI:

- **Futuristic Aesthetics**: Dark theme with neon accents
- **Data-Driven Interface**: Charts and metrics take center stage
- **Intuitive Navigation**: Clear information hierarchy
- **Performance First**: Fast loading and smooth interactions
- **Trust Through Transparency**: Clear status indicators and real-time data

---

Built with ❤️ for the DeFi community. Powered by AI, secured by Solana.

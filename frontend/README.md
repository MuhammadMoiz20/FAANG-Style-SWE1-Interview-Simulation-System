# Frontend - FAANG Interview Simulation System

React + TypeScript frontend for the interview simulation system.

## Structure

```
frontend/
├── src/
│   ├── services/        # API client and services
│   │   └── api.ts
│   ├── App.tsx          # Main application component
│   ├── App.css          # Application styles
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── index.html           # HTML template
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite configuration
└── setup.sh            # Setup script
```

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Development

### API Integration

The frontend proxies API requests to the backend:
- Development: `/api` → `http://localhost:8000`
- Production: Configure via `VITE_API_URL` environment variable

### Adding New Features

1. Create component in `src/components/`
2. Add API methods in `src/services/api.ts`
3. Update routing if needed

## Building for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Code Quality

Lint code:
```bash
npm run lint
```

Format code (if configured):
```bash
npm run format
```

## Environment Variables

Create `.env` file:
```env
VITE_API_URL=/api
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

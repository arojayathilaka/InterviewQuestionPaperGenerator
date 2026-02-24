# Frontend Documentation

## Overview

React frontend for Interview Question Paper Generator.

## Features

- ✅ User registration and authentication
- ✅ Form-based paper generation
- ✅ Real-time status polling
- ✅ Result display with download
- ✅ Responsive design with Tailwind CSS
- ✅ Error handling and validation

## Installation

```bash
npm install
```

## Configuration

Create `.env.local`:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENV=development
```

## Running

Development server:

```bash
npm start
```

Build for production:

```bash
npm run build
```

## Project Structure

- `src/components/` - React components
  - `PaperGenerationForm.jsx` - Main paper generation form
  - `PaperResults.jsx` - Results display
  - `UserRegistration.jsx` - User registration
  
- `src/pages/` - Page components
  - `HomePage.jsx` - Main application page

- `src/services/` - API integration
  - `api.js` - Axios API client

## Components

### PaperGenerationForm
Form for generating question papers with:
- Topic input
- Question count
- Difficulty level
- Question types
- Exam duration
- Additional preferences

### PaperResults
Displays generated paper with:
- Loading state during generation
- Status polling every 5 seconds
- Download functionality
- Difficulty distribution
- Paper metadata

### UserRegistration
User registration form with:
- User ID
- Email
- Name
- Local storage persistence

## Styling

- Tailwind CSS for utility-first styling
- Responsive design for mobile/tablet/desktop
- Gradient backgrounds and shadows
- Loading states and animations

## API Integration

All API calls handled through `api.js`:

```javascript
// Generate paper
await paperAPI.generatePaper({
  user_id: "user123",
  technology_topic: "React Hooks",
  num_questions: 10,
  ...
});

// Get paper status
await paperAPI.getPaperStatus(paperId);

// Get paper content
await paperAPI.getPaper(paperId);
```

## Error Handling

- Form validation before submission
- API error response handling
- User-friendly error messages
- Graceful degradation

## Local Storage

User data stored in browser:
- `user_id` - User identifier
- `user_email` - User email
- `user_name` - User name

## Dependencies

See `package.json` for all dependencies.

Key packages:
- react - UI framework
- react-dom - React rendering
- axios - HTTP client
- react-router-dom - Routing
- tailwindcss - CSS framework

## Environment Variables

```
REACT_APP_API_URL    - Backend API URL (default: http://localhost:8000/api/v1)
REACT_APP_ENV        - Environment (development/production)
```

## Performance

- Lazy loading of components
- Optimized re-renders with hooks
- Efficient state management
- Minified production build

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Deployment

Build production bundle:

```bash
npm run build
```

The `build/` directory is production-ready.

## Troubleshooting

**CORS errors**: Ensure backend CORS is configured for frontend origin
**API not found**: Check `REACT_APP_API_URL` environment variable
**Registration fails**: Verify backend is running and database is configured

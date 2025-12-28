#!/bin/bash

echo "🚀 Setting up Frontend"
echo ""

cd frontend

# Install dependencies (already done by create-vite, but just in case)
echo "Installing npm dependencies..."
npm install

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "Next steps:"
echo "1. Start dev server: cd frontend && npm run dev"
echo "2. Open browser: http://localhost:5173"

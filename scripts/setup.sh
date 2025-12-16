#!/bin/bash
set -e

echo "=== FTAI Voice Agent Setup ==="
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env and add your API keys:"
    echo "  - OPENROUTER_API_KEY (https://openrouter.ai/keys)"
    echo "  - DEEPGRAM_API_KEY (https://console.deepgram.com - \$200 free)"
    echo "  - CARTESIA_API_KEY (https://play.cartesia.ai/)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check for required API keys
if grep -q "sk-or-your-openrouter-key" .env; then
    echo "ERROR: Please update OPENROUTER_API_KEY in .env"
    exit 1
fi

if grep -q "your-deepgram-key" .env; then
    echo "ERROR: Please update DEEPGRAM_API_KEY in .env"
    exit 1
fi

if grep -q "your-cartesia-key" .env; then
    echo "ERROR: Please update CARTESIA_API_KEY in .env"
    exit 1
fi

echo "API keys configured!"
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

echo "Docker found!"
echo ""

# Start services
echo "Starting LiveKit server and agent..."
docker-compose up -d

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Services running:"
echo "  - LiveKit Server: ws://localhost:7880"
echo "  - Voice Agent: connected to LiveKit"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f agent"
echo ""
echo "To stop services:"
echo "  docker-compose down"

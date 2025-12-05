#!/bin/bash

# Define the API endpoint URL for the Swagger UI
API_URL="http://localhost:8080/docs"

# Wait a few seconds to ensure the API service is fully initialized and listening
echo "Waiting 10 seconds for the FastAPI service to spin up..."
sleep 10

echo "Attempting to open the API interface at: $API_URL"

# Command to open the URL in the default browser, compatible with most OSes
# Use "open" for macOS, "start" for Windows (WSL), and "xdg-open" for Linux
if command -v xdg-open > /dev/null; then
    xdg-open "$API_URL" &
elif command -v open > /dev/null; then
    open "$API_URL" &
elif command -v start > /dev/null; then
    start "$API_URL"
else
    echo "Could not automatically open browser. Please navigate to $API_URL manually."
fi

echo "Deployment complete. Monitor logs for ingestion progress."
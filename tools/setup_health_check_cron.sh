#!/bin/bash
# Setup cron job for DeepCAL++ health checks

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}  DeepCAL++ Health Check Cron Setup   ${NC}"
echo -e "${BLUE}=======================================${NC}"

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_PATH="$(which python3 || which python)"
CRON_SCRIPT="${PROJECT_DIR}/backend/cli/cron_health_check.py"

# Check if the cron script exists
if [ ! -f "$CRON_SCRIPT" ]; then
    echo -e "${RED}Error: Cron script not found at ${CRON_SCRIPT}${NC}"
    exit 1
fi

# Make the script executable
chmod +x "$CRON_SCRIPT"

# Create a wrapper script that sets up the environment
WRAPPER_SCRIPT="${PROJECT_DIR}/tools/run_health_check.sh"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# DeepCAL++ Health Check Wrapper Script
# This script sets up the environment and runs the health check

# Load environment variables
if [ -f "${PROJECT_DIR}/.env" ]; then
    source "${PROJECT_DIR}/.env"
fi

# Run the health check
cd "${PROJECT_DIR}"
"${PYTHON_PATH}" "${CRON_SCRIPT}" >> "${PROJECT_DIR}/backend/logs/cron_output.log" 2>&1
EOF

# Make the wrapper script executable
chmod +x "$WRAPPER_SCRIPT"

# Ask for cron schedule
echo -e "${YELLOW}How often should the health check run?${NC}"
echo "1) Hourly"
echo "2) Every 6 hours"
echo "3) Daily"
echo "4) Custom"
read -p "Enter your choice (1-4): " schedule_choice

case $schedule_choice in
    1)
        CRON_SCHEDULE="0 * * * *" # Hourly
        SCHEDULE_DESC="hourly"
        ;;
    2)
        CRON_SCHEDULE="0 */6 * * *" # Every 6 hours
        SCHEDULE_DESC="every 6 hours"
        ;;
    3)
        CRON_SCHEDULE="0 0 * * *" # Daily at midnight
        SCHEDULE_DESC="daily at midnight"
        ;;
    4)
        read -p "Enter custom cron schedule (e.g., '*/30 * * * *' for every 30 minutes): " CRON_SCHEDULE
        SCHEDULE_DESC="custom schedule ($CRON_SCHEDULE)"
        ;;
    *)
        echo -e "${RED}Invalid choice. Using daily schedule.${NC}"
        CRON_SCHEDULE="0 0 * * *" # Daily at midnight
        SCHEDULE_DESC="daily at midnight"
        ;;
esac

# Create a temporary file for the crontab
TEMP_CRONTAB=$(mktemp)

# Get existing crontab
crontab -l > "$TEMP_CRONTAB" 2>/dev/null || true

# Check if the cron job already exists
if grep -q "DeepCAL++ Health Check" "$TEMP_CRONTAB"; then
    echo -e "${YELLOW}DeepCAL++ Health Check cron job already exists. Updating...${NC}"
    sed -i '/# DeepCAL++ Health Check/d' "$TEMP_CRONTAB"
    sed -i "\|${WRAPPER_SCRIPT}|d" "$TEMP_CRONTAB"
fi

# Add the new cron job
echo "" >> "$TEMP_CRONTAB"
echo "# DeepCAL++ Health Check - Added $(date)" >> "$TEMP_CRONTAB"
echo "$CRON_SCHEDULE $WRAPPER_SCRIPT" >> "$TEMP_CRONTAB"

# Install the new crontab
crontab "$TEMP_CRONTAB"

# Clean up
rm "$TEMP_CRONTAB"

echo -e "${GREEN}DeepCAL++ Health Check cron job installed successfully!${NC}"
echo -e "The health check will run ${SCHEDULE_DESC}."
echo -e "Logs will be written to: ${PROJECT_DIR}/backend/logs/cron_output.log"
echo -e "Health check results will be stored in: ${PROJECT_DIR}/backend/logs/health_check_history.json"

if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_SERVICE_KEY" ]; then
    echo -e "${GREEN}Health check results will also be logged to Supabase.${NC}"
else
    echo -e "${YELLOW}Note: Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables to log results to Supabase.${NC}"
fi

echo -e "${BLUE}=======================================${NC}"


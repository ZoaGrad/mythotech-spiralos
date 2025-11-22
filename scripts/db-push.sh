#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Database Push Script with Retry Logic
# ═══════════════════════════════════════════════════════════════════════════
# Purpose: Push database migrations to Supabase with retry logic for transient failures
# Usage: ./scripts/db-push.sh [migration_file]
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Configuration
MAX_RETRIES="${DB_PUSH_MAX_RETRIES:-5}"
RETRY_DELAY="${DB_PUSH_RETRY_DELAY:-5}"
BACKOFF_MULTIPLIER="${DB_PUSH_BACKOFF_MULTIPLIER:-2}"
TIMEOUT="${DB_PUSH_TIMEOUT:-30}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required environment variables are set
check_env() {
    if [ -z "${SUPABASE_PROJECT_ID:-}" ]; then
        log_error "SUPABASE_PROJECT_ID environment variable is not set"
        exit 1
    fi
    
    if [ -z "${SUPABASE_DB_PASSWORD:-}" ] && [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
        log_error "Either SUPABASE_DB_PASSWORD or SUPABASE_SERVICE_ROLE_KEY must be set"
        exit 1
    fi
}

# Function to execute SQL with retry logic
execute_sql_with_retry() {
    local sql_file="$1"
    local attempt=1
    local delay=$RETRY_DELAY
    
    if [ ! -f "$sql_file" ]; then
        log_error "SQL file not found: $sql_file"
        exit 1
    fi
    
    log_info "Executing SQL file: $sql_file"
    
    while [ $attempt -le $MAX_RETRIES ]; do
        log_info "Attempt $attempt of $MAX_RETRIES..."
        
        # Try to execute the SQL file
        if timeout $TIMEOUT psql \
            "postgresql://postgres:${SUPABASE_DB_PASSWORD}@db.${SUPABASE_PROJECT_ID}.supabase.co:5432/postgres" \
            -f "$sql_file" \
            2>&1 | tee /tmp/db-push-output.log; then
            
            # Check if the output contains any errors
            if grep -qi "error\|failed\|fatal" /tmp/db-push-output.log; then
                log_warn "SQL execution completed with warnings/errors"
                
                # Check if errors are about existing objects (idempotency - OK)
                if grep -qi "already exists\|duplicate" /tmp/db-push-output.log; then
                    log_info "Idempotent operation - objects already exist (OK)"
                    return 0
                fi
                
                if [ $attempt -eq $MAX_RETRIES ]; then
                    log_error "Max retries reached. SQL execution failed."
                    exit 1
                fi
            else
                log_info "SQL execution successful!"
                return 0
            fi
        else
            local exit_code=$?
            
            if [ $exit_code -eq 124 ]; then
                log_warn "Operation timed out after ${TIMEOUT}s"
            else
                log_warn "SQL execution failed with exit code: $exit_code"
            fi
            
            if [ $attempt -eq $MAX_RETRIES ]; then
                log_error "Max retries reached. Giving up."
                exit 1
            fi
        fi
        
        # Exponential backoff
        log_warn "Retrying in ${delay}s..."
        sleep $delay
        delay=$((delay * BACKOFF_MULTIPLIER))
        attempt=$((attempt + 1))
    done
}

# Function to push all migrations
push_all_migrations() {
    local migrations_dir="${1:-supabase/migrations}"
    
    if [ ! -d "$migrations_dir" ]; then
        log_error "Migrations directory not found: $migrations_dir"
        exit 1
    fi
    
    log_info "Pushing all migrations from: $migrations_dir"
    
    # Find all .sql files and sort them
    local migration_files
    migration_files=$(find "$migrations_dir" -name "*.sql" -type f | sort)
    
    if [ -z "$migration_files" ]; then
        log_warn "No migration files found in $migrations_dir"
        return 0
    fi
    
    # Execute each migration
    while IFS= read -r migration_file; do
        execute_sql_with_retry "$migration_file"
    done <<< "$migration_files"
    
    log_info "All migrations pushed successfully!"
}

# Main script
main() {
    log_info "SpiralOS Database Push with Retry Logic"
    log_info "========================================"
    
    # Check environment
    check_env
    
    # Check if a specific migration file was provided
    if [ $# -eq 1 ]; then
        execute_sql_with_retry "$1"
    else
        push_all_migrations
    fi
    
    log_info "Database push completed successfully!"
}

# Run main function
main "$@"

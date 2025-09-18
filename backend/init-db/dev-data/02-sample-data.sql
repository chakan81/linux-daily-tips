-- Sample data for development environment
-- This file is loaded only in development mode

SET search_path TO linux_tips, public;

-- Insert sample admin user (password: "admin123" - hashed with bcrypt)
INSERT INTO admin_users (username, email, password_hash, is_superuser) VALUES
(
    'admin',
    'admin@linuxtips.dev',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdoP7/9bh/SdkWy',  -- admin123
    true
);

-- Insert sample tips for testing
INSERT INTO tips (title, content, difficulty, category, terminal_setup, publish_date) VALUES
(
    'Basic File Navigation with ls command',
    'The `ls` command is one of the most fundamental Linux commands for listing directory contents. Learn how to use various options to customize the output.

## Basic Usage
```bash
ls                  # List files in current directory
ls -l               # Long format with details
ls -la              # Include hidden files
ls -lh              # Human readable file sizes
```

## Advanced Options
- `-R`: Recursive listing of subdirectories
- `--color=auto`: Colorize output for better readability
- `-t`: Sort by modification time
- `-S`: Sort by file size',
    'beginner',
    '["file-system", "navigation", "basic-commands"]'::jsonb,
    '{
        "directories": ["/home/user/documents", "/home/user/downloads"],
        "files": [
            {"path": "/home/user/documents/readme.txt", "content": "Welcome to Linux Daily Tips!"},
            {"path": "/home/user/documents/script.sh", "content": "#!/bin/bash\necho \"Hello World\""},
            {"path": "/home/user/downloads/data.csv", "content": "name,age,city\nJohn,25,NYC\nJane,30,LA"}
        ],
        "commands": ["ls", "ls -la", "ls -lh"]
    }'::jsonb,
    CURRENT_DATE
),
(
    'Process Management with ps and top',
    'Understanding how to monitor and manage processes is crucial for system administration. Learn the essential commands for process management.

## Viewing Processes
```bash
ps aux              # All processes with detailed info
ps -ef              # Full format listing
top                 # Real-time process viewer
htop                # Enhanced process viewer (if available)
```

## Process Control
```bash
kill PID            # Terminate process by ID
killall name        # Terminate all processes by name
nohup command &     # Run command immune to hangups
```

## Finding Processes
```bash
pgrep firefox       # Find process ID by name
pidof nginx         # Get PID of running program
```',
    'intermediate',
    '["process-management", "system-admin", "monitoring"]'::jsonb,
    '{
        "directories": ["/tmp"],
        "files": [
            {"path": "/tmp/test_script.sh", "content": "#!/bin/bash\nwhile true; do\n  echo \"Running...\"\n  sleep 1\ndone"}
        ],
        "commands": ["chmod +x /tmp/test_script.sh", "/tmp/test_script.sh &", "ps aux | grep test_script", "top"]
    }'::jsonb,
    CURRENT_DATE - INTERVAL '1 day'
),
(
    'Advanced Text Processing with awk',
    'AWK is a powerful pattern-scanning and processing language. Master its basic usage for text manipulation and data extraction.

## Basic Syntax
```bash
awk ''pattern { action }'' file
awk ''{ print $1 }''           # Print first column
awk ''/pattern/ { print }''    # Print lines matching pattern
```

## Built-in Variables
- `NR`: Number of records (line number)
- `NF`: Number of fields in current record
- `$0`: Entire line
- `$1, $2, ...`: Individual fields

## Examples
```bash
awk ''{ print NR, $0 }'' file          # Add line numbers
awk -F'','' ''{ print $2 }'' data.csv   # Print second column from CSV
awk ''$3 > 100 { print $1 }'' data     # Conditional processing
```',
    'advanced',
    '["text-processing", "scripting", "data-manipulation"]'::jsonb,
    '{
        "directories": ["/home/user/workspace"],
        "files": [
            {"path": "/home/user/workspace/sales.csv", "content": "Product,Price,Quantity\nLaptop,999.99,5\nMouse,29.99,50\nKeyboard,79.99,25"},
            {"path": "/home/user/workspace/log.txt", "content": "2024-01-01 10:00 INFO: Server started\n2024-01-01 10:15 ERROR: Connection failed\n2024-01-01 10:30 INFO: User logged in"},
            {"path": "/home/user/workspace/numbers.txt", "content": "10 20 30\n40 50 60\n70 80 90"}
        ],
        "commands": ["awk ''{ print NR, $0 }'' /home/user/workspace/numbers.txt", "awk -F'','' ''{ print $2 }'' /home/user/workspace/sales.csv"]
    }'::jsonb,
    CURRENT_DATE - INTERVAL '2 days'
);

-- Insert sample draft week
INSERT INTO draft_weeks (week_start_date, status, generated_by) VALUES
(
    CURRENT_DATE + INTERVAL '7 days',
    'draft',
    'openai-gpt4'
);

-- Get the draft week ID for draft tips
WITH current_draft AS (
    SELECT id FROM draft_weeks WHERE week_start_date = CURRENT_DATE + INTERVAL '7 days'
)
-- Insert sample draft tips
INSERT INTO draft_tips (draft_week_id, day_of_week, title, content, difficulty, category, terminal_setup, llm_confidence_score)
SELECT
    cd.id,
    1,
    'Understanding File Permissions',
    'Learn how to read and modify file permissions using chmod and understanding the permission system in Linux.',
    'beginner',
    '["permissions", "security", "file-system"]'::jsonb,
    '{
        "directories": ["/home/user/test"],
        "files": [
            {"path": "/home/user/test/secret.txt", "content": "This is a secret file"},
            {"path": "/home/user/test/public.txt", "content": "This is a public file"}
        ],
        "commands": ["ls -l", "chmod 644", "chmod 755"]
    }'::jsonb,
    0.85
FROM current_draft cd;

-- Insert sample analytics events
INSERT INTO analytics_events (event_type, tip_id, session_id, ip_address, event_data)
SELECT
    'tip_view',
    t.id,
    uuid_generate_v4(),
    '127.0.0.1'::inet,
    '{"user_agent": "Mozilla/5.0 (Development)", "duration": 120}'::jsonb
FROM tips t
WHERE t.publish_date = CURRENT_DATE;

-- Insert sample terminal session
INSERT INTO terminal_sessions (tip_id, container_id, ip_address, user_agent, session_data)
SELECT
    t.id,
    'dev_container_' || substr(md5(random()::text), 1, 8),
    '127.0.0.1'::inet,
    'Mozilla/5.0 (Development Browser)',
    '{"commands_executed": ["ls -la", "ps aux"], "last_command": "ls -la"}'::jsonb
FROM tips t
WHERE t.publish_date = CURRENT_DATE
LIMIT 1;

-- Update view counts for sample data
UPDATE tips SET view_count = floor(random() * 100) + 10;

\echo 'Sample development data inserted successfully!';
\echo 'Admin user: admin / admin123';
\echo 'Sample tips created with various difficulty levels';
\echo 'Sample draft week and analytics data added';
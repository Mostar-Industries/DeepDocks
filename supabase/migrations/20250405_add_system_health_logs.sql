-- Create system health logs table
CREATE TABLE IF NOT EXISTS public.system_health_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    system_id TEXT NOT NULL,
    overall_status TEXT NOT NULL,
    execution_time_ms INTEGER NOT NULL,
    details JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_system_health_logs_timestamp ON public.system_health_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_health_logs_system_id ON public.system_health_logs(system_id);
CREATE INDEX IF NOT EXISTS idx_system_health_logs_status ON public.system_health_logs(overall_status);

-- Add RLS policies
ALTER TABLE public.system_health_logs ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to view health logs
CREATE POLICY "Health logs are viewable by authenticated users"
ON public.system_health_logs FOR SELECT
USING (auth.role() = 'authenticated');

-- Allow service role to insert health logs
CREATE POLICY "Service role can insert health logs"
ON public.system_health_logs FOR INSERT
USING (auth.role() = 'service_role');

-- Create a function to clean up old health logs (keep last 30 days)
CREATE OR REPLACE FUNCTION clean_old_health_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM public.system_health_logs
    WHERE timestamp < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Create a cron job to run the cleanup function daily
SELECT cron.schedule(
    'clean-health-logs',
    '0 0 * * *',  -- Run at midnight every day
    $$SELECT clean_old_health_logs()$$
);

-- Add a comment to the table
COMMENT ON TABLE public.system_health_logs IS 'Stores DeepCAL++ system health check logs';


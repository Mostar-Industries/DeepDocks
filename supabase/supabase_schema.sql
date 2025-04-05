-- DeepCAL++ Database Schema for Supabase

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Forwarders Table
CREATE TABLE public.forwarders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    code TEXT UNIQUE,
    description TEXT,
    country TEXT,
    region TEXT,
    website TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Forwarder Services Table
CREATE TABLE public.forwarder_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    forwarder_id UUID REFERENCES public.forwarders(id) ON DELETE CASCADE,
    service_name TEXT NOT NULL,
    has_tracking BOOLEAN DEFAULT FALSE,
    has_insurance BOOLEAN DEFAULT FALSE,
    has_express BOOLEAN DEFAULT FALSE,
    has_bulk BOOLEAN DEFAULT FALSE,
    has_hazardous BOOLEAN DEFAULT FALSE,
    has_refrigerated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(forwarder_id, service_name)
);

-- Routes Table
CREATE TABLE public.routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    origin_country TEXT NOT NULL,
    origin_city TEXT,
    destination_country TEXT NOT NULL,
    destination_city TEXT,
    distance_km NUMERIC,
    typical_transit_days INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(origin_country, origin_city, destination_country, destination_city)
);

-- Rate Cards Table
CREATE TABLE public.rate_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    forwarder_id UUID REFERENCES public.forwarders(id) ON DELETE CASCADE,
    route_id UUID REFERENCES public.routes(id) ON DELETE CASCADE,
    cargo_type TEXT NOT NULL,
    base_cost NUMERIC NOT NULL,
    currency TEXT DEFAULT 'USD',
    cost_per_kg NUMERIC,
    cost_per_cbm NUMERIC,
    minimum_weight_kg NUMERIC,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(forwarder_id, route_id, cargo_type, effective_date)
);

-- Shipments Table
CREATE TABLE public.shipments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tracking_number TEXT UNIQUE,
    forwarder_id UUID REFERENCES public.forwarders(id) ON DELETE SET NULL,
    route_id UUID REFERENCES public.routes(id) ON DELETE SET NULL,
    cargo_type TEXT NOT NULL,
    weight_kg NUMERIC NOT NULL,
    volume_cbm NUMERIC,
    declared_value NUMERIC,
    currency TEXT DEFAULT 'USD',
    shipping_cost NUMERIC,
    insurance_cost NUMERIC,
    ship_date DATE,
    estimated_delivery DATE,
    actual_delivery DATE,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Shipment Status History Table
CREATE TABLE public.shipment_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shipment_id UUID REFERENCES public.shipments(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    location TEXT,
    notes TEXT,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Analytics Table
CREATE TABLE public.performance_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    forwarder_id UUID REFERENCES public.forwarders(id) ON DELETE CASCADE,
    route_id UUID REFERENCES public.routes(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    on_time_rate NUMERIC,
    damage_rate NUMERIC,
    claim_rate NUMERIC,
    avg_transit_days NUMERIC,
    shipment_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(forwarder_id, route_id, period_start, period_end)
);

-- User Analyses Table
CREATE TABLE public.user_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    analysis_name TEXT,
    forwarders JSONB NOT NULL,
    results JSONB NOT NULL,
    parameters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the updated_at triggers to all tables
CREATE TRIGGER update_forwarders_modtime
BEFORE UPDATE ON public.forwarders
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_forwarder_services_modtime
BEFORE UPDATE ON public.forwarder_services
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_routes_modtime
BEFORE UPDATE ON public.routes
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_rate_cards_modtime
BEFORE UPDATE ON public.rate_cards
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_shipments_modtime
BEFORE UPDATE ON public.shipments
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_performance_analytics_modtime
BEFORE UPDATE ON public.performance_analytics
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Add RLS Policies
ALTER TABLE public.forwarders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.forwarder_services ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.routes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rate_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shipments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shipment_status_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_analyses ENABLE ROW LEVEL SECURITY;

-- RLS Policies for public data (read-only)
CREATE POLICY "Public forwarders are viewable by everyone"
ON public.forwarders FOR SELECT
USING (TRUE);

CREATE POLICY "Public routes are viewable by everyone"
ON public.routes FOR SELECT
USING (TRUE);

-- RLS Policies for user-specific data
CREATE POLICY "User analyses are viewable by their owners"
ON public.user_analyses FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own analyses"
ON public.user_analyses FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Sample Data
-- Insert sample forwarders
INSERT INTO public.forwarders (name, code, country, region, website)
VALUES 
('AfricaLogistics', 'ALOG', 'Kenya', 'East Africa', 'https://africalogistics.example.com'),
('GlobalFreight', 'GFRT', 'South Africa', 'Southern Africa', 'https://globalfreight.example.com'),
('ExpressShip', 'EXPS', 'Nigeria', 'West Africa', 'https://expressship.example.com');

-- Insert sample routes
INSERT INTO public.routes (origin_country, origin_city, destination_country, destination_city, distance_km, typical_transit_days)
VALUES 
('Kenya', 'Nairobi', 'Egypt', 'Cairo', 3600, 14),
('South Africa', 'Johannesburg', 'Morocco', 'Casablanca', 7200, 18),
('Nigeria', 'Lagos', 'Ethiopia', 'Addis Ababa', 3200, 10);

-- Create indexes for performance
CREATE INDEX idx_shipments_forwarder ON public.shipments(forwarder_id);
CREATE INDEX idx_shipments_route ON public.shipments(route_id);
CREATE INDEX idx_shipment_status_history_shipment ON public.shipment_status_history(shipment_id);
CREATE INDEX idx_rate_cards_forwarder_route ON public.rate_cards(forwarder_id, route_id);
CREATE INDEX idx_performance_analytics_forwarder ON public.performance_analytics(forwarder_id);


# Supabase Setup Guide

This guide explains how to set up Supabase for the AI Hub Content Creation system and run the integration test.

## 1. Create a Supabase Project

1. Go to [Supabase](https://supabase.com/) and sign up or log in
2. Create a new project
3. Choose a name for your project
4. Set a secure database password
5. Choose a region close to your location
6. Click "Create new project"

## 2. Get Your Supabase Credentials

1. Once your project is created, go to the project dashboard
2. Click on the "Settings" icon in the left sidebar
3. Click on "API" in the settings menu
4. You'll find your:
   - **Project URL**: This is your `SUPABASE_URL`
   - **API Key**: Use the "anon" public key as your `SUPABASE_KEY`

## 3. Create Required Tables

You need to create the following tables in your Supabase project:

### content_inventory

```sql
create table content_inventory (
  id uuid primary key default uuid_generate_v4(),
  content_id text not null unique,
  section text,
  subsection text,
  title text,
  content_type text,
  status text default 'Not Started',
  priority text,
  dependencies text,
  audience_technical_level text,
  audience_role text,
  audience_constraints text,
  primary_mission_pillar_1 text,
  primary_mission_pillar_2 text,
  secondary_mission_pillars text,
  smart_objectives text,
  practical_components text,
  estimated_dev_time text,
  required_expertise text,
  assigned_creator text,
  assigned_reviewers text,
  review_status text,
  platform_requirements text,
  notes text,
  metadata jsonb,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Create index on content_id
create index content_inventory_content_id_idx on content_inventory (content_id);

-- Create index on section
create index content_inventory_section_idx on content_inventory (section);

-- Create index on status
create index content_inventory_status_idx on content_inventory (status);
```

### prompt_logs

```sql
create table prompt_logs (
  id uuid primary key default uuid_generate_v4(),
  session_id text not null,
  prompt_type text,
  prompt_text text,
  model text,
  temperature float,
  content_id text,
  user_id text,
  created_at timestamp with time zone default now()
);

-- Create index on session_id
create index prompt_logs_session_id_idx on prompt_logs (session_id);

-- Create index on content_id
create index prompt_logs_content_id_idx on prompt_logs (content_id);
```

### generation_outputs

```sql
create table generation_outputs (
  id uuid primary key default uuid_generate_v4(),
  prompt_id uuid references prompt_logs(id),
  output_text text,
  content_id text,
  status text default 'completed',
  metadata jsonb,
  created_at timestamp with time zone default now()
);

-- Create index on prompt_id
create index generation_outputs_prompt_id_idx on generation_outputs (prompt_id);

-- Create index on content_id
create index generation_outputs_content_id_idx on generation_outputs (content_id);
```

### content_files

```sql
create table content_files (
  id uuid primary key default uuid_generate_v4(),
  output_id uuid references generation_outputs(id),
  content_type text,
  file_content text,
  created_at timestamp with time zone default now()
);

-- Create index on output_id
create index content_files_output_id_idx on content_files (output_id);
```

### test_table (Optional, for testing only)

```sql
create table test_table (
  id uuid primary key default uuid_generate_v4(),
  test_id text not null unique,
  test_name text,
  test_data jsonb,
  created_at timestamp with time zone default now()
);
```

## 4. Set Up Environment Variables

1. Copy the `.env.sample` file to `.env`:
   ```bash
   cp .env.sample .env
   ```

2. Edit the `.env` file and add your Supabase credentials:
   ```
   SUPABASE_URL="https://your-project-id.supabase.co"
   SUPABASE_KEY="your-supabase-api-key"
   ```

3. Add your Google Generative AI API key:
   ```
   GOOGLE_GENAI_API_KEY="your-google-genai-api-key"
   ```

4. Set a secure Flask secret key:
   ```
   FLASK_SECRET_KEY="your-flask-secret-key"
   ```

## 5. Run the Supabase Integration Test

Run the test script to verify that your Supabase integration is working correctly:

```bash
python test_supabase_connection.py
```

If the test passes, you'll see:
```
✅ SUPABASE INTEGRATION TEST PASSED
```

If the test fails, check the error message and make sure:
1. Your Supabase credentials are correct
2. The required tables exist in your Supabase project
3. You have network connectivity to Supabase

## 6. Import Content Inventory

Once the test passes, you can import the content inventory:

```bash
python supabase_client.py
```

This will import the content inventory from `AI_Hub_Content_Inventory_Enhanced.csv` into the Supabase database.

## 7. Verify the Import

You can verify that the content inventory was imported correctly by listing the content items:

```bash
python list_content_inventory.py
```

## Next Steps

Now that your Supabase integration is set up and working, you can:

1. Generate content for specific items:
   ```bash
   python content_workflow_supabase.py --content-id LRN-BEG-001
   ```

2. Generate content in batch:
   ```bash
   python generate_content_batch.py --section "Learn AI" --status "Not Started"
   ```

3. View prompt logs:
   ```bash
   python view_prompt_logs.py --content-id LRN-BEG-001 --show-content
   ```

For more information, see the [Supabase Integration](SUPABASE_INTEGRATION.md) documentation.

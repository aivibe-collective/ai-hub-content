#!/usr/bin/env python3
"""
Dashboard for AI Hub Content Creation System.

This script creates a web-based dashboard that displays:
- Content generation status
- Content quality metrics
- Source quality metrics
- Generation performance metrics
- Model comparison
"""

import os
import sys
import glob
import json
import logging
import argparse
from typing import Dict, List, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request, jsonify, send_from_directory
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx

# Import our custom modules
from supabase_client import is_connected, get_content_inventory
from content_evaluation import ContentEvaluation
from source_evaluation import parse_sources_from_markdown, evaluate_sources

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='dashboard_templates', static_folder='dashboard_static')

# Create directories if they don't exist
os.makedirs('dashboard_templates', exist_ok=True)
os.makedirs('dashboard_static', exist_ok=True)
os.makedirs('dashboard_static/js', exist_ok=True)
os.makedirs('dashboard_static/css', exist_ok=True)
os.makedirs('dashboard_static/images', exist_ok=True)

class Dashboard:
    """Dashboard class for content metrics."""
    
    def __init__(self, content_dir: str = 'generated_content'):
        """Initialize dashboard.
        
        Args:
            content_dir: Directory containing generated content
        """
        self.content_dir = content_dir
        self.content_files = self._get_content_files()
        self.evaluation_files = self._get_evaluation_files()
        self.content_inventory = self._get_content_inventory()
        self.evaluations = self._load_evaluations()
        self.content_df = self._create_content_dataframe()
    
    def _get_content_files(self) -> List[str]:
        """Get list of content files.
        
        Returns:
            List of content file paths
        """
        return glob.glob(os.path.join(self.content_dir, '*.md'))
    
    def _get_evaluation_files(self) -> List[str]:
        """Get list of evaluation files.
        
        Returns:
            List of evaluation file paths
        """
        return glob.glob(os.path.join(self.content_dir, '*.md.evaluation.json'))
    
    def _get_content_inventory(self) -> List[Dict]:
        """Get content inventory from Supabase.
        
        Returns:
            List of content inventory items
        """
        if not is_connected():
            logger.warning("Not connected to Supabase, using empty inventory")
            return []
        
        return get_content_inventory() or []
    
    def _load_evaluations(self) -> Dict[str, Dict]:
        """Load content evaluations.
        
        Returns:
            Dictionary of content evaluations by content ID
        """
        evaluations = {}
        
        for eval_file in self.evaluation_files:
            try:
                with open(eval_file, 'r') as f:
                    evaluation = json.load(f)
                    content_id = evaluation.get('content_id')
                    if content_id:
                        evaluations[content_id] = evaluation
            except Exception as e:
                logger.error(f"Error loading evaluation file {eval_file}: {str(e)}")
        
        return evaluations
    
    def _create_content_dataframe(self) -> pd.DataFrame:
        """Create DataFrame with content data.
        
        Returns:
            DataFrame with content data
        """
        data = []
        
        # Add inventory data
        for item in self.content_inventory:
            content_id = item.get('content_id')
            row = {
                'content_id': content_id,
                'title': item.get('title', ''),
                'section': item.get('section', ''),
                'status': item.get('status', 'Unknown'),
                'model': item.get('model', ''),
                'temperature': item.get('temperature', 0.0),
                'generation_time': item.get('generation_time', 0),
                'dependencies': item.get('dependencies', ''),
                'has_evaluation': content_id in self.evaluations
            }
            
            # Add evaluation data if available
            if content_id in self.evaluations:
                eval_data = self.evaluations[content_id]
                scores = eval_data.get('scores', {})
                row.update({
                    'accuracy_score': scores.get('accuracy', 0),
                    'relevance_score': scores.get('relevance', 0),
                    'engagement_score': scores.get('engagement', 0),
                    'mission_alignment_score': scores.get('mission_alignment', 0),
                    'source_quality_score': scores.get('source_quality', 0),
                    'average_score': scores.get('average', 0),
                    'quality_rating': eval_data.get('quality_rating', ''),
                    'source_count': eval_data.get('source_count', 0),
                    'word_count': eval_data.get('word_count', 0)
                })
            
            data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        return df
    
    def get_status_counts(self) -> Dict[str, int]:
        """Get counts of content by status.
        
        Returns:
            Dictionary of status counts
        """
        if self.content_df.empty:
            return {}
        
        return self.content_df['status'].value_counts().to_dict()
    
    def get_section_counts(self) -> Dict[str, int]:
        """Get counts of content by section.
        
        Returns:
            Dictionary of section counts
        """
        if self.content_df.empty:
            return {}
        
        return self.content_df['section'].value_counts().to_dict()
    
    def get_quality_counts(self) -> Dict[str, int]:
        """Get counts of content by quality rating.
        
        Returns:
            Dictionary of quality rating counts
        """
        if self.content_df.empty:
            return {}
        
        # Filter to only rows with quality ratings
        df = self.content_df[self.content_df['has_evaluation']]
        if df.empty:
            return {}
        
        return df['quality_rating'].value_counts().to_dict()
    
    def get_model_performance(self) -> pd.DataFrame:
        """Get performance metrics by model.
        
        Returns:
            DataFrame with model performance metrics
        """
        if self.content_df.empty:
            return pd.DataFrame()
        
        # Filter to only rows with evaluations
        df = self.content_df[self.content_df['has_evaluation']]
        if df.empty:
            return pd.DataFrame()
        
        # Group by model and calculate metrics
        metrics = df.groupby('model').agg({
            'average_score': ['mean', 'std', 'count'],
            'accuracy_score': 'mean',
            'relevance_score': 'mean',
            'engagement_score': 'mean',
            'mission_alignment_score': 'mean',
            'source_quality_score': 'mean',
            'word_count': 'mean',
            'source_count': 'mean',
            'generation_time': 'mean'
        })
        
        # Flatten column names
        metrics.columns = ['_'.join(col).strip() for col in metrics.columns.values]
        
        return metrics.reset_index()
    
    def get_dependency_graph(self) -> nx.DiGraph:
        """Get dependency graph of content.
        
        Returns:
            NetworkX DiGraph of content dependencies
        """
        G = nx.DiGraph()
        
        # Add nodes
        for _, row in self.content_df.iterrows():
            content_id = row['content_id']
            G.add_node(content_id, **row.to_dict())
        
        # Add edges
        for _, row in self.content_df.iterrows():
            content_id = row['content_id']
            dependencies = row['dependencies']
            
            if dependencies:
                for dep in dependencies.split(';'):
                    dep = dep.strip()
                    if dep and dep in G:
                        # Add edge from dependency to content (content depends on dep)
                        G.add_edge(dep, content_id)
        
        return G
    
    def create_status_chart(self) -> Dict:
        """Create chart of content status.
        
        Returns:
            Plotly figure as JSON
        """
        status_counts = self.get_status_counts()
        
        if not status_counts:
            return {}
        
        fig = px.pie(
            names=list(status_counts.keys()),
            values=list(status_counts.values()),
            title="Content Status",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        
        return json.loads(plotly.io.to_json(fig))
    
    def create_quality_chart(self) -> Dict:
        """Create chart of content quality.
        
        Returns:
            Plotly figure as JSON
        """
        quality_counts = self.get_quality_counts()
        
        if not quality_counts:
            return {}
        
        # Define quality order
        quality_order = ["Excellent", "Very Good", "Good", "Fair", "Poor"]
        
        # Filter and sort data
        labels = []
        values = []
        for quality in quality_order:
            if quality in quality_counts:
                labels.append(quality)
                values.append(quality_counts[quality])
        
        fig = px.bar(
            x=labels,
            y=values,
            title="Content Quality",
            labels={'x': 'Quality Rating', 'y': 'Count'},
            color=labels,
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        
        return json.loads(plotly.io.to_json(fig))
    
    def create_model_comparison_chart(self) -> Dict:
        """Create chart comparing model performance.
        
        Returns:
            Plotly figure as JSON
        """
        model_performance = self.get_model_performance()
        
        if model_performance.empty:
            return {}
        
        fig = px.bar(
            model_performance,
            x='model',
            y='average_score_mean',
            error_y='average_score_std',
            title="Model Performance Comparison",
            labels={'model': 'Model', 'average_score_mean': 'Average Quality Score'},
            color='model',
            color_discrete_sequence=px.colors.qualitative.Plotly,
            hover_data=['average_score_count', 'generation_time_mean']
        )
        
        return json.loads(plotly.io.to_json(fig))
    
    def create_score_breakdown_chart(self) -> Dict:
        """Create chart of score breakdown by model.
        
        Returns:
            Plotly figure as JSON
        """
        model_performance = self.get_model_performance()
        
        if model_performance.empty:
            return {}
        
        # Select score columns
        score_cols = [
            'accuracy_score_mean',
            'relevance_score_mean',
            'engagement_score_mean',
            'mission_alignment_score_mean',
            'source_quality_score_mean'
        ]
        
        # Melt DataFrame for plotting
        melted = pd.melt(
            model_performance,
            id_vars=['model'],
            value_vars=score_cols,
            var_name='score_type',
            value_name='score'
        )
        
        # Clean up score type names
        melted['score_type'] = melted['score_type'].str.replace('_score_mean', '').str.replace('_', ' ').str.title()
        
        fig = px.bar(
            melted,
            x='score_type',
            y='score',
            color='model',
            barmode='group',
            title="Score Breakdown by Model",
            labels={'score_type': 'Score Type', 'score': 'Average Score', 'model': 'Model'},
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        
        return json.loads(plotly.io.to_json(fig))
    
    def create_dependency_chart(self) -> Dict:
        """Create chart of content dependencies.
        
        Returns:
            Plotly figure as JSON
        """
        G = self.get_dependency_graph()
        
        if not G.nodes:
            return {}
        
        # Create positions using spring layout
        pos = nx.spring_layout(G)
        
        # Create edge trace
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node trace
        node_x = []
        node_y = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
        
        # Get node attributes for hover text
        node_text = []
        node_color = []
        for node in G.nodes():
            if 'status' in G.nodes[node]:
                status = G.nodes[node]['status']
                if status == 'Completed':
                    color = 'green'
                elif status == 'In Progress':
                    color = 'blue'
                elif status == 'Failed':
                    color = 'red'
                else:
                    color = 'gray'
                
                node_color.append(color)
                
                # Create hover text
                text = f"ID: {node}<br>"
                if 'title' in G.nodes[node]:
                    text += f"Title: {G.nodes[node]['title']}<br>"
                text += f"Status: {status}<br>"
                if 'average_score' in G.nodes[node]:
                    text += f"Score: {G.nodes[node]['average_score']:.1f}/5<br>"
                
                node_text.append(text)
            else:
                node_color.append('gray')
                node_text.append(f"ID: {node}")
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                color=node_color,
                size=10,
                line=dict(width=2)
            )
        )
        
        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title="Content Dependency Graph",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        return json.loads(plotly.io.to_json(fig))
    
    def create_dashboard_data(self) -> Dict:
        """Create data for dashboard.
        
        Returns:
            Dictionary with dashboard data
        """
        return {
            'status_chart': self.create_status_chart(),
            'quality_chart': self.create_quality_chart(),
            'model_comparison_chart': self.create_model_comparison_chart(),
            'score_breakdown_chart': self.create_score_breakdown_chart(),
            'dependency_chart': self.create_dependency_chart(),
            'content_count': len(self.content_df),
            'completed_count': len(self.content_df[self.content_df['status'] == 'Completed']),
            'evaluated_count': len(self.content_df[self.content_df['has_evaluation']]),
            'average_score': self.content_df[self.content_df['has_evaluation']]['average_score'].mean() if not self.content_df.empty else 0,
            'average_word_count': self.content_df[self.content_df['has_evaluation']]['word_count'].mean() if not self.content_df.empty else 0,
            'average_source_count': self.content_df[self.content_df['has_evaluation']]['source_count'].mean() if not self.content_df.empty else 0
        }


# Create HTML template
dashboard_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Hub Content Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">AI Hub Content Dashboard</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link active" href="#">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/content">Content List</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/models">Model Comparison</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dependencies">Dependencies</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-3">
                <div class="card text-white bg-primary mb-3">
                    <div class="card-body">
                        <h5 class="card-title">Total Content</h5>
                        <p class="card-text display-4">{{ content_count }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-success mb-3">
                    <div class="card-body">
                        <h5 class="card-title">Completed</h5>
                        <p class="card-text display-4">{{ completed_count }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-info mb-3">
                    <div class="card-body">
                        <h5 class="card-title">Evaluated</h5>
                        <p class="card-text display-4">{{ evaluated_count }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-warning mb-3">
                    <div class="card-body">
                        <h5 class="card-title">Avg. Quality</h5>
                        <p class="card-text display-4">{{ "%.1f"|format(average_score) }}/5</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-body">
                        <div id="status-chart"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-body">
                        <div id="quality-chart"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card mb-3">
                    <div class="card-body">
                        <div id="model-comparison-chart"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card mb-3">
                    <div class="card-body">
                        <div id="score-breakdown-chart"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card mb-3">
                    <div class="card-body">
                        <div id="dependency-chart"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load charts
        document.addEventListener('DOMContentLoaded', function() {
            // Status chart
            var statusChart = {{ status_chart|tojson }};
            if (Object.keys(statusChart).length > 0) {
                Plotly.newPlot('status-chart', statusChart.data, statusChart.layout);
            }
            
            // Quality chart
            var qualityChart = {{ quality_chart|tojson }};
            if (Object.keys(qualityChart).length > 0) {
                Plotly.newPlot('quality-chart', qualityChart.data, qualityChart.layout);
            }
            
            // Model comparison chart
            var modelComparisonChart = {{ model_comparison_chart|tojson }};
            if (Object.keys(modelComparisonChart).length > 0) {
                Plotly.newPlot('model-comparison-chart', modelComparisonChart.data, modelComparisonChart.layout);
            }
            
            // Score breakdown chart
            var scoreBreakdownChart = {{ score_breakdown_chart|tojson }};
            if (Object.keys(scoreBreakdownChart).length > 0) {
                Plotly.newPlot('score-breakdown-chart', scoreBreakdownChart.data, scoreBreakdownChart.layout);
            }
            
            // Dependency chart
            var dependencyChart = {{ dependency_chart|tojson }};
            if (Object.keys(dependencyChart).length > 0) {
                Plotly.newPlot('dependency-chart', dependencyChart.data, dependencyChart.layout);
            }
        });
    </script>
</body>
</html>
"""

# Create CSS file
dashboard_css = """
body {
    background-color: #f8f9fa;
}

.card {
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.navbar {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.display-4 {
    font-size: 2.5rem;
    font-weight: bold;
}
"""

# Save template and CSS
with open('dashboard_templates/index.html', 'w') as f:
    f.write(dashboard_template)

with open('dashboard_static/css/dashboard.css', 'w') as f:
    f.write(dashboard_css)

# Flask routes
@app.route('/')
def index():
    """Dashboard home page."""
    dashboard = Dashboard()
    data = dashboard.create_dashboard_data()
    return render_template('index.html', **data)

@app.route('/content')
def content_list():
    """Content list page."""
    dashboard = Dashboard()
    return jsonify(dashboard.content_df.to_dict(orient='records'))

@app.route('/models')
def model_comparison():
    """Model comparison page."""
    dashboard = Dashboard()
    return jsonify(dashboard.get_model_performance().to_dict(orient='records'))

@app.route('/dependencies')
def dependencies():
    """Dependencies page."""
    dashboard = Dashboard()
    G = dashboard.get_dependency_graph()
    return jsonify({
        'nodes': [{'id': n, **G.nodes[n]} for n in G.nodes()],
        'edges': [{'source': u, 'target': v} for u, v in G.edges()]
    })

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files."""
    return send_from_directory('dashboard_static', path)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="AI Hub Content Dashboard")
    parser.add_argument("--port", type=int, default=8082, help="Port to run the dashboard on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run the dashboard on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Run the app
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()

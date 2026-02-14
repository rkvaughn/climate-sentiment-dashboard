import networkx as nx
import json

# 1. Load your sources
with open('climate_sources.json') as f:
    data = json.load(f)

# 2. Initialize Graph
G = nx.DiGraph()

# 3. Add Nodes (Sources)
for source in data['sources']:
    G.add_node(source['id'], type=source['type'])

# 4. Add Edges (Simulated Data)
# In production, you populate this by crawling the RSS feeds and parsing <a href> tags.
# Example: Carbon Brief (carbon_brief) links to a Nature study (nature_climate)
edges = [
    ("carbon_brief", "nature_climate"),
    ("guardian_environment", "ipcc_ch"),
    ("nyt_climate", "nasa_climate"),
    ("inside_climate_news", "epa_gov"), # Assuming you add EPA
    ("grist", "nyt_climate")
]
G.add_edges_from(edges)

# 5. Calculate PageRank
# 'personalization' parameter allows us to bias the rank towards our "Scientific Authorities"
# This ensures that being close to the science > being viral.
scientific_nodes = {n: 1.0 if G.nodes[n].get('type') == 'Scientific Authority' else 0.1 for n in G.nodes}

rankings = nx.pagerank(G, alpha=0.85, personalization=scientific_nodes)

# 6. Output Weights for Dashboard
print(json.dumps(rankings, indent=2))
import xml.etree.ElementTree as ET

from exports.gephi import export_graphml

output_path = export_graphml()

print(f"GraphML exported to: {output_path}")

tree = ET.parse(output_path)
root = tree.getroot()

ns = {"g": "http://graphml.graphdrawing.org/xmlns"}

graph = root.find("g:graph", ns)

nodes = graph.findall("g:node", ns)
edges = graph.findall("g:edge", ns)

print(f"Validated nodes: {len(nodes)}")
print(f"Validated edges: {len(edges)}")
print(f"Edge default: {graph.get('edgedefault')}")
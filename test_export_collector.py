from exports.data_collector import collect_export_data

data = collect_export_data()

print(f"Nodes: {len(data['nodes'])}")
print(f"Edges: {len(data['edges'])}")

print("\nFirst node:")
if data["nodes"]:
    print(data["nodes"][0])

print("\nFirst edge:")
if data["edges"]:
    print(data["edges"][0])
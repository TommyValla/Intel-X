
from exports.obsidian import export_obsidian

output_dir = export_obsidian()

print(f"Obsidian export created at: {output_dir}")
print(f"Markdown files: {len(list(output_dir.glob('*.md')))}")

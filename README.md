# Intel-X

**A desktop application for managing, exploring, and visualizing entity networks.**

Intel-X is a Python desktop application for intelligence-style research and knowledge management. It provides a structured way to maintain information about people and organizations, document their relationships, and explore connections through an interactive network graph.

The project is a personal development project focused on learning Python application development, database design, and network visualization.

## Features

- **Entity management** — create and edit records for people and organizations.
- **Relationship management** — record relationships between people, organizations, and other organizations, including roles, dates, and notes.
- **Interactive network visualization** — explore entities and their connections in a graphical network view.
- **Network exploration** — focus on a selected entity and inspect its connections within a configurable radius of one to three hops.
- **Temporal exploration** — filter the network by date to examine relationships over time.
- **Entity dossiers** — maintain structured Markdown dossiers with biographical information, organizational affiliations, timelines, sources, and notes.
- **Project management** — create and open separate projects, each with its own SQLite database and supporting files.
- **Gephi export** — export network data as GraphML for further analysis and visualization in Gephi.
- **Obsidian export** — export entities and relationships as linked Markdown notes, including existing dossier content.

## Technology stack

- **Python** — application logic and data processing.
- **PySide6** — graphical user interface and interactive network view.
- **SQLite** — structured storage for entities and relationships.
- **Markdown** — human-readable entity dossiers and Obsidian-compatible exports.
- **GraphML** — network data interchange for Gephi and other compatible tools.

## Installation

### Requirements

- Python 3.10 or later.
- Git.
- PySide6.

### 1. Clone the repository

```bash
git clone https://github.com/TommyValla/Intel-X.git
cd Intel-X
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependency

```bash
python -m pip install PySide6
```

## Running the application

From the repository root, run:

```bash
python main.py
```

At startup, Intel-X prompts you to select a valid project folder. A project contains a `project.json` configuration file, a SQLite database, and a dossiers directory.

Once a project is open, use the **File** menu to create a new project or open another existing project.

## Using Intel-X

### Managing entities

Use the entity tree to browse people and organizations. Select an entity to inspect its attributes, edit its information, or open its dossier.

### Exploring relationships

Relationships can be inspected through the entity interface and the network view. Select a node to inspect the corresponding entity, use **Focus** to explore its surrounding network, and adjust the hop radius to control the scope of the view.

The date slider filters the network to explore connections at different points in time.

### Working with dossiers

Dossiers are stored as Markdown files within the active project. They provide a space for structured research notes, biographies, organizational histories, timelines, and source references.

### Exporting network data

Intel-X provides two export formats:

- **GraphML:** suitable for importing the network into Gephi for further visualization and analysis.
- **Obsidian Markdown:** creates linked notes for entities and their relationships, with existing dossier content included where available.

Exports are generated from the active project's data. Keep generated exports separate from the application source code.

## Project structure

```text
Intel-X/
├── assets/
│   └── icons/          # Entity icons
├── data/
│   ├── database.py     # Database operations
│   ├── project.py      # Project management and paths
│   └── schema.py       # Database schema initialization
├── dossier/
│   └── manager.py      # Dossier creation and management
├── dossiers/           # Project dossier files
├── exports/
│   ├── data_collector.py
│   ├── gephi.py        # GraphML export
│   └── obsidian.py     # Markdown vault export
├── network/
│   ├── edge.py
│   ├── graph.py
│   ├── node.py
│   └── view.py         # Network visualization
├── ui/                 # Dialogs and interface components
├── main.py             # Application entry point
└── README.md
```

## Development and testing

The repository includes standalone test scripts for project management, database schema initialization, and network export functionality.

Run an individual test from the repository root, for example:

```bash
python test_schema.py
python test_project.py
python test_export_collector.py
python test_gephi_export.py
python test_obsidian_export.py
```

Some tests create project directories or export files. Run them with this in mind and inspect their output before removing any generated files.

## Current status

Intel-X is an evolving prototype. Features and internal interfaces may change as the project develops. The included tests and export workflows support ongoing development, but the application has not been presented as a production-ready intelligence platform.

## License

No license has been specified yet. Unless a license is added to the repository, reuse and redistribution are subject to the applicable default copyright rules.

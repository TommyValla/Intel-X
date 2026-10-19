
from data.project import (
    open_project,
    get_project_root,
    get_database_path,
)

metadata = open_project(r"C:\Intel-X-test-project")

print("Project:", metadata["name"])
print("Root:", get_project_root())
print("Database:", get_database_path())

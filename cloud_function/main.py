import os
from .utils import create_hub_structure

def main(request):
    print("Agentic AI Content Creation Triggered!")

    # Define the base directory for the Hub content
    base_dir = "HubContent"

    # Define the list of directories to create relative to the base_dir
    # Using standard characters instead of symbols for compatibility
    directories_to_create = [
        "",  # Create the base directory itself
        "Standards",
        "Standards/StyleGuide",
        "Standards/OutlineTemplates",
        "Standards/ReviewChecklists",
        "Standards/Personas",
        "Standards/MissionResources",
        "Standards/MissionResources/ResponsibleAI_Frameworks",
        "Standards/OperationalDocs",
        "HomePage",
        "HomePage/Assets",
        "LearnAI",
        "LearnAI/Beginner",
        "LearnAI/Beginner/_TemplateContent",  # Placeholder for module folders
        "LearnAI/Beginner/Assessments",
        "LearnAI/Intermediate",
        "LearnAI/Intermediate/_TemplateContent",  # Placeholder
        "LearnAI/Intermediate/Assessments",
        "LearnAI/Expert",
        "LearnAI/Expert/_TemplateContent",  # Placeholder
        "LearnAI/Expert/Assessments",
    ]  # truncated for brevity

    create_hub_structure(base_dir, directories_to_create)

    return "Agentic AI Content Creation Triggered! Directory structure created."
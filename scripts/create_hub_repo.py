import os

# Define the base directory for the Hub content
base_dir = "HubContent"

# Define the list of directories to create relative to the base_dir
# Using standard characters instead of symbols for compatibility
directories_to_create = [
    "", # Create the base directory itself
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
    "LearnAI/Beginner/_TemplateContent", # Placeholder for module folders
    "LearnAI/Beginner/Assessments",
    "LearnAI/Intermediate",
    "LearnAI/Intermediate/_TemplateContent", # Placeholder
    "LearnAI/Intermediate/Assessments",
    "LearnAI/Expert",
    "LearnAI/Expert/_TemplateContent", # Placeholder
    "LearnAI/Expert/Assessments",
    "ApplyAI",
    "ApplyAI/SME_Playbooks",
    "ApplyAI/SME_Playbooks/_TemplateSector", # Placeholder for specific sectors
    "ApplyAI/SME_Playbooks/_TemplateSector/Assets",
    "ApplyAI/CaseStudies",
    "ApplyAI/CaseStudies/_TemplateCaseStudy", # Placeholder for specific case studies
    "ApplyAI/CaseStudies/_TemplateCaseStudy/Data",
    "ApplyAI/CaseStudies/_TemplateCaseStudy/Assets",
    "ApplyAI/Templates_Toolkits",
    "ApplyAI/Templates_Toolkits/_TemplateTool", # Placeholder for specific templates/tools
    "ApplyAI/SupportDirectory",
    "CommunityHub",
    "ResponsibleAI_Sustainability",
    "ResponsibleAI_Sustainability/PolicySummaries",
    "ResponsibleAI_Sustainability/Frameworks",
    "ResponsibleAI_Sustainability/Tools", # For lists/guides of tools
    "ResponsibleAI_Sustainability/ResearchReports", # If hosting reports
    "CareerReskilling",
    "CareerReskilling/Roadmaps",
    "GlobalInclusionLab",
    "GlobalInclusionLab/RegionalSpotlights",
    "GlobalInclusionLab/TranslatedContent", # For translated content structure
    "GlobalInclusionLab/OfflineToolkits", # For source content of toolkits
    "DeveloperToolkit",
    "DeveloperToolkit/Libraries", # For lists/guides of libraries
    "DeveloperToolkit/DeploymentTemplates",
    "DeveloperToolkit/DeploymentTemplates/_TemplateSpecific", # Placeholder for specific templates
    "DeveloperToolkit/PromptEngineering", # For templates/guides
    "BlogPodcast",
    "BlogPodcast/BlogPosts",
    "BlogPodcast/BlogPosts/Assets",
    "BlogPodcast/PodcastSummaries",
    "ImpactDashboard",
    "ImpactDashboard/TransparencyReports",
    "ModerationGovernance", # Operational docs
    "SharedResources", # General contributor/user resources (excluding standards/operational)
    "SuggestedTools_Stack" # High-level tech stack notes
]

def create_hub_structure(base_directory, directory_list):
    """
    Creates the specified directory structure relative to a base directory.

    Args:
        base_directory (str): The root directory name.
        directory_list (list): A list of subdirectories to create.
    """
    print(f"Creating directory structure under ./{base_directory}/")

    for dir_path in directory_list:
        # Construct the full path
        full_path = os.path.join(base_directory, dir_path)

        try:
            # Use os.makedirs to create the directory and any necessary parents
            # exist_ok=True prevents errors if the directory already exists
            os.makedirs(full_path, exist_ok=True)
            print(f"Created: {full_path}")
        except OSError as e:
            print(f"Error creating directory {full_path}: {e}")
        except Exception as e:
             print(f"An unexpected error occurred for {full_path}: {e}")


if __name__ == "__main__":
    create_hub_structure(base_dir, directories_to_create)
    print("\nRepository structure creation process finished.")
    print(f"Check the ./{base_dir}/ directory.")
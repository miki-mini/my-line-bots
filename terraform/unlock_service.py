import subprocess
import sys
import re

SERVICE_NAME = "voidoll-bot"
REGION = "asia-northeast1"
PROJECT_ID = "usaginooekaki"

def run_command(command):
    try:
        result = subprocess.run(
            command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e.stderr)
        sys.exit(1)

print(f"Fetching configuration for {SERVICE_NAME}...")
# Fetch current config in YAML
yaml_config = run_command(f"gcloud run services describe {SERVICE_NAME} --region {REGION} --project {PROJECT_ID} --format=yaml")

# Check if deletion protection is enabled
if "deletionProtection: true" in yaml_config or "run.googleapis.com/deletion-protection': 'true'" in yaml_config:
    print("Deletion protection found. Disabling...")

    # Simple string replacement to disable it
    # Handle main field
    new_config = yaml_config.replace("deletionProtection: true", "deletionProtection: false")

    # Handle annotation just in case (v1 style fallback)
    new_config = new_config.replace("'run.googleapis.com/deletion-protection': 'true'", "'run.googleapis.com/deletion-protection': 'false'")
    new_config = new_config.replace('"run.googleapis.com/deletion-protection": "true"', '"run.googleapis.com/deletion-protection": "false"')

    # Save to temp file
    with open("temp_service.yaml", "w", encoding="utf-8") as f:
        f.write(new_config)

    print("Applying updated configuration...")
    run_command(f"gcloud run services replace temp_service.yaml --region {REGION} --project {PROJECT_ID}")
    print("Success! Deletion protection disabled.")
else:
    print("Deletion protection does not seem to be enabled in the YAML, or format differs.")
    print("Proceeding to delete attempt just in case...")

# Try to delete it (optional, but Terraform wants to destroy it anyway)
# We won't delete it here, letting Terraform do its job.

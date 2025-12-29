import subprocess
import json

try:
    cmd = [
        "gcloud.cmd", "run", "revisions", "list",
        "--service", "usagi-oekaki-service",
        "--limit", "5",
        "--format", "json",
        "--region", "asia-northeast1"
    ]
    result = subprocess.run(cmd, capture_output=True, shell=True)
    revisions = json.loads(result.stdout)

    print(f"{'REVISION':<35} {'ACTIVE':<10} {'CREATED':<30}")
    print("-" * 75)
    for rev in revisions:
        name = rev.get('metadata', {}).get('name', 'UNKNOWN')
        active = str(rev.get('status', {}).get('conditions', [{}])[0].get('status', 'Unknown')) # Approximate
        created = rev.get('metadata', {}).get('creationTimestamp', 'UNKNOWN')
        print(f"{name:<35} {active:<10} {created:<30}")

except Exception as e:
    print(e)

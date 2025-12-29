import subprocess
import json
import os

print("Fetching logs...")
try:
    cmd = [
        "gcloud.cmd", "logging", "read",
        "resource.type=cloud_run_revision AND resource.labels.service_name=usagi-oekaki-service",
        "--limit", "30",
        "--format", "json",
    ]

    result = subprocess.run(cmd, capture_output=True, shell=True)

    if result.returncode != 0:
        print("Error fetching logs:")
        print(result.stderr.decode('utf-8', errors='ignore'))
        exit(1)

    logs_data = result.stdout.decode('utf-8', errors='ignore')
    logs = json.loads(logs_data)

    print(f"Fetched {len(logs)} log entries.")

    with open("latest_logs_3.txt", "w", encoding="utf-8") as f_out:
        for entry in logs:
            timestamp = entry.get('timestamp', 'UNKNOWN')
            severity = entry.get('severity', 'UNKNOWN')
            revision = entry.get('resource', {}).get('labels', {}).get('revision_name', 'UNKNOWN')
            text = entry.get("textPayload", "")
            data = entry.get("jsonPayload", {})

            f_out.write(f"[{timestamp}] {severity} {revision}\n")
            if text:
                f_out.write(f"{text}\n")
            if data:
                f_out.write(f"{json.dumps(data, indent=2, ensure_ascii=False)}\n")
            f_out.write("-" * 40 + "\n")

    print("Logs written to latest_logs_3.txt")

except Exception as e:
    print(f"Script Error: {e}")

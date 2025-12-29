import subprocess
import json
import os

print("Fetching logs...")
try:
    cmd = [
        "gcloud.cmd", "logging", "read",
        "resource.type=cloud_run_revision AND resource.labels.service_name=usagi-oekaki-service",
        "--limit", "50",
        "--format", "json"
    ]

    result = subprocess.run(cmd, capture_output=True, shell=True)

    if result.returncode != 0:
        print("Error fetching logs:")
        print(result.stderr.decode('utf-8', errors='ignore'))
        exit(1)

    logs_data = result.stdout.decode('utf-8', errors='ignore')
    logs = json.loads(logs_data)

    print(f"Fetched {len(logs)} log entries.")

    with open("logs_final.txt", "w", encoding="utf-8") as f_out:
        found_error = False
        for entry in logs:
            text = entry.get("textPayload", "")
            data = entry.get("jsonPayload", {})

            full_text = text + str(data)

            if "Traceback" in full_text or "Error" in full_text or "Exception" in full_text:
                msg = f"\n[{entry['timestamp']}] Severity: {entry.get('severity')}\n"
                msg += text if text else json.dumps(data, indent=2)
                f_out.write(msg + "\n")
                found_error = True

        if not found_error:
            f_out.write("No explicit error keywords found in last 50 logs.\n")
            for entry in logs[:5]:
                 f_out.write(f"\n[{entry['timestamp']}] {entry.get('textPayload')}\n")

    print("Logs written to logs_final.txt")

except Exception as e:
    print(f"Script Error: {e}")

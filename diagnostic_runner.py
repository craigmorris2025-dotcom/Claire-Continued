import subprocess
import traceback
import datetime
import os
import sys
import time
import urllib.request
import urllib.error

OUTPUT = "claire_full_diagnostic.txt"
LAUNCHER = "LAUNCH.bat"

def log(text):
    with open(OUTPUT, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def run_section(title, cmd, timeout=None):
    log(f"\n=== {title} ===")
    log(f"Command: {cmd}\n")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )

        log("----- STDOUT -----")
        log(result.stdout)

        log("----- STDERR -----")
        log(result.stderr)

        if result.returncode != 0:
            log(f"[ERROR] Exit code {result.returncode}")
            return False

        log("[OK]")
        return True

    except subprocess.TimeoutExpired as e:
        log("[TIMEOUT] Command did not finish in time.")
        log("----- PARTIAL STDOUT -----")
        log(e.stdout or "")
        log("----- PARTIAL STDERR -----")
        log(e.stderr or "")
        return False

    except Exception:
        log("[EXCEPTION]")
        log(traceback.format_exc())
        return False

def http_check(title, url):
    log(f"\n=== HTTP CHECK: {title} ===")
    log(f"URL: {url}\n")
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            log(f"Status: {resp.status}")
            log("----- RESPONSE BODY (truncated) -----")
            log(body[:2000])
            log("[OK]")
            return True
    except urllib.error.HTTPError as e:
        log(f"[HTTP ERROR] {e.code} {e.reason}")
        return False
    except Exception:
        log("[EXCEPTION]")
        log(traceback.format_exc())
        return False

def main():
    # Reset output file
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("=== CLAIRE FULL SYSTEM DIAGNOSTIC (END-TO-END TO UI) ===\n")
        f.write(f"Timestamp: {datetime.datetime.now()}\n\n")

    ok = True

    # 1. Environment info
    ok &= run_section("Python Version", "python --version")
    ok &= run_section("Environment Variables", "set")

    # 2. Project structure
    ok &= run_section("Project Structure", "tree /F src")

    # 3. Backend import test (Windows-safe)
    ok &= run_section(
        "Backend Import Test",
        'python -c "import backend.server; print(\'Backend import OK\')"'
    )

    # 4. App factory test (Windows-safe)
    ok &= run_section(
        "FastAPI App Factory Test",
        'python -c "from backend.server import create_app; app = create_app(); print(\'App created OK\')"'
    )

    # 5. Run LAUNCH.bat but DO NOT LET IT BLOCK
    if os.path.exists(LAUNCHER):
        ok &= run_section(
            "System Launcher (LAUNCH.bat)",
            LAUNCHER,
            timeout=5  # prevent blocking forever
        )
    else:
        log(f"\n[WARN] {LAUNCHER} not found, skipping launcher section.")

    # 6. Direct backend run to reach the UI reliably
    log("\n=== STARTING BACKEND DIRECTLY FOR UI TESTS ===")
    server_cmd = "python src/main.py"
    log(f"Command: {server_cmd}\n")

    try:
        server_proc = subprocess.Popen(
            server_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
    except Exception:
        log("[EXCEPTION] Failed to start backend directly")
        log(traceback.format_exc())
        log("\n=== DIAGNOSTIC FAILED ===")
        sys.exit(1)

    # Give the server time to start
    time.sleep(8)

    # 7. UI / HTTP checks
    ui_ok = True
    ui_ok &= http_check("Root UI", "http://127.0.0.1:8000/")
    ui_ok &= http_check("Dashboard (likely)", "http://127.0.0.1:8000/index.html")
    ui_ok &= http_check("API Health (if exists)", "http://127.0.0.1:8000/api")

    # 8. Collect server output and shut it down
    log("\n=== BACKEND PROCESS OUTPUT ===")
    try:
        server_proc.terminate()
        try:
            stdout, stderr = server_proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()
            stdout, stderr = server_proc.communicate()

        log("----- STDOUT -----")
        log(stdout)
        log("----- STDERR -----")
        log(stderr)
    except Exception:
        log("[EXCEPTION] While collecting backend output")
        log(traceback.format_exc())

    ok &= ui_ok

    # Final status
    if not ok:
        log("\n=== DIAGNOSTIC FAILED (SEE ALL SECTIONS ABOVE) ===")
        sys.exit(1)

    log("\n=== DIAGNOSTIC PASSED (END-TO-END TO UI) ===")
    sys.exit(0)

if __name__ == "__main__":
    main()
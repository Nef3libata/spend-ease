import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "dashboard":
        # Launch web dashboard
        import subprocess
        from pathlib import Path

        dashboard_path = Path(__file__).parent / "dashboard.py"
        subprocess.run(["streamlit", "run", str(dashboard_path)])
    else:
        # Launch CLI (default)
        from spend_ease.cli import main as cli_main

        cli_main()


if __name__ == "__main__":
    main()

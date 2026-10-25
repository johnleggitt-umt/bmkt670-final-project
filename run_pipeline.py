import subprocess
import sys

# Extract steps take a long time (~ three - four hours) to run. Set this value to True if you want them to run.
run_extract_steps = False

# Scripts to run, in order
extract_steps = [
    "etl/extract_1.py",         # extract: SteamSpy top 2000 games
    "etl/extract_2.py",         # extract: Extract SteamWorks info for those 2000 games
    "etl/extract_3.py",         # extract: Extract SteamCharts info for those 2000 games
    "etl/extract_4.py",          # extract: Extract SteamSpy detailed info for those 2000 games
]

transform_steps = [
    "etl/transform.py",         # clean, match keys, reshape, build features
    "etl/load.py",              # empty tables, then load into Postgres
    "etl/quality_checks.py",    # print PASS/FAIL for each check
]

if run_extract_steps:
    print("Running Data Extraction steps:")
    for step in extract_steps:
        print(f"\n=== Running {step} ===")
        result = subprocess.run([sys.executable, step])

        if result.returncode != 0:
            print(f"\nStopped: {step} failed. Fix it and run again.")
            sys.exit(1)
else:
    print("Skipping data extraction")

print("Running Data Transformation steps:")
for step in transform_steps:
    print(f"\n=== Running {step} ===")
    result = subprocess.run([sys.executable, step])

    if result.returncode != 0:
        print(f"\nStopped: {step} failed. Fix it and run again.")
        sys.exit(1)

print("\nPipeline finished.")
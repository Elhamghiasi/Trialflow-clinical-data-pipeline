"""Run the complete lightweight TrialFlow workflow."""

from pathlib import Path

from src.generate_synthetic_data import write_dataset
from src.pipeline import run_pipeline


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parent
    write_dataset(project_dir / "data" / "raw" / "synthetic_clinical_data.csv")
    results = run_pipeline(project_dir)
    print("TrialFlow completed")
    for name, value in results.items():
        print(f"  {name}: {value}")


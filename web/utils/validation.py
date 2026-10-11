
import pandas as pd


def validate_dataframe(df: pd.DataFrame, name: str) -> list[str]:
    """Return data-quality issues found in a dataset."""
    issues = []

    if df.empty:
        issues.append(f"{name}: dataset is empty")
        return issues

    if df.columns.duplicated().any():
        issues.append(f"{name}: duplicate column names found")

    if df.isnull().values.any():
        missing = int(df.isnull().sum().sum())
        issues.append(f"{name}: {missing} missing value(s)")

    duplicate_rows = int(df.duplicated().sum())
    if duplicate_rows:
        issues.append(f"{name}: {duplicate_rows} duplicate row(s)")

    return issues
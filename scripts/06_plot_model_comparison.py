from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "results" / "final_model_comparison_table.csv"
OUTPUT_PNG = ROOT / "assets" / "04_model_metric_comparison_v2.png"

SELECTED_MODEL = "BiomedCLIP adapter probe"
METRICS = [
    "Sensitivity",
    "Specificity",
    "Precision",
    "F1",
    "Macro F1",
    "AUROC",
    "AUPRC",
]

DISPLAY_NAMES = {
    "BiomedCLIP zero-shot": "BiomedCLIP\nZero-shot",
    "BiomedCLIP linear probe": "BiomedCLIP\nLinear Probe",
    "BiomedCLIP adapter probe": "BiomedCLIP\nAdapter Probe",
    "BiomedCLIP LoRA": "BiomedCLIP\nLoRA",
    "BiomedCLIP Internal Adapter": "BiomedCLIP\nInternal Adapter*",
    "EfficientNet CNN baseline": "EfficientNet\nCNN Baseline",
}


def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    df = df[df["Method"].isin(DISPLAY_NAMES)].copy()

    # Keep the repository comparison order stable.
    df["Method"] = pd.Categorical(
        df["Method"], categories=list(DISPLAY_NAMES.keys()), ordered=True
    )
    df = df.sort_values("Method")

    table_data = []
    for _, row in df.iterrows():
        table_data.append(
            [DISPLAY_NAMES[str(row["Method"])]]
            + [f"{float(row[m]):.3f}" for m in METRICS]
        )

    columns = ["Model"] + METRICS

    fig, ax = plt.subplots(figsize=(16, 6.6))
    ax.axis("off")

    table = ax.table(
        cellText=table_data,
        colLabels=columns,
        cellLoc="center",
        colLoc="center",
        loc="center",
        bbox=[0.02, 0.15, 0.96, 0.73],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10.5)

    # Header styling.
    for col in range(len(columns)):
        cell = table[(0, col)]
        cell.set_facecolor("#E9EEF5")
        cell.set_text_props(weight="bold", color="#1F2937")
        cell.set_edgecolor("#AAB4C0")
        cell.set_linewidth(1.1)

    selected_row = None
    for row_idx, (_, row) in enumerate(df.iterrows(), start=1):
        is_selected = str(row["Method"]) == SELECTED_MODEL
        if is_selected:
            selected_row = row_idx

        for col_idx in range(len(columns)):
            cell = table[(row_idx, col_idx)]
            cell.set_edgecolor("#C9D1D9")
            cell.set_linewidth(0.8)

            if is_selected:
                # Stronger than the previous pale-yellow highlight.
                cell.set_facecolor("#FFD6D6")
                cell.set_text_props(color="#B71C1C", weight="bold")
                cell.set_edgecolor("#D32F2F")
                cell.set_linewidth(2.0)
            elif row_idx % 2 == 0:
                cell.set_facecolor("#F7F9FB")
            else:
                cell.set_facecolor("#FFFFFF")

    # Slightly widen the model-name column.
    for row_idx in range(len(df) + 1):
        table[(row_idx, 0)].set_width(0.20)

    ax.text(
        0.5,
        0.955,
        "Model Performance Comparison",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=18,
        weight="bold",
        color="#111827",
    )

    ax.text(
        0.5,
        0.905,
        "Patient-level evaluation metrics",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=10.5,
        color="#4B5563",
    )

    ax.text(
        0.02,
        0.105,
        "FINAL SELECTED CLASSIFIER  —  BiomedCLIP Adapter Probe",
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=12,
        weight="bold",
        color="#B71C1C",
        bbox={
            "boxstyle": "round,pad=0.45",
            "facecolor": "#FFD6D6",
            "edgecolor": "#D32F2F",
            "linewidth": 1.8,
        },
    )

    ax.text(
        0.02,
        0.035,
        "Selected for sensitivity-first screening and parameter-efficient foundation-model adaptation. "
        "EfficientNet remains stronger on AUROC/AUPRC.  *Internal Adapter: Fold 1 only.",
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=9.3,
        color="#4B5563",
    )

    fig.savefig(OUTPUT_PNG, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"Saved: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_research_plots():
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    plots_dir = os.path.join(results_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    # 1. Three-Way Baseline Comparison Chart
    comp_csv = os.path.join(results_dir, "baseline_comparison.csv")
    if os.path.exists(comp_csv):
        df_comp = pd.read_csv(comp_csv)
        fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
        x = np.arange(len(df_comp))
        width = 0.25

        ax.bar(x - width, df_comp["Accuracy (%)"], width, label="Classification Accuracy (%)", color="#3b82f6")
        ax.bar(x, df_comp["Automation Rate (%)"], width, label="Automation Rate (%)", color="#10b981")
        ax.bar(x + width, df_comp["Unsafe Auto Rate (%)"], width, label="Unsafe Auto-Exec Rate (%)", color="#ef4444")

        ax.set_ylabel("Percentage (%)", fontsize=11, fontweight='bold')
        ax.set_title("Three-Way Baseline Comparison: Accuracy vs Automation vs Safety", fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(["Rule-Only", "AI-Only (No Policy)", "Hybrid AI+Policy"], fontsize=10)
        ax.legend(loc='upper right', frameon=True)
        ax.set_ylim(0, 115)
        plt.tight_layout()
        plot1_path = os.path.join(plots_dir, "baseline_comparison.png")
        plt.savefig(plot1_path)
        plt.close()
        print(f"Plot 1 saved: '{plot1_path}'")

    # 2. Multi-Dimensional Robustness Degradation Curve
    rob_csv = os.path.join(results_dir, "robustness_metrics.csv")
    if os.path.exists(rob_csv):
        df_rob = pd.read_csv(rob_csv)
        fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)

        labels = [f"{row['Perturbation Type'][:10]}\n{row['Perturbation Level']}" for _, row in df_rob.iterrows()]
        x_indices = range(len(df_rob))

        color = '#2563eb'
        ax1.set_xlabel('Perturbation Condition', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Accuracy / Macro F1 (%)', color=color, fontsize=11, fontweight='bold')
        l1 = ax1.plot(x_indices, df_rob['Accuracy (%)'], marker='o', color='#2563eb', linewidth=2.5, label='Classification Accuracy')
        l2 = ax1.plot(x_indices, df_rob['Macro F1 (%)'], marker='s', color='#7c3aed', linewidth=2, linestyle='--', label='Macro F1-Score')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim(85, 105)

        ax2 = ax1.twinx()
        color = '#d97706'
        ax2.set_ylabel('Mean AI Confidence Score', color=color, fontsize=11, fontweight='bold')
        l3 = ax2.plot(x_indices, df_rob['Avg AI Confidence'], marker='^', color='#d97706', linewidth=2, linestyle=':', label='AI Confidence Score')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0.50, 1.05)

        lines = l1 + l2 + l3
        labels_leg = [l.get_label() for l in lines]
        ax1.legend(lines, labels_leg, loc='lower left', frameon=True)

        plt.title('Multi-Dimensional Robustness & Uncertainty Degradation', fontsize=12, fontweight='bold')
        ax1.set_xticks(list(x_indices))
        ax1.set_xticklabels(labels, fontsize=9)
        plt.tight_layout()
        plot2_path = os.path.join(plots_dir, "robustness_degradation_curve.png")
        plt.savefig(plot2_path)
        plt.close()
        print(f"Plot 2 saved: '{plot2_path}'")

    # 3. Confusion Matrix Heatmap
    conf_csv = os.path.join(results_dir, "confusion_matrix.csv")
    if os.path.exists(conf_csv):
        df_conf = pd.read_csv(conf_csv, index_col=0)
        fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
        cax = ax.matshow(df_conf.values, cmap='Blues')
        fig.colorbar(cax)

        classes = ["Invoice", "Service Req", "Unknown (OOD)"]
        ax.set_xticks(range(len(classes)))
        ax.set_yticks(range(len(classes)))
        ax.set_xticklabels(classes, fontsize=10)
        ax.set_yticklabels(classes, fontsize=10)

        for i in range(len(classes)):
            for j in range(len(classes)):
                ax.text(j, i, str(df_conf.values[i, j]), ha='center', va='center', color='black' if df_conf.values[i, j] < df_conf.values.max()/2 else 'white', fontweight='bold', fontsize=12)

        plt.xlabel('Predicted Label', fontsize=11, fontweight='bold')
        plt.ylabel('True Ground Truth Label', fontsize=11, fontweight='bold')
        plt.title('Confusion Matrix (TF-IDF + Logistic Regression)', fontsize=12, fontweight='bold', pad=15)
        plt.tight_layout()
        plot3_path = os.path.join(plots_dir, "confusion_matrix_heatmap.png")
        plt.savefig(plot3_path)
        plt.close()
        print(f"Plot 3 saved: '{plot3_path}'")

if __name__ == "__main__":
    generate_research_plots()

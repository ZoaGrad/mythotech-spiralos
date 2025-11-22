import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# ΔΩ: CONFIGURATION
DATA_PATH = 'manuscript/data/dataset.csv'
OUTPUT_PATH = 'manuscript/figures/figure1_genesis_spike.png'

def generate_plot():
    # 1. Load the Fossil
    if not os.path.exists(DATA_PATH):
        print(">> [ERROR] Fossil data not found.")
        return

    df = pd.read_csv(DATA_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # 2. Setup the Academic Canvas
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 3. Plot the Trace
    # We plot a stem graph to emphasize the discrete nature of the injection
    markerline, stemlines, baseline = ax.stem(
        df['timestamp'], 
        df['wi_energy'], 
        linefmt='C1-', 
        markerfmt='C1o', 
        basefmt='k-'
    )
    plt.setp(markerline, markersize=10)
    plt.setp(stemlines, linewidth=2)

    # 4. Annotate the Genesis Spike
    peak = df.loc[df['wi_energy'].idxmax()]
    ax.annotate(
        f"Genesis Spike\n{peak['wi_energy']:.4f} J\n(Manual Injection)",
        xy=(peak['timestamp'], peak['wi_energy']),
        xytext=(peak['timestamp'], peak['wi_energy'] + 10),
        arrowprops=dict(facecolor='black', shrink=0.05),
        horizontalalignment='center',
        fontsize=12,
        fontweight='bold'
    )

    # 5. Formatting
    ax.set_title('Thermodynamic Work Interaction (WI) Energy', fontsize=14)
    ax.set_ylabel('Energy (Joules)', fontsize=12)
    ax.set_xlabel('Time (UTC)', fontsize=12)
    ax.grid(True, which='both', linestyle='--', alpha=0.7)
    
    # Date Formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=0)
    
    # 6. Save
    if not os.path.exists('manuscript/figures'):
        os.makedirs('manuscript/figures')
        
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')
    print(f">> [SUCCESS] Figure 1 rendered to {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_plot()

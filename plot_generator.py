import os
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates

# Use a non-interactive backend for Matplotlib to prevent GUI issues
matplotlib.use('Agg')

def plot_anomalies(df, coin_name, anomalies_df, output_dir='public/pred'):
    """
    Plots price trends with detected anomalies and saves the plot as a PNG.

    :param df: DataFrame with price and volume data
    :param coin_name: Name of the cryptocurrency
    :param anomalies_df: DataFrame of detected anomalies
    :param output_dir: Directory to save the plot image
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.style.use('default')

    # Adjust figure size for better web display
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#111827")

    ax.plot(df.index, df['value'], color="#5990E7", label='Price')

    # Plot anomalies if they exist
    if not anomalies_df.empty:
        ax.scatter(anomalies_df.index, anomalies_df['value'], color="#DE7D16", s=50, zorder=5, label='Anomalies')

    text_color = '#F8FAFC'
    muted_text_color = '#CBD5E1'
    ax.set_title(f"{coin_name.capitalize()} Price with Anomalies", color=text_color, fontsize=16)
    ax.set_xlabel('Date', color=muted_text_color, fontsize=12)
    ax.set_ylabel('Price (USD)', color=muted_text_color, fontsize=12)

    # Customize the legend text color
    ax.legend(facecolor='#F8FAFC', framealpha=0.9, fontsize=10, labelcolor='#0F172A')

    # --- FIX for X-axis labels ---
    # Use Matplotlib's date formatters for correct date display
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    # Set tick label colors
    ax.tick_params(axis='x', colors=muted_text_color, labelsize=10)
    ax.tick_params(axis='y', colors=muted_text_color, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color('#334155')

    # Set grid color to a lighter gray for better contrast
    ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='#64748B', alpha=0.35)

    # Automatically format date labels on the X-axis for better readability
    fig.autofmt_xdate()

    # Save the plot
    file_path = os.path.join(output_dir, f"{coin_name}_analysis.png")
    plt.savefig(file_path, transparent=False, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    return file_path

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FuncFormatter
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

    # Use a dark background theme for the plot
    plt.style.use('dark_background')

    # Adjust figure size for better web display
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(df.index, df['value'], color="#5990E7", label='Price')

    # Plot anomalies if they exist
    if not anomalies_df.empty:
        ax.scatter(anomalies_df.index, anomalies_df['value'], color="#DE7D16", s=50, zorder=5, label='Anomalies')

    # Set labels and title to a dark color for visibility on a light background
    # CORRECTED LINE: Change text_color to white for visibility on dark background
    text_color = '#FFFFFF' 
    ax.set_title(f"{coin_name.capitalize()} Price with Anomalies", color=text_color, fontsize=16)
    ax.set_xlabel('Date', color=text_color, fontsize=12)
    ax.set_ylabel('Price (USD)', color=text_color, fontsize=12)

    # Customize the legend text color
    ax.legend(facecolor='white', framealpha=0.7, fontsize=10, labelcolor='#080808')

    # --- FIX for X-axis labels ---
    # Use Matplotlib's date formatters for correct date display
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    # Set tick label colors
    ax.tick_params(axis='x', colors=text_color, labelsize=10)
    ax.tick_params(axis='y', colors=text_color, labelsize=10)

    # Set grid color to a lighter gray for better contrast
    ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)

    # Automatically format date labels on the X-axis for better readability
    fig.autofmt_xdate()

    # Save the plot
    file_path = os.path.join(output_dir, f"{coin_name}_analysis.png")
    plt.savefig(file_path, transparent=True, bbox_inches='tight')
    plt.close(fig)
    return file_path
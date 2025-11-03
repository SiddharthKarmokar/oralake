import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# 15 simulated upload records
np.random.seed(42)
image_ids = np.arange(1, 16)

# Saved size in KB
file_sizes_kb = np.array([
    191.7, 26.9, 827.4, 591.0, 935.3, 183.0,
    450.2, 720.5, 310.8, 640.7, 510.4, 880.9,
    275.6, 990.2, 120.4
])

# Processing times in ms (roughly correlated to file size)
processing_times = np.array([
    331.3, 70.4, 631.6, 504.7, 151.6, 568.4,
    390.1, 470.2, 280.5, 410.3, 350.8, 640.5,
    260.2, 720.6, 120.4
]) + np.random.normal(0, 20, 15)  # small noise

# Compression ratios (%)
compression = np.array([
    85, 85, 85, 85, 0, 100,
    70, 75, 80, 60, 65, 85,
    55, 90, 50
])

# Plot setup
fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot
sc = ax.scatter(
    file_sizes_kb,
    processing_times,
    compression,
    c=compression,
    cmap='plasma',
    s=90,
    edgecolors='k',
    alpha=0.85
)

# Labels and title
ax.set_xlabel('Saved Size (KB)')
ax.set_ylabel('Processing Time (ms)')
ax.set_zlabel('Compression (%)')
ax.set_title('3D Performance Visualization: OraLake Upload Analysis')

# Color bar for compression intensity
cbar = plt.colorbar(sc, pad=0.1)
cbar.set_label('Compression (%)')

# Annotate key points (for larger images)
for i in range(len(image_ids)):
    if file_sizes_kb[i] > 800 or compression[i] in [0, 100]:
        ax.text(file_sizes_kb[i], processing_times[i], compression[i] + 2,
                f"#{image_ids[i]}", fontsize=8, color='black')

plt.tight_layout()
plt.show()

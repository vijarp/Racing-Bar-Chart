import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import FuncFormatter
from PIL import Image
import io
# Load your data
df = pd.read_csv('car_sales_2000_2024.csv')

# Sort data by year and sales
df = df.sort_values(['Year', 'Sales'], ascending=[True, False])

# Get unique years and cars
years = sorted(df['Year'].unique())
cars = df['Car'].unique()

# Function to interpolate data between years
def interpolate_data(start_year, end_year, steps):
    start_data = df[df['Year'] == start_year].set_index('Car')['Sales']
    end_data = df[df['Year'] == end_year].set_index('Car')['Sales']
    
    # Combine all cars from both years
    all_cars = list(set(start_data.index) | set(end_data.index))
    
    interpolated = []
    for i in range(steps):
        frame = pd.Series(index=all_cars, dtype=float)
        for car in all_cars:
            start_sales = start_data.get(car, 0)
            end_sales = end_data.get(car, 0)
            frame[car] = start_sales + (end_sales - start_sales) * i / steps
        interpolated.append(frame.sort_values(ascending=False))
    return interpolated

# Prepare interpolated data
frames_per_year = 10
all_frames = []
for i in range(len(years) - 1):
    all_frames.extend(interpolate_data(years[i], years[i+1], frames_per_year))

# Function to create a single frame
def create_frame(frame_data, frame_index, total_frames, year_start, year_end):
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Create horizontal bars
    bars = ax.barh(frame_data.index, frame_data.values, color='skyblue')
    
    # Customize the plot
    current_year = int(year_start + (year_end - year_start) * (frame_index / total_frames))
    ax.set_title(f'Car Sales Ranking - Year {current_year}', fontsize=16)
    ax.set_xlabel('Sales', fontsize=12)
    ax.set_ylabel('Car Model', fontsize=12)
    ax.set_xlim(0, df['Sales'].max() * 1.1)
    
    # Add sales labels to the end of each bar
    for i, (sales, car) in enumerate(zip(frame_data.values, frame_data.index)):
        ax.text(sales, i, f'{sales:,.0f}', va='center', ha='left', fontsize=10)
    
    # Color the top 3 bars differently
    colors = ['gold', 'silver', 'chocolate'] + ['skyblue'] * (len(frame_data) - 3)
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    plt.tight_layout()
    
    # Convert plot to PIL Image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img = Image.open(buf)
    plt.close(fig)
    return img

# Create and save the GIF
images = []
total_frames = len(all_frames)
for i, frame_data in enumerate(all_frames):
    img = create_frame(frame_data, i, total_frames, years[0], years[-1])
    images.append(img)

# Save as GIF
images[0].save('car_sales_ranking_smooth.gif',
               save_all=True,
               append_images=images[1:],
               duration=100,  # Duration per frame in milliseconds
               loop=0)  # 0 means loop indefinitely

print("Animation saved as 'car_sales_ranking_smooth.gif'")

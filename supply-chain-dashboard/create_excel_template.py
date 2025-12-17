"""
Create a sample Excel template for the demand analysis script
Run this to generate sample_data_template.xlsx with the correct format
"""

import pandas as pd
from datetime import datetime

# Create sample data for template
sample_dates = pd.date_range(start='2012-10-01', end='2012-10-10', freq='D')

sample_df = pd.DataFrame({
    'Date': sample_dates,
    'Idly': [120, 135, 142, 128, 151, 160, 155, 140, 138, 145],
    'Dosa': [95, 110, 105, 98, 125, 130, 128, 115, 108, 120],
    'Sambar': [85, 92, 88, 90, 98, 102, 100, 95, 93, 97],
    'Occupancy': [140, 155, 148, 142, 165, 170, 168, 158, 152, 160]
})

# Save to Excel
output_path = 'd:/Jaya Files/Higher Studies/IIM Udaipur/Term 3/Supply Chain Analytics/Code/sample_data_template.xlsx'
sample_df.to_excel(output_path, index=False, sheet_name='Demand Data')

print(f"[OK] Excel template created: {output_path}")
print(f"\nTemplate contains {len(sample_df)} sample rows with columns:")
print(f"  - Date (datetime)")
print(f"  - Idly (integer)")
print(f"  - Dosa (integer)")
print(f"  - Sambar (integer)")
print(f"  - Occupancy (integer)")
print("\nReplace the sample data with your actual data and save.")


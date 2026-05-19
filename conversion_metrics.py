import pandas as pd
import os
import matplotlib.pyplot as plt

# Step 1: Load Data
file_path = "input/sample.csv"
data = pd.read_csv(file_path)

# Step 2: Filter the Data for Conversion Criteria
# User has at least 1 transaction that satisfies the following:
converted_users = data[
    (data['IS_FRAUD'] == False) &  # Non-fraudulent transactions
    (data['KYC'] != 'FAILED') &    # KYC is not failed
    (data['AMOUNT'] > 0) &         # Amount is greater than 0
    (data['TYPE'] != 'TOPUP')      # Exclude top-up-only transactions
]['USER_ID'].nunique()  # Count unique users meeting the criteria

# Step 3: Calculate Total Users and Conversion Rate
total_users = data['USER_ID'].nunique()
conversion_rate = (converted_users / total_users) * 100

# Print the results
print(f"Total Users: {total_users}")
print(f"Converted Users: {converted_users}")
print(f"Conversion Rate: {conversion_rate:.2f}%")

# Step 4: Create Output Folder
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Step 5: Save Results to a CSV File
output_csv_path = os.path.join(output_folder, "conversion_metrics.csv")
conversion_metrics = pd.DataFrame({
    'Metric': ['Total Users', 'Converted Users', 'Conversion Rate (%)'],
    'Value': [total_users, converted_users, conversion_rate]
})
conversion_metrics.to_csv(output_csv_path, index=False)
print(f"Saved conversion metrics to: {output_csv_path}")

# Step 6: Visualize Conversion Rate
# Create a pie chart to visualize converted vs non-converted users
non_converted_users = total_users - converted_users
labels = ['Converted Users', 'Non-Converted Users']
sizes = [converted_users, non_converted_users]
colors = ['#4CAF50', '#FF5733']
explode = (0.1, 0)  # Highlight the converted users slice

fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
ax.set_title('User Conversion Rate')

# Save the plot to the output folder
output_graph_path = os.path.join(output_folder, "conversion_metrics.png")
plt.savefig(output_graph_path)
print(f"Saved conversion rate pie chart to: {output_graph_path}")
plt

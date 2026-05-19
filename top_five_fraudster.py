import pandas as pd
import os
import matplotlib.pyplot as plt

# Step 1: Load Data
# Read the transaction data CSV file
file_path = "input/sample.csv"
data = pd.read_csv(file_path)

# Read the currency conversion rates CSV file
conversion_file = "input/currency.csv"
conversion_rates = pd.read_csv(conversion_file)

# Merge transaction data with currency conversion rates
data = data.merge(conversion_rates, how='left', left_on='CURRENCY', right_on='CURRENCY')

# Add Converted Amount in GBP
data['AMOUNT_GBP'] = data['AMOUNT'] * data['CURRENCY_RATE']

# Step 2: Filter Fraudulent Transactions
# Explicitly create a copy of the filtered DataFrame to avoid warnings
fraud_data = data[data['IS_FRAUD'] == True].copy()

# Step 3: Aggregate Fraud Metrics by User
fraudster_stats = fraud_data.groupby('USER_ID').agg(
    total_fraud_events=('IS_FRAUD', 'count'),  # Total fraud events
    total_fraud_volume=('AMOUNT_GBP', 'sum'),  # Total fraud volume in GBP
    kyc_passed_fraud_events=('KYC', lambda x: (x != 'FAILED').sum()),  # Fraud events with KYC PASSED
    unique_countries=('COUNTRY', 'nunique'),  # Number of unique countries (cross-geo behavior)
    unique_channels=('TYPE', 'nunique')  # Number of unique transaction types (multi-channel behavior)
).reset_index()

# Step 4: Create a Composite Score
# Composite score based on the weighted sum of metrics
fraudster_stats['composite_score'] = (
    fraudster_stats['total_fraud_events'] * 0.4 +  # Weight for persistence
    fraudster_stats['total_fraud_volume'] * 0.3 +  # Weight for high-value fraud
    fraudster_stats['kyc_passed_fraud_events'] * 0.2 +  # Weight for KYC infiltration
    fraudster_stats['unique_countries'] * 0.1 +  # Weight for cross-geo behavior
    fraudster_stats['unique_channels'] * 0.1  # Weight for multi-channel behavior
)

# Step 5: Sort by Composite Score
top_fraudsters = fraudster_stats.sort_values('composite_score', ascending=False).head(5)

# Step 6: Create Output Folder
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Step 7: Save Results to CSV
output_csv_path = os.path.join(output_folder, "top_five_fraudsters.csv")
top_fraudsters.to_csv(output_csv_path, index=False)
print(f"Saved top 5 fraudsters to: {output_csv_path}")

# Step 8: Print Results to Console
print("\nTop 5 Fraudsters:")
print(top_fraudsters)

# Step 9: Visualize Composite Scores of Top 5 Fraudsters
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(top_fraudsters['USER_ID'], top_fraudsters['composite_score'], color='blue', alpha=0.7)
ax.set_title('Top 5 Fraudsters by Composite Score')
ax.set_xlabel('User ID')
ax.set_ylabel('Composite Score')
ax.set_xticks(range(len(top_fraudsters['USER_ID'])))
ax.set_xticklabels(top_fraudsters['USER_ID'], rotation=45, ha='right')

# Save the graph to the output folder
output_graph_path = os.path.join(output_folder, "top_five_fraudsters.png")
plt.tight_layout()
plt.savefig(output_graph_path)
print(f"Saved fraudster graph to: {output_graph_path}")
plt.show()

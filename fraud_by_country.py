import pandas as pd
import matplotlib.pyplot as plt
import os

# Step 1: Load Data
# Read the transaction data CSV file
file_path = "input/sample.csv"
data = pd.read_csv(file_path)

# Read the currency conversion rates CSV file
conversion_file = "input/currency.csv"
conversion_rates = pd.read_csv(conversion_file)

# Step 2: Merge Transaction Data with Conversion Rates
# Merge the transaction data with the currency conversion rates
data = data.merge(conversion_rates, how='left', left_on='CURRENCY', right_on='CURRENCY')

# Step 3: Convert Transaction Amounts to GBP
# Calculate the transaction amounts in GBP using the conversion rates
data['AMOUNT_GBP'] = data['AMOUNT'] * data['CURRENCY_RATE']

# Step 4: Pre-filter Fraudulent Transactions
# Filter fraudulent transactions to improve efficiency
fraud_data = data[data['IS_FRAUD'] == True]

# Step 5: Group Transactions by User Geography (`COUNTRY`)
fraud_stats = data.groupby('COUNTRY').agg(
    total_transactions=('IS_FRAUD', 'count'),  # Total transactions
    fraud_transactions=('IS_FRAUD', lambda x: (x == True).sum()),  # Count fraudulent transactions
    fraud_volume_gbp=('AMOUNT_GBP', 'sum')  # Total fraudulent amount in GBP
).reset_index()

# Step 6: Compute Fraud Metrics
# Calculate fraud rate as the proportion of fraudulent transactions
fraud_stats['fraud_rate'] = fraud_stats['fraud_transactions'] / fraud_stats['total_transactions']

# Step 7: Calculate Composite Score
# Adjust weights as needed (e.g., give equal importance to fraud volume and fraud rate)
weight_volume = 0.5
weight_rate = 0.5
fraud_stats['composite_score'] = (
    fraud_stats['fraud_volume_gbp'] * weight_volume +
    fraud_stats['fraud_rate'] * weight_rate
)

# Step 8: Order by Composite Score and print
# Sort the results by composite score in descending order
fraud_stats_sorted = fraud_stats.sort_values('composite_score', ascending=False)
print("Enhanced Fraud Analysis by Currency and Country: (Top 10 Rows Only)")
print(fraud_stats_sorted.head(10))

# Step 9: Create Output Folder
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Step 10: Save Results to CSV
output_csv_path = os.path.join(output_folder, "fraud_by_country.csv")
fraud_stats_sorted.to_csv(output_csv_path, index=False)
print(f"Saved fraud statistics to: {output_csv_path}")

# Step 11: Visualize Top 10 Countries
top_10 = fraud_stats_sorted.head(10)
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart for fraud volume
ax1.bar(top_10['COUNTRY'], top_10['fraud_volume_gbp'], color='b', alpha=0.6, label='Fraud Volume (GBP)')
ax1.set_xlabel('Country')
ax1.set_ylabel('Fraud Volume (GBP)', color='b')
ax1.tick_params(axis='y', labelcolor='b')
ax1.set_title('Top 10 Countries by Fraud Volume and Rate')

# Line chart for fraud rate
ax2 = ax1.twinx()
ax2.plot(top_10['COUNTRY'], top_10['fraud_rate'], color='r', marker='o', label='Fraud Rate')
ax2.set_ylabel('Fraud Rate', color='r')
ax2.tick_params(axis='y', labelcolor='r')

# Add legend and save the plot
fig.tight_layout()
output_graph_path = os.path.join(output_folder, "fraud_by_country.png")
plt.savefig(output_graph_path)
print(f"Saved fraud statistics graph to: {output_graph_path}")
plt.show()

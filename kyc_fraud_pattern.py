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

# Step 2: Merge Transaction Data with Conversion Rates
# Merge the transaction data with the currency conversion rates
data = data.merge(conversion_rates, how='left', left_on='CURRENCY', right_on='CURRENCY')

# Step 3: Filter Transactions (KYC Passed + Fraud)
# Explicitly create a copy of the filtered DataFrame
filtered_data = data[
    (data['KYC'] != 'FAILED') &  # KYC has passed
    (data['IS_FRAUD'] == True)   # Fraudulent transactions
].copy()

# Step 4: Add Converted Amount in GBP
# This modification will now safely work on the copied DataFrame
filtered_data['AMOUNT_GBP'] = filtered_data['AMOUNT'] * filtered_data['CURRENCY_RATE']

# Step 5: Categorize Transactions as Domestic or International
# This modification will also safely work on the copied DataFrame
filtered_data['TRANSACTION_TYPE'] = filtered_data.apply(
    lambda row: 'Domestic' if row['COUNTRY'] == row['HOME_COUNTRY'] else 'International', axis=1
)

# Step 6: Group Transactions by Country and Transaction Type (Domestic/International)
fraud_stats = filtered_data.groupby(['COUNTRY', 'TRANSACTION_TYPE']).agg(
    total_transactions=('IS_FRAUD', 'count'),  # Total transactions
    fraud_transactions=('IS_FRAUD', lambda x: (x == True).sum()),  # Count fraudulent transactions
    fraud_volume=('AMOUNT_GBP', 'sum'),  # Total fraudulent amount in GBP
    card_transactions=('TYPE', lambda x: (x == 'CARD_PAYMENT').sum()),  # Count of card-heavy transactions
    small_transactions=('AMOUNT_GBP', lambda x: (x < 10).sum()),  # Count of small fraudulent transactions (< 10 GBP)
    high_value_transactions=('AMOUNT_GBP', lambda x: (x > 1000).sum()),  # Count of high-value fraudulent transactions (> 1000 GBP)
    avg_transaction_amount=('AMOUNT_GBP', 'mean')  # Average fraudulent transaction amount
).reset_index()

# Compute Fraud Rate
fraud_stats['fraud_rate'] = fraud_stats['fraud_transactions'] / fraud_stats['total_transactions']

# Step 7: Sort by Fraud Volume and Rate
fraud_stats_sorted = fraud_stats.sort_values(['fraud_volume', 'fraud_rate'], ascending=[False, False])

print("\nFraud Statistics (Top 10 Rows):")
print(fraud_stats_sorted.head(10))

# Step 8: Create Output Folder
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Step 9: Save Results to CSV
output_csv_path = os.path.join(output_folder, "kyc_fraud_pattern.csv")
fraud_stats_sorted.to_csv(output_csv_path, index=False)
print(f"Saved fraud analysis to: {output_csv_path}")

# Step 10: Visualize Fraud Statistics
# Plot fraud volume and fraud rate for the top 10 rows
top_10 = fraud_stats_sorted.head(10)
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart for fraud volume
ax1.bar(top_10['COUNTRY'] + " (" + top_10['TRANSACTION_TYPE'] + ")", 
        top_10['fraud_volume'], color='b', alpha=0.6, label='Fraud Volume (GBP)')
ax1.set_xlabel('Country (Transaction Type)')
ax1.set_ylabel('Fraud Volume (GBP)', color='b')
ax1.tick_params(axis='y', labelcolor='b')
ax1.set_title('Top 10 Countries by Fraud Volume and Rate')

# Line chart for fraud rate
ax2 = ax1.twinx()
ax2.plot(top_10['COUNTRY'] + " (" + top_10['TRANSACTION_TYPE'] + ")", 
         top_10['fraud_rate'], color='r', marker='o', label='Fraud Rate')
ax2.set_ylabel('Fraud Rate', color='r')
ax2.tick_params(axis='y', labelcolor='r')

# Add legend and save the plot
fig.tight_layout()
output_graph_path = os.path.join(output_folder, "kyc_fraud_pattern.png")
plt.savefig(output_graph_path)
print(f"Saved fraud analysis graph to: {output_graph_path}")
plt.show()

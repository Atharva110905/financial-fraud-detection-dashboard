"""
Synthetic Financial Transaction Fraud Dataset Generator
---------------------------------------------------------
Generates ~100,000 realistic transaction records with engineered fraud
patterns (not pure random noise) so that EDA + ML actually finds signal.

Fraud patterns simulated:
1. Card testing        - many tiny rapid-fire transactions on a new card
2. Account takeover     - sudden burst of high-value txns after dormancy
3. Geo-velocity mismatch - transactions in distant locations within a short time
4. Odd-hour high-value   - large transactions at unusual hours (12am-4am)
5. New-device + new-merchant combo - first-time device used at unfamiliar merchant
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RNG = np.random.default_rng(42)
N_CUSTOMERS = 8000
N_TRANSACTIONS = 100_000
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

MERCHANT_CATEGORIES = [
    "Grocery", "Electronics", "Fashion & Apparel", "Travel", "Dining",
    "Fuel & Gas", "Healthcare", "Entertainment", "Utilities", "Online Retail",
    "Jewelry", "Crypto Exchange", "Gambling", "Money Transfer", "Subscriptions"
]

HIGH_RISK_CATEGORIES = ["Crypto Exchange", "Gambling", "Money Transfer", "Jewelry"]

CITIES = [
    ("Mumbai", 19.0760, 72.8777), ("Delhi", 28.7041, 77.1025),
    ("Bengaluru", 12.9716, 77.5946), ("Hyderabad", 17.3850, 78.4867),
    ("Chennai", 13.0827, 80.2707), ("Kolkata", 22.5726, 88.3639),
    ("Pune", 18.5204, 73.8567), ("Ahmedabad", 23.0225, 72.5714),
    ("Jaipur", 26.9124, 75.7873), ("Lucknow", 26.8467, 80.9462),
    ("Surat", 21.1702, 72.8311), ("Nagpur", 21.1458, 79.0882),
    ("Indore", 22.7196, 75.8577), ("Kochi", 9.9312, 76.2673),
    ("Chandigarh", 30.7333, 76.7794),
]

CHANNELS = ["POS", "Online", "ATM", "Mobile App", "Recurring"]
DEVICE_TYPES = ["Mobile", "Desktop", "POS Terminal", "ATM Machine", "Tablet"]
CARD_TYPES = ["Visa", "Mastercard", "RuPay", "Amex"]

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

# ---------------------------------------------------------------
# Step 1: Generate customer profiles
# ---------------------------------------------------------------
print("Generating customer profiles...")
customer_ids = [f"CUST{str(i).zfill(6)}" for i in range(N_CUSTOMERS)]
home_city_idx = RNG.integers(0, len(CITIES), N_CUSTOMERS)
customer_profiles = pd.DataFrame({
    "customer_id": customer_ids,
    "home_city": [CITIES[i][0] for i in home_city_idx],
    "home_lat": [CITIES[i][1] for i in home_city_idx],
    "home_lon": [CITIES[i][2] for i in home_city_idx],
    "card_type": RNG.choice(CARD_TYPES, N_CUSTOMERS, p=[0.4, 0.35, 0.2, 0.05]),
    "avg_monthly_spend": RNG.gamma(shape=3.0, scale=8000, size=N_CUSTOMERS).round(2),
    "account_age_days": RNG.integers(30, 3650, N_CUSTOMERS),
    "risk_segment": RNG.choice(["Low", "Medium", "High"], N_CUSTOMERS, p=[0.7, 0.22, 0.08]),
})

# ---------------------------------------------------------------
# Step 2: Assign number of transactions per customer (Poisson-ish)
# ---------------------------------------------------------------
base_txn_counts = RNG.poisson(lam=N_TRANSACTIONS / N_CUSTOMERS, size=N_CUSTOMERS)
base_txn_counts = np.clip(base_txn_counts, 1, None)
total = base_txn_counts.sum()
# scale to hit target total
scale_factor = N_TRANSACTIONS / total
txn_counts = np.round(base_txn_counts * scale_factor).astype(int)
txn_counts = np.clip(txn_counts, 1, None)

rows = []
txn_seq = 0

print("Generating transactions per customer...")
for idx, cust in customer_profiles.iterrows():
    n_txn = txn_counts[idx]
    cust_id = cust["customer_id"]
    home_lat, home_lon = cust["home_lat"], cust["home_lon"]
    avg_spend = max(cust["avg_monthly_spend"] / 10, 200)
    risk_seg = cust["risk_segment"]

    # Random timestamps across the year, sorted
    days_range = (END_DATE - START_DATE).days
    txn_days = RNG.integers(0, days_range, n_txn)
    txn_seconds = RNG.integers(0, 86400, n_txn)
    timestamps = sorted([START_DATE + timedelta(days=int(d), seconds=int(s))
                          for d, s in zip(txn_days, txn_seconds)])

    last_device_new = RNG.random() < 0.1

    for i, ts in enumerate(timestamps):
        txn_seq += 1
        # base "normal" transaction
        category = RNG.choice(MERCHANT_CATEGORIES)
        channel = RNG.choice(CHANNELS, p=[0.35, 0.30, 0.10, 0.20, 0.05])
        amount = max(50, RNG.gamma(shape=2.0, scale=avg_spend / 2))

        # location: mostly home city, occasionally a nearby/far city
        if RNG.random() < 0.85:
            city, lat, lon = cust["home_city"], home_lat, home_lon
        else:
            city_idx = RNG.integers(0, len(CITIES))
            city, lat, lon = CITIES[city_idx]

        device = RNG.choice(DEVICE_TYPES)
        is_new_device = RNG.random() < 0.05

        rows.append({
            "transaction_id": f"TXN{str(txn_seq).zfill(7)}",
            "customer_id": cust_id,
            "timestamp": ts,
            "amount": round(amount, 2),
            "merchant_category": category,
            "channel": channel,
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "device_type": device,
            "is_new_device": is_new_device,
            "card_type": cust["card_type"],
            "customer_risk_segment": risk_seg,
            "account_age_days": cust["account_age_days"],
            "is_fraud": 0,
            "fraud_pattern": "None",
        })

df = pd.DataFrame(rows)
print(f"Base transactions generated: {len(df):,}")

# ---------------------------------------------------------------
# Step 3: Inject fraud patterns (~1.5% of total, realistic for fraud data)
# ---------------------------------------------------------------
print("Injecting fraud patterns...")
df = df.sort_values(["customer_id", "timestamp"]).reset_index(drop=True)

fraud_target_rate = 0.018  # ~1.8% fraud, realistic imbalance
n_fraud_target = int(len(df) * fraud_target_rate)

# Helper to pick random row indices not already marked as fraud
def get_candidate_indices(n, exclude_mask):
    available = df.index[~exclude_mask]
    return RNG.choice(available, size=min(n, len(available)), replace=False)

fraud_mask = pd.Series(False, index=df.index)

# --- Pattern 1: Card testing - rapid tiny transactions burst ---
n_pattern1_customers = max(1, n_fraud_target // 5 // 4)  # avg ~4 txns per burst
chosen_customers = RNG.choice(customer_profiles["customer_id"], n_pattern1_customers, replace=False)
for cust_id in chosen_customers:
    cust_rows = df[df["customer_id"] == cust_id]
    if len(cust_rows) < 2:
        continue
    start_idx = RNG.choice(cust_rows.index[:-1])
    base_time = df.loc[start_idx, "timestamp"]
    burst_size = RNG.integers(3, 7)
    for b in range(burst_size):
        idx = RNG.choice(df.index[~fraud_mask])
        df.loc[idx, "customer_id"] = cust_id
        df.loc[idx, "timestamp"] = base_time + timedelta(minutes=int(RNG.integers(1, 15)) * b)
        df.loc[idx, "amount"] = round(RNG.uniform(10, 150), 2)
        df.loc[idx, "merchant_category"] = "Online Retail"
        df.loc[idx, "channel"] = "Online"
        df.loc[idx, "is_new_device"] = True
        df.loc[idx, "is_fraud"] = 1
        df.loc[idx, "fraud_pattern"] = "Card Testing"
        fraud_mask.loc[idx] = True

# --- Pattern 2: Account takeover - high value burst after dormancy ---
n_pattern2 = n_fraud_target // 5
candidate_idx = get_candidate_indices(n_pattern2, fraud_mask)
for idx in candidate_idx:
    cust_id = df.loc[idx, "customer_id"]
    cust_avg = customer_profiles.loc[customer_profiles["customer_id"] == cust_id, "avg_monthly_spend"].values[0]
    df.loc[idx, "amount"] = round(max(cust_avg * RNG.uniform(2.5, 6), 5000), 2)
    df.loc[idx, "merchant_category"] = RNG.choice(["Electronics", "Jewelry", "Crypto Exchange", "Money Transfer"])
    df.loc[idx, "channel"] = "Online"
    df.loc[idx, "is_new_device"] = True
    df.loc[idx, "timestamp"] = df.loc[idx, "timestamp"].replace(
        hour=int(RNG.choice([0, 1, 2, 3, 4, 23])), minute=int(RNG.integers(0, 60))
    )
    df.loc[idx, "is_fraud"] = 1
    df.loc[idx, "fraud_pattern"] = "Account Takeover"
    fraud_mask.loc[idx] = True

# --- Pattern 3: Geo-velocity mismatch - far-away city, short time gap ---
n_pattern3 = n_fraud_target // 5
candidate_idx = get_candidate_indices(n_pattern3, fraud_mask)
for idx in candidate_idx:
    cust_id = df.loc[idx, "customer_id"]
    home_lat = customer_profiles.loc[customer_profiles["customer_id"] == cust_id, "home_lat"].values[0]
    home_lon = customer_profiles.loc[customer_profiles["customer_id"] == cust_id, "home_lon"].values[0]
    # pick a far city
    distances = [haversine_km(home_lat, home_lon, c[1], c[2]) for c in CITIES]
    far_city_idx = int(np.argmax(distances))
    city, lat, lon = CITIES[far_city_idx]
    df.loc[idx, "city"] = city
    df.loc[idx, "latitude"] = lat
    df.loc[idx, "longitude"] = lon
    df.loc[idx, "amount"] = round(RNG.uniform(2000, 15000), 2)
    df.loc[idx, "channel"] = RNG.choice(["POS", "ATM"])
    df.loc[idx, "is_fraud"] = 1
    df.loc[idx, "fraud_pattern"] = "Geo-Velocity Mismatch"
    fraud_mask.loc[idx] = True

# --- Pattern 4: Odd-hour high-value transactions ---
n_pattern4 = n_fraud_target // 5
candidate_idx = get_candidate_indices(n_pattern4, fraud_mask)
for idx in candidate_idx:
    odd_hour = int(RNG.choice([0, 1, 2, 3, 4]))
    df.loc[idx, "timestamp"] = df.loc[idx, "timestamp"].replace(hour=odd_hour, minute=int(RNG.integers(0, 60)))
    df.loc[idx, "amount"] = round(RNG.uniform(5000, 25000), 2)
    df.loc[idx, "merchant_category"] = RNG.choice(HIGH_RISK_CATEGORIES)
    df.loc[idx, "channel"] = "Online"
    df.loc[idx, "is_fraud"] = 1
    df.loc[idx, "fraud_pattern"] = "Odd-Hour High-Value"
    fraud_mask.loc[idx] = True

# --- Pattern 5: New device + new/high-risk merchant combo ---
n_pattern5 = n_fraud_target - fraud_mask.sum()
candidate_idx = get_candidate_indices(max(n_pattern5, 0), fraud_mask)
for idx in candidate_idx:
    df.loc[idx, "is_new_device"] = True
    df.loc[idx, "device_type"] = RNG.choice(["Mobile", "Desktop"])
    df.loc[idx, "merchant_category"] = RNG.choice(HIGH_RISK_CATEGORIES)
    df.loc[idx, "amount"] = round(RNG.uniform(1500, 9000), 2)
    df.loc[idx, "channel"] = "Online"
    df.loc[idx, "is_fraud"] = 1
    df.loc[idx, "fraud_pattern"] = "New Device + High-Risk Merchant"
    fraud_mask.loc[idx] = True

print(f"Total fraud injected: {fraud_mask.sum():,} ({fraud_mask.sum()/len(df)*100:.2f}%)")

# ---------------------------------------------------------------
# Step 4: Feature engineering helpful for both EDA + ML
# ---------------------------------------------------------------
print("Engineering derived features...")
df = df.sort_values(["customer_id", "timestamp"]).reset_index(drop=True)
df["hour_of_day"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.day_name()
df["is_weekend"] = df["timestamp"].dt.dayofweek >= 5
df["month"] = df["timestamp"].dt.month_name()

# time since previous transaction for same customer (minutes)
df["prev_timestamp"] = df.groupby("customer_id")["timestamp"].shift(1)
df["minutes_since_last_txn"] = (df["timestamp"] - df["prev_timestamp"]).dt.total_seconds() / 60
df["minutes_since_last_txn"] = df["minutes_since_last_txn"].fillna(df["minutes_since_last_txn"].median())

# distance from home city for this txn
df = df.merge(customer_profiles[["customer_id", "home_lat", "home_lon", "avg_monthly_spend"]],
               on="customer_id", how="left")
df["distance_from_home_km"] = haversine_km(df["home_lat"], df["home_lon"], df["latitude"], df["longitude"]).round(1)

# amount relative to customer's average spend
df["amount_to_avg_spend_ratio"] = (df["amount"] / (df["avg_monthly_spend"] / 10 + 1)).round(2)

df = df.drop(columns=["prev_timestamp", "home_lat", "home_lon"])

# ---------------------------------------------------------------
# Step 5: Finalize and save
# ---------------------------------------------------------------
df["transaction_id"] = [f"TXN{str(i).zfill(7)}" for i in range(1, len(df) + 1)]
df = df.sort_values("timestamp").reset_index(drop=True)

col_order = [
    "transaction_id", "customer_id", "timestamp", "amount", "merchant_category",
    "channel", "city", "latitude", "longitude", "distance_from_home_km",
    "device_type", "is_new_device", "card_type", "customer_risk_segment",
    "account_age_days", "hour_of_day", "day_of_week", "is_weekend", "month",
    "minutes_since_last_txn", "avg_monthly_spend", "amount_to_avg_spend_ratio",
    "is_fraud", "fraud_pattern"
]
df = df[col_order]

output_path = "/home/claude/fraud_project/fraud_transactions.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved dataset to {output_path}")
print(f"Shape: {df.shape}")
print(f"Fraud rate: {df['is_fraud'].mean()*100:.2f}%")
print(f"\nFraud pattern breakdown:")
print(df[df["is_fraud"] == 1]["fraud_pattern"].value_counts())

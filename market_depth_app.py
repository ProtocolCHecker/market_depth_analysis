# import streamlit as st
# import json
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import os
# import requests
# import time
# from typing import Dict, Any, Optional, List, Tuple
# from curve_liquidity_monitoring import MarketDepthFetcher as CurveMarketDepthFetcher

# # Set page config
# st.set_page_config(
#     page_title="DeFi Market Depth Analyzer",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS for better styling
# st.markdown("""
# <style>
#     .main .block-container {
#         padding-top: 2rem;
#         padding-bottom: 2rem;
#     }
#     .stButton>button {
#         background-color: #4CAF50;
#         color: white;
#         border-radius: 4px;
#         border: none;
#         padding: 0.5rem 1rem;
#     }
#     .stButton>button:hover {
#         background-color: #45a049;
#     }
#     .stSelectbox>div>div>select {
#         padding: 0.5rem;
#     }
#     .stSlider>div>div>div>div {
#         background-color: #4CAF50;
#     }
#     .metric-card {
#         background-color: #f0f2f6;
#         border-radius: 8px;
#         padding: 1rem;
#         margin-bottom: 1rem;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     }
#     .metric-title {
#         font-size: 1rem;
#         font-weight: 600;
#         color: #555;
#         margin-bottom: 0.5rem;
#     }
#     .metric-value {
#         font-size: 1.5rem;
#         font-weight: 700;
#         color: #333;
#     }
#     .tab-content {
#         padding: 1rem 0;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Initialize classes from the provided scripts
# class DuneClient:
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#         self.base_url = "https://api.dune.com/api/v1"
#         self.headers = {
#             "X-Dune-API-Key": api_key,
#             "Content-Type": "application/json"
#         }
    
#     def execute_query_by_id(self, query_id: int, parameters: Dict = None, performance: str = "medium") -> Optional[str]:
#         """Execute an existing query by ID on Dune Analytics"""
#         url = f"{self.base_url}/query/{query_id}/execute"
        
#         payload = {"performance": performance}
#         if parameters:
#             payload["query_parameters"] = parameters
        
#         try:
#             response = requests.post(url, headers=self.headers, json=payload)
#             response.raise_for_status()
            
#             result = response.json()
#             execution_id = result.get("execution_id")
            
#             if execution_id:
#                 st.session_state['dune_message'] = f"Query execution submitted successfully. Execution ID: {execution_id}"
#                 return execution_id
#             else:
#                 st.session_state['dune_message'] = "Failed to get execution ID from response"
#                 return None
                
#         except requests.exceptions.RequestException as e:
#             st.session_state['dune_message'] = f"Error executing query: {e}"
#             return None
    
#     def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
#         """Get the status of a query execution"""
#         url = f"{self.base_url}/execution/{execution_id}/status"
        
#         try:
#             response = requests.get(url, headers=self.headers)
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             st.session_state['dune_message'] = f"Error getting execution status: {e}"
#             return {"state": "FAILED", "error": str(e)}
    
#     def get_execution_results(self, execution_id: str) -> Optional[Dict[str, Any]]:
#         """Get the results of a completed query execution"""
#         url = f"{self.base_url}/execution/{execution_id}/results"
        
#         try:
#             response = requests.get(url, headers=self.headers)
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             st.session_state['dune_message'] = f"Error getting execution results: {e}"
#             return None
    
#     def wait_for_completion(self, execution_id: str, max_wait_time: int = 300, 
#                           poll_interval: int = 5) -> Optional[Dict[str, Any]]:
#         """Wait for query execution to complete and return results"""
#         start_time = time.time()
#         progress_bar = st.progress(0)
#         status_text = st.empty()
        
#         while time.time() - start_time < max_wait_time:
#             elapsed = time.time() - start_time
#             progress = min(elapsed / max_wait_time, 1.0)
#             progress_bar.progress(progress)
            
#             status = self.get_execution_status(execution_id)
#             state = status.get("state", "UNKNOWN")
            
#             status_text.text(f"Query status: {state} ({(elapsed/60):.1f} minutes elapsed)")
            
#             if state == "QUERY_STATE_COMPLETED":
#                 progress_bar.progress(1.0)
#                 status_text.text("Query completed successfully!")
#                 return self.get_execution_results(execution_id)
#             elif state == "QUERY_STATE_FAILED":
#                 progress_bar.progress(1.0)
#                 status_text.text(f"Query failed: {status.get('error', 'Unknown error')}")
#                 return None
#             elif state in ["QUERY_STATE_EXECUTING", "QUERY_STATE_PENDING"]:
#                 time.sleep(poll_interval)
#             else:
#                 time.sleep(poll_interval)
        
#         progress_bar.progress(1.0)
#         status_text.text(f"Query timed out after {max_wait_time} seconds")
#         return None

#     def create_and_execute_query(self, query_sql: str, name: str = "API Query") -> Optional[str]:
#         """Alternative approach: Try to create and execute in one go"""
#         try:
#             url = f"{self.base_url}/execution"
#             payload = {
#                 "query_sql": query_sql,
#                 "performance": "medium"
#             }
            
#             response = requests.post(url, headers=self.headers, json=payload)
#             if response.status_code == 200:
#                 result = response.json()
#                 execution_id = result.get("execution_id")
#                 if execution_id:
#                     st.session_state['dune_message'] = f"Query submitted via direct execution. Execution ID: {execution_id}"
#                     return execution_id
#         except:
#             pass
        
#         try:
#             url = f"{self.base_url}/query"
#             payload = {
#                 "query_sql": query_sql,
#                 "name": name,
#                 "is_private": False
#             }
            
#             response = requests.post(url, headers=self.headers, json=payload)
#             if response.status_code == 200:
#                 result = response.json()
#                 query_id = result.get("query_id")
#                 if query_id:
#                     return self.execute_query_by_id(query_id)
#         except Exception as e:
#             st.session_state['dune_message'] = f"Query creation failed: {e}"
        
#         return None

# class MarketDepthCalculator:
#     def __init__(self, token0_symbol, token1_symbol, token0_decimals, token1_decimals, 
#                  token0_price_usd, token1_price_usd, tick_spacing=60):
#         self.token0_symbol = token0_symbol
#         self.token1_symbol = token1_symbol
#         self.token0_decimals = token0_decimals
#         self.token1_decimals = token1_decimals
#         self.token0_price_usd = token0_price_usd
#         self.token1_price_usd = token1_price_usd
#         self.tick_spacing = tick_spacing

#     def calculate_token_amounts(self, liquidity, sqrt_price_lower, sqrt_price_upper, sqrt_price_current):
#         """Calculate token amounts for a liquidity position"""
#         liquidity = float(liquidity)
        
#         if sqrt_price_current <= sqrt_price_lower:
#             amount0 = liquidity * (1/sqrt_price_lower - 1/sqrt_price_upper)
#             amount1 = 0
#         elif sqrt_price_current >= sqrt_price_upper:
#             amount0 = 0
#             amount1 = liquidity * (sqrt_price_upper - sqrt_price_lower)
#         else:
#             amount0 = liquidity * (1/sqrt_price_current - 1/sqrt_price_upper)
#             amount1 = liquidity * (sqrt_price_current - sqrt_price_lower)
        
#         return amount0, amount1

#     def gen_market_depth(self, df, current_tick, current_sqrt_price, delta):
#         """Calculate market depth for a given price change percentage"""
#         if delta > 0:
#             target_sqrt_price = current_sqrt_price * np.sqrt(1 + delta)
#             target_tick = current_tick + int(np.log(1 + delta) / np.log(1.0001))
#         else:
#             target_sqrt_price = current_sqrt_price * np.sqrt(1 + delta)
#             target_tick = current_tick + int(np.log(1 + delta) / np.log(1.0001))
        
#         total_amount0 = 0
#         total_amount1 = 0
        
#         for _, position in df.iterrows():
#             tick_lower = int(position['tick_lower'])
#             tick_upper = int(position['tick_upper'])
#             liquidity = float(position['net_liquidity'])
            
#             if liquidity <= 0:
#                 continue
            
#             if delta > 0:
#                 if tick_upper <= current_tick or tick_lower >= target_tick:
#                     continue
#             else:
#                 if tick_upper <= target_tick or tick_lower >= current_tick:
#                     continue
            
#             sqrt_price_lower = 1.0001 ** (tick_lower / 2)
#             sqrt_price_upper = 1.0001 ** (tick_upper / 2)
            
#             amount0_current, amount1_current = self.calculate_token_amounts(
#                 liquidity, sqrt_price_lower, sqrt_price_upper, current_sqrt_price
#             )
            
#             amount0_target, amount1_target = self.calculate_token_amounts(
#                 liquidity, sqrt_price_lower, sqrt_price_upper, target_sqrt_price
#             )
            
#             delta_amount0 = abs(amount0_target - amount0_current)
#             delta_amount1 = abs(amount1_target - amount1_current)
            
#             total_amount0 += delta_amount0
#             total_amount1 += delta_amount1
        
#         amount0_decimal = total_amount0 / (10 ** self.token0_decimals)
#         amount1_decimal = total_amount1 / (10 ** self.token1_decimals)
        
#         return amount0_decimal, amount1_decimal

#     def pipe_market_depth(self, df, current_tick, current_sqrt_price_x96, pctchg):
#         """Main function to calculate market depth at multiple percentage levels"""
#         current_sqrt_price = float(current_sqrt_price_x96) / (2 ** 96)
        
#         results = []
        
#         for pct in pctchg:
#             amount0, amount1 = self.gen_market_depth(df, current_tick, current_sqrt_price, pct)
            
#             market_depth_usd = (amount0 * self.token0_price_usd) + (amount1 * self.token1_price_usd)
            
#             results.append({
#                 'pct': pct,
#                 'marketdepth_token0': amount0,
#                 'marketdepth_token1': amount1,
#                 'marketdepth_usd': market_depth_usd
#             })
        
#         return pd.DataFrame(results)

#     def calculate_tvl(self, df, current_tick, current_sqrt_price):
#         """Calculate Total Value Locked (TVL) in the pool"""
#         total_token0 = 0
#         total_token1 = 0
        
#         for _, position in df.iterrows():
#             tick_lower = int(position['tick_lower'])
#             tick_upper = int(position['tick_upper'])
#             liquidity = float(position['net_liquidity'])
            
#             if liquidity <= 0:
#                 continue
                
#             sqrt_price_lower = 1.0001 ** (tick_lower / 2)
#             sqrt_price_upper = 1.0001 ** (tick_upper / 2)
            
#             amount0, amount1 = self.calculate_token_amounts(
#                 liquidity, sqrt_price_lower, sqrt_price_upper, current_sqrt_price
#             )
            
#             total_token0 += amount0 / (10 ** self.token0_decimals)
#             total_token1 += amount1 / (10 ** self.token1_decimals)
        
#         token0_value_usd = total_token0 * self.token0_price_usd
#         token1_value_usd = total_token1 * self.token1_price_usd
#         total_value_usd = token0_value_usd + token1_value_usd
        
#         return {
#             'token0_amount': total_token0,
#             'token1_amount': total_token1,
#             'token0_value_usd': token0_value_usd,
#             'token1_value_usd': token1_value_usd,
#             'total_value_usd': total_value_usd
#         }

#     def tick_to_price(self, tick):
#         """Convert tick to price (token1/token0)"""
#         return 1.0001 ** tick

#     def prepare_liquidity_distribution(self, df, current_tick, current_sqrt_price, tick_spacing=None):
#         """Prepare liquidity distribution data for visualization"""
#         if tick_spacing is None:
#             tick_spacing = self.tick_spacing
        
#         # Calculate current values for each position
#         positions_with_values = []
        
#         for _, position in df.iterrows():
#             tick_lower = int(position['tick_lower'])
#             tick_upper = int(position['tick_upper'])
#             liquidity = float(position['net_liquidity'])
            
#             if liquidity <= 0:
#                 continue
            
#             # Calculate current token amounts
#             sqrt_price_lower = 1.0001 ** (tick_lower / 2)
#             sqrt_price_upper = 1.0001 ** (tick_upper / 2)
            
#             amount0, amount1 = self.calculate_token_amounts(
#                 liquidity, sqrt_price_lower, sqrt_price_upper, current_sqrt_price
#             )
            
#             # Convert to decimal amounts
#             amount0_decimal = amount0 / (10 ** self.token0_decimals)
#             amount1_decimal = amount1 / (10 ** self.token1_decimals)
            
#             # Calculate USD value
#             usd_value = (amount0_decimal * self.token0_price_usd) + (amount1_decimal * self.token1_price_usd)
            
#             # Calculate price range
#             price_lower = self.tick_to_price(tick_lower)
#             price_upper = self.tick_to_price(tick_upper)
#             price_mid = np.sqrt(price_lower * price_upper)  # Geometric mean
            
#             # Calculate distance from current price
#             current_price = self.tick_to_price(current_tick)
#             distance_from_current = (price_mid - current_price) / current_price
            
#             positions_with_values.append({
#                 'tick_lower': tick_lower,
#                 'tick_upper': tick_upper,
#                 'price_lower': price_lower,
#                 'price_upper': price_upper,
#                 'price_mid': price_mid,
#                 'liquidity': liquidity,
#                 'amount0': amount0_decimal,
#                 'amount1': amount1_decimal,
#                 'usd_value': usd_value,
#                 'distance_from_current': distance_from_current,
#                 'is_active': tick_lower <= current_tick <= tick_upper
#             })
        
#         return pd.DataFrame(positions_with_values)

# def load_pools_from_json(v3_filename="pools_uni_v3.json", v4_filename="pools_uni_v4.json"):
#     """Load pool data from both V3 and V4 JSON files"""
#     all_pools = []
    
#     # Load V3 pools
#     try:
#         with open(v3_filename, 'r') as f:
#             v3_data = json.load(f)
#         v3_pools = v3_data.get('pools', []) if 'pools' in v3_data else v3_data
#         for pool in v3_pools:
#             pool['version'] = 'v3'
#             all_pools.append(pool)
#         st.session_state['log_messages'] = f"Loaded {len(v3_pools)} Uniswap V3 pools"
#     except FileNotFoundError:
#         st.session_state['log_messages'] = f"Warning: File '{v3_filename}' not found!"
#     except json.JSONDecodeError:
#         st.session_state['log_messages'] = f"Error: Invalid JSON in '{v3_filename}'!"
    
#     # Load V4 pools
#     try:
#         with open(v4_filename, 'r') as f:
#             v4_data = json.load(f)
#         v4_pools = v4_data if isinstance(v4_data, list) else v4_data.get('pools', [])
#         for pool in v4_pools:
#             pool['version'] = 'v4'
#             pool['poolAddress'] = pool.get('poolAddress')  # This is actually the pool ID for V4
#             all_pools.append(pool)
#         st.session_state['log_messages'] = f"Loaded {len(v4_pools)} Uniswap V4 pools"
#     except FileNotFoundError:
#         st.session_state['log_messages'] = f"Warning: File '{v4_filename}' not found!"
#     except json.JSONDecodeError:
#         st.session_state['log_messages'] = f"Error: Invalid JSON in '{v4_filename}'!"
    
#     return all_pools

# def generate_dune_query_v3(pool_address):
#     """Generate the Dune SQL query for Uniswap V3 pools"""
#     return f"""
# -- Uniswap V3 Market Depth Analysis Query
# WITH current_positions AS (
#   SELECT 
#     tickLower as tick_lower,
#     tickUpper as tick_upper,
#     amount as liquidity,
#     evt_tx_hash,
#     evt_block_number,
#     evt_block_time,
#     CAST(amount AS INT256) as liquidity_delta
#   FROM uniswap_v3_ethereum.uniswapv3pool_evt_mint m
#   WHERE m.contract_address = {pool_address}
  
#   UNION ALL
  
#   SELECT 
#     tickLower as tick_lower,
#     tickUpper as tick_upper,
#     amount as liquidity,
#     evt_tx_hash,
#     evt_block_number,
#     evt_block_time,
#     -CAST(amount AS INT256) as liquidity_delta
#   FROM uniswap_v3_ethereum.uniswapv3pool_evt_burn b
#   WHERE b.contract_address = {pool_address}
# ),
# net_liquidity AS (
#   SELECT 
#     tick_lower,
#     tick_upper,
#     SUM(liquidity_delta) as net_liquidity
#   FROM current_positions
#   GROUP BY tick_lower, tick_upper
#   HAVING SUM(liquidity_delta) > 0
# ),
# current_price AS (
#   SELECT 
#     sqrtPriceX96 as sqrt_price_x96,
#     tick,
#     evt_block_number,
#     evt_block_time
#   FROM uniswap_v3_ethereum.uniswapv3pool_evt_swap s
#   WHERE s.contract_address = {pool_address}
#   ORDER BY evt_block_number DESC, evt_index DESC
#   LIMIT 1
# )
# SELECT 
#   nl.tick_lower,
#   nl.tick_upper,
#   nl.net_liquidity,
#   cp.sqrt_price_x96,
#   cp.tick as current_tick,
#   cp.evt_block_time as price_timestamp,
#   CAST(cp.sqrt_price_x96 AS DOUBLE) / POWER(2, 96) as sqrt_price,
#   POWER(CAST(cp.sqrt_price_x96 AS DOUBLE) / POWER(2, 96), 2) as current_price
# FROM net_liquidity nl
# CROSS JOIN current_price cp
# WHERE nl.net_liquidity > 0
# ORDER BY nl.tick_lower
# """

# def generate_dune_query_v4(pool_id):
#     """Generate the Dune SQL query for Uniswap V4 pools"""
#     return f"""
# -- Uniswap V4 Market Depth Analysis Query
# WITH current_positions AS (
#   SELECT 
#     tickLower as tick_lower,
#     tickUpper as tick_upper,
#     liquidityDelta as liquidity_delta,
#     evt_tx_hash,
#     evt_block_number,
#     evt_block_time,
#     id as pool_id
#   FROM uniswap_v4_ethereum.poolmanager_evt_modifyliquidity ml
#   WHERE ml.contract_address = 0x000000000004444c5dc75cb358380d2e3de08a90
#     AND ml.id = {pool_id}
# ),
# net_liquidity AS (
#   SELECT 
#     tick_lower,
#     tick_upper,
#     SUM(liquidity_delta) as net_liquidity
#   FROM current_positions
#   GROUP BY tick_lower, tick_upper
#   HAVING SUM(liquidity_delta) > 0
# ),
# current_price AS (
#   SELECT 
#     sqrtPriceX96 as sqrt_price_x96,
#     tick,
#     evt_block_number,
#     evt_block_time
#   FROM uniswap_v4_ethereum.poolmanager_evt_swap s
#   WHERE s.contract_address = 0x000000000004444c5dc75cb358380d2e3de08a90
#     AND s.id = {pool_id}
#   ORDER BY evt_block_number DESC, evt_index DESC
#   LIMIT 1
# )
# SELECT 
#   nl.tick_lower,
#   nl.tick_upper,
#   nl.net_liquidity,
#   cp.sqrt_price_x96,
#   cp.tick as current_tick,
#   cp.evt_block_time as price_timestamp,
#   CAST(cp.sqrt_price_x96 AS DOUBLE) / POWER(2, 96) as sqrt_price,
#   POWER(CAST(cp.sqrt_price_x96 AS DOUBLE) / POWER(2, 96), 2) as current_price
# FROM net_liquidity nl
# CROSS JOIN current_price cp
# WHERE nl.net_liquidity > 0
# ORDER BY nl.tick_lower
# """

# def get_token_price_from_coingecko(coingecko_id, token_symbol):
#     """Fetch current token price from CoinGecko API"""
#     if not coingecko_id:
#         st.session_state['log_messages'] = f"No CoinGecko ID available for {token_symbol}"
#         return get_manual_token_price(token_symbol)
    
#     try:
#         url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
        
#         data = response.json()
#         if coingecko_id in data and 'usd' in data[coingecko_id]:
#             price = data[coingecko_id]['usd']
#             st.session_state['log_messages'] = f"Fetched {token_symbol} price from CoinGecko: ${price}"
#             return float(price)
#         else:
#             st.session_state['log_messages'] = f"Price not found for {token_symbol} ({coingecko_id})"
#             return get_manual_token_price(token_symbol)
            
#     except requests.exceptions.RequestException as e:
#         st.session_state['log_messages'] = f"Error fetching price for {token_symbol} from CoinGecko: {e}"
#         return get_manual_token_price(token_symbol)
#     except (KeyError, ValueError) as e:
#         st.session_state['log_messages'] = f"Error parsing price data for {token_symbol}: {e}"
#         return get_manual_token_price(token_symbol)

# def get_manual_token_price(token_symbol):
#     """Fallback to manual price entry with smart defaults"""
#     default_prices = {
#         'USDC': 1.0,
#         'USDT': 1.0,
#         'DAI': 1.0,
#         'FRAX': 1.0,
#         'LUSD': 1.0,
#         'BOLD': 1.0,
#         'USD0': 1.0,
#         'USD0++': 1.0,
#         'OUSD': 1.0,
#         'WETH': 2600.0,
#         'ETH': 2600.0,
#         'WBTC': 65000.0,
#         'BTC': 65000.0,
#         'syrupUSDC': 1.0,
#     }
    
#     if token_symbol in default_prices:
#         default_price = default_prices[token_symbol]
#         return default_price
#     else:
#         return 1.0  # Default fallback price

# def plot_market_depth_curve(market_depth, token0_symbol, token1_symbol, version):
#     """Plot the market depth curve"""
#     fig, ax = plt.subplots(figsize=(10, 6))
    
#     buy_side = market_depth[market_depth['pct'] > 0].sort_values('pct')
#     sell_side = market_depth[market_depth['pct'] < 0].sort_values('pct')
    
#     ax.plot(buy_side['pct'] * 100, buy_side['marketdepth_usd'], 'g-', linewidth=2, label='Buy side')
#     ax.plot(sell_side['pct'] * 100, sell_side['marketdepth_usd'], 'r-', linewidth=2, label='Sell side')
    
#     ax.set_xlabel('Price Impact (%)')
#     ax.set_ylabel('Market Depth (USD)')
#     ax.set_title(f'{token0_symbol}/{token1_symbol} Market Depth Profile [Uniswap {version.upper()}]')
#     ax.grid(True, alpha=0.3)
#     ax.legend()
    
#     return fig

# def plot_liquidity_distribution(liquidity_df, token0_symbol, token1_symbol, current_tick, version):
#     """Plot the liquidity distribution"""
#     fig, ax = plt.subplots(figsize=(10, 6))
    
#     # Sort by price for better visualization
#     liquidity_df_sorted = liquidity_df.sort_values('price_lower')
    
#     # Calculate current price
#     current_price = 1.0001 ** current_tick
    
#     # Position ranges as horizontal bars
#     y_positions = range(len(liquidity_df_sorted))
    
#     for i, (_, row) in enumerate(liquidity_df_sorted.iterrows()):
#         color = 'green' if row['is_active'] else 'lightblue'
#         alpha = 0.8 if row['is_active'] else 0.4
        
#         # Draw horizontal bar representing the price range
#         ax.barh(i, row['price_upper'] - row['price_lower'], 
#                 left=row['price_lower'], height=0.8,
#                 color=color, alpha=alpha, 
#                 edgecolor='black', linewidth=0.5)
    
#     # Add current price line
#     ax.axvline(current_price, color='red', linestyle='--', linewidth=2, 
#                label=f'Current Price: {current_price:.6f}')
    
#     ax.set_xlabel(f'Price Range ({token1_symbol}/{token0_symbol})')
#     ax.set_ylabel('Position Index')
#     ax.set_title(f'Liquidity Position Ranges [Uniswap {version.upper()}]\n(Green = Active, Blue = Out of Range)')
#     ax.legend()
#     ax.grid(True, alpha=0.3)
    
#     return fig

# def analyze_uniswap_pool(selected_pool, dune_api_key):
#     """Analyze a selected Uniswap pool"""
#     version = selected_pool['version']
#     pool_identifier = selected_pool['poolAddress']
#     token0 = selected_pool['token0']
#     token1 = selected_pool['token1']
#     fee_tier = selected_pool['feeTier']
#     pool_name = f"{token0['symbol']}/{token1['symbol']}"
    
#     st.write(f"### Analyzing {pool_name} [Uniswap {version.upper()}]")
    
#     # Get token prices
#     token0_price = get_token_price_from_coingecko(token0.get('coingeckoId'), token0['symbol'])
#     token1_price = get_token_price_from_coingecko(token1.get('coingeckoId'), token1['symbol'])
    
#     # Determine tick spacing
#     fee_tier_to_basis_points = {0.001: 1, 0.05: 500, 0.3: 3000, 1.0: 10000}
#     fee_basis_points = fee_tier_to_basis_points.get(fee_tier, 3000)
#     tick_spacing_map = {1: 1, 500: 10, 3000: 60, 10000: 200}
#     tick_spacing = tick_spacing_map.get(fee_basis_points, 60)
    
#     # Initialize Dune client
#     dune_client = DuneClient(dune_api_key)
    
#     # Generate and execute appropriate Dune query
#     if version == 'v3':
#         query_sql = generate_dune_query_v3(pool_identifier)
#     else:  # v4
#         query_sql = generate_dune_query_v4(pool_identifier)
    
#     with st.spinner(f"Querying {pool_name} liquidity data from Dune Analytics..."):
#         execution_id = dune_client.create_and_execute_query(
#             query_sql, 
#             f"{pool_name} {version.upper()} Market Depth Analysis"
#         )
        
#         if execution_id is None:
#             st.error("Failed to execute Dune query. Please check your API key and try again.")
#             return None, None, None
        
#         results = dune_client.wait_for_completion(execution_id, max_wait_time=300)
        
#         if results is None:
#             st.error("Failed to get query results")
#             return None, None, None
    
#     # Process results
#     if 'result' in results and 'rows' in results['result']:
#         rows = results['result']['rows']
        
#         if not rows:
#             st.warning("No liquidity positions found for this pool.")
#             return None, None, None
        
#         # Convert to DataFrame
#         df = pd.DataFrame(rows)
        
#         # Ensure numeric types
#         df['tick_lower'] = pd.to_numeric(df['tick_lower'], errors='coerce')
#         df['tick_upper'] = pd.to_numeric(df['tick_upper'], errors='coerce')
#         df['net_liquidity'] = pd.to_numeric(df['net_liquidity'], errors='coerce')
#         df['sqrt_price_x96'] = pd.to_numeric(df['sqrt_price_x96'], errors='coerce')
#         df['current_tick'] = pd.to_numeric(df['current_tick'], errors='coerce')
        
#         # Remove NaN values
#         df = df.dropna()
        
#         if len(df) == 0:
#             st.warning("No valid liquidity positions after data cleaning.")
#             return None, None, None
        
#         # Extract current state
#         current_tick = int(df['current_tick'].iloc[0])
#         current_sqrt_price_x96 = int(df['sqrt_price_x96'].iloc[0])
#         current_sqrt_price = float(current_sqrt_price_x96) / (2 ** 96)
        
#         # Initialize market depth calculator
#         calculator = MarketDepthCalculator(
#             token0['symbol'], token1['symbol'],
#             token0['decimals'], token1['decimals'],
#             token0_price, token1_price,
#             tick_spacing
#         )
        
#         # Calculate TVL
#         tvl = calculator.calculate_tvl(df, current_tick, current_sqrt_price)
        
#         # Prepare liquidity distribution
#         liquidity_df = calculator.prepare_liquidity_distribution(df, current_tick, current_sqrt_price, tick_spacing)
        
#         # Define percentage changes for market depth calculation
#         pctchg = [
#             -0.10, -0.06, -0.05, -0.04, -0.02, -0.01, -0.0075, -0.005, -0.004, 
#             -0.003, -0.002, -0.001, -0.00075, -0.0005, -0.00025,
#             0.00025, 0.0005, 0.00075, 0.001, 0.002, 0.003, 0.004, 0.005, 
#             0.0075, 0.01, 0.02, 0.04, 0.05, 0.06, 0.10
#         ]
        
#         # Calculate market depth
#         market_depth = calculator.pipe_market_depth(df, current_tick, current_sqrt_price_x96, pctchg)
        
#         return market_depth, liquidity_df, current_tick, tvl
#     else:
#         st.error(f"Unable to retrieve data for {pool_name}")
#         return None, None, None, None

# def analyze_curve_pool(pair_name):
#     """Analyze a Curve pool"""
#     fetcher = CurveMarketDepthFetcher()
    
#     # Load pools configuration
#     config_loaded = fetcher.load_pools_config("curve_pools_config.json")
    
#     if not config_loaded:
#         st.error("Failed to load Curve pools configuration")
#         return None, None
    
#     pool_config = fetcher.get_pool_by_pair_name(pair_name)
#     if not pool_config:
#         st.error(f"Pool with pair name '{pair_name}' not found")
#         return None, None
    
#     # Fetch data
#     data = fetcher.fetch_market_depth(
#         pool_config['pool_address'],
#         pool_config['token1_address'],
#         pool_config['token2_address']
#     )
    
#     if not data:
#         st.error("Failed to fetch data")
#         return None, None
    
#     try:
#         # Parse data
#         bid_data, ask_data, spot_prices = fetcher.parse_market_depth_data(data)
#         return bid_data, ask_data, spot_prices, pool_config['pair_name']
#     except Exception as e:
#         st.error(f"Error processing data: {e}")
#         return None, None, None, None

# def plot_curve_market_depth(bid_data, ask_data, spot_prices, pair_name):
#     """Plot Curve market depth"""
#     fig, ax = plt.subplots(figsize=(12, 8))
    
#     # Prepare data for plotting
#     if bid_data:
#         bid_impacts, bid_liquidity = zip(*bid_data)
#         # Convert to negative price impacts for bids (left side)
#         bid_impacts = [-x for x in bid_impacts]
#         ax.bar(bid_impacts, [x/1e6 for x in bid_liquidity], 
#               width=0.002, color='#4169E1', alpha=0.8, label='Bids')
    
#     if ask_data:
#         ask_impacts, ask_liquidity = zip(*ask_data)
#         ax.bar(ask_impacts, [x/1e6 for x in ask_liquidity], 
#               width=0.002, color='#FF1493', alpha=0.8, label='Asks')
    
#     # Add spot price line
#     ax.axvline(x=0, color='gray', linestyle='--', alpha=0.7, linewidth=1)
    
#     # Formatting
#     ax.set_xlabel('Price Impact (%)', fontsize=12)
#     ax.set_ylabel('Liquidity (M USD)', fontsize=12)
#     ax.set_title(f'Market Depth - {pair_name}', fontsize=14, fontweight='bold')
    
#     # Format x-axis to show percentages
#     ax.set_xlim(-0.05, 0.05)
#     x_ticks = np.arange(-0.04, 0.05, 0.01)
#     ax.set_xticks(x_ticks)
#     ax.set_xticklabels([f'{x:.1%}' for x in x_ticks])
    
#     # Add grid
#     ax.grid(True, alpha=0.3)
    
#     # Add spot price annotation
#     ax.text(0.02, ax.get_ylim()[1] * 0.9, 
#            f'Spot price: {spot_prices[0]:.4f}', 
#            fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
    
#     # Add legend
#     ax.legend()
    
#     plt.tight_layout()
#     return fig

# def main():
#     """Main Streamlit app function"""
#     st.title("DeFi Market Depth Analyzer")
#     st.markdown("""
#     Analyze market depth and liquidity distribution for Curve and Uniswap V3/V4 pools.
#     """)
    
#     # Initialize session state
#     if 'log_messages' not in st.session_state:
#         st.session_state['log_messages'] = ""
#     if 'dune_message' not in st.session_state:
#         st.session_state['dune_message'] = ""
    
#     # Create tabs for different protocols
#     tab1, tab2 = st.tabs(["Uniswap V3/V4", "Curve"])
    
#     with tab1:
#         st.header("Uniswap V3/V4 Market Depth Analysis")
        
#         # Load pools
#         pools = load_pools_from_json()
        
#         if not pools:
#             st.error("No pools available. Please check your JSON files.")
#             return
        
#         # Split into V3 and V4 pools
#         v3_pools = [p for p in pools if p.get('version') == 'v3']
#         v4_pools = [p for p in pools if p.get('version') == 'v4']
        
#         # Create columns for pool selection and settings
#         col1, col2 = st.columns([3, 1])
        
#         with col1:
#             # Pool selection
#             pool_options = []
#             if v3_pools:
#                 pool_options.append("🦄 Uniswap V3 Pools")
#                 for i, pool in enumerate(v3_pools, 1):
#                     token0 = pool['token0']['symbol']
#                     token1 = pool['token1']['symbol']
#                     fee_tier = pool['feeTier']
#                     pool_options.append(f"{i}. {token0}/{token1} (Fee: {fee_tier}%) [V3]")
            
#             if v4_pools:
#                 pool_options.append("\n🦄 Uniswap V4 Pools")
#                 start_idx = len(v3_pools) + 1
#                 for i, pool in enumerate(v4_pools, start_idx):
#                     token0 = pool['token0']['symbol']
#                     token1 = pool['token1']['symbol']
#                     fee_tier = pool['feeTier']
#                     pool_options.append(f"{i}. {token0}/{token1} (Fee: {fee_tier}%) [V4]")
            
#             selected_option = st.selectbox(
#                 "Select a pool to analyze:",
#                 pool_options,
#                 index=0
#             )
            
#             # Parse selection
#             try:
#                 if selected_option.startswith(("🦄", "\n🦄")):
#                     st.warning("Please select a specific pool from the list")
#                     selected_pool = None
#                 else:
#                     # Extract pool index from selection (e.g., "1. ETH/USDC" -> 0)
#                     pool_index = int(selected_option.split('.')[0]) - 1
#                     selected_pool = pools[pool_index]
#             except:
#                 selected_pool = None
        
#         with col2:
#             # Dune API key input
#             dune_api_key = st.text_input(
#                 "Dune API Key (optional)",
#                 type="password",
#                 help="Required for Uniswap analysis. Get one at https://dune.com/settings/api"
#             )
        
#         if selected_pool:
#             # Display pool info
#             version = selected_pool['version']
#             token0 = selected_pool['token0']
#             token1 = selected_pool['token1']
            
#             st.subheader(f"{token0['symbol']}/{token1['symbol']} [Uniswap {version.upper()}]")
            
#             if version == 'v3':
#                 st.caption(f"Pool Address: {selected_pool['poolAddress']}")
#             else:
#                 st.caption(f"Pool ID: {selected_pool['poolAddress']}")
            
#             st.caption(f"Fee Tier: {selected_pool['feeTier']}%")
            
#             # Analyze button
#             if st.button("Analyze Pool", key="analyze_uniswap"):
#                 if not dune_api_key:
#                     st.warning("Please enter a Dune API key to analyze Uniswap pools")
#                 else:
#                     with st.spinner("Analyzing pool..."):
#                         market_depth, liquidity_df, current_tick, tvl = analyze_uniswap_pool(selected_pool, dune_api_key)
                        
#                         if market_depth is not None and liquidity_df is not None:
#                             # Display metrics
#                             col1, col2, col3 = st.columns(3)
                            
#                             with col1:
#                                 st.metric("Total Value Locked", f"${tvl['total_value_usd']:,.2f}")
#                                 st.metric(f"{token0['symbol']} Amount", f"{tvl['token0_amount']:,.4f}")                            
#                             with col2:
#                                 active_liquidity = liquidity_df[liquidity_df['is_active']]['usd_value'].sum()
#                                 efficiency = (active_liquidity / liquidity_df['usd_value'].sum()) * 100
#                                 st.metric("Active Liquidity", f"${active_liquidity:,.2f}")
#                                 st.metric(f"{token1['symbol']} Amount", f"{tvl['token1_amount']:,.4f}")
                            
#                             with col3:
#                                 st.metric("Liquidity Efficiency", f"{efficiency:.1f}%")
#                                 if tvl['token0_amount'] > 0:
#                                     current_price = tvl['token1_amount'] / tvl['token0_amount']
#                                     st.metric("Current Price", f"1 {token0['symbol']} = {current_price:.6f} {token1['symbol']}")
                            
#                             # Display charts
#                             st.subheader("Market Depth Profile")
#                             st.pyplot(plot_market_depth_curve(market_depth, token0['symbol'], token1['symbol'], version))
                            
#                             st.subheader("Liquidity Distribution")
#                             st.pyplot(plot_liquidity_distribution(liquidity_df, token0['symbol'], token1['symbol'], current_tick, version))
                            
#                             # Show data tables
#                             with st.expander("View Market Depth Data"):
#                                 st.dataframe(market_depth)
                            
#                             with st.expander("View Liquidity Distribution Data"):
#                                 st.dataframe(liquidity_df)
    
#     with tab2:
#         st.header("Curve Market Depth Analysis")
        
#         # Initialize Curve fetcher
#         fetcher = CurveMarketDepthFetcher()
        
#         # Load pools configuration
#         config_loaded = fetcher.load_pools_config("curve_pools_config.json")
        
#         if config_loaded:
#             # Get available pairs
#             pairs = fetcher.list_available_pairs()
            
#             if pairs:
#                 # Pair selection
#                 selected_pair = st.selectbox(
#                     "Select a Curve pool to analyze:",
#                     pairs,
#                     index=0
#                 )
                
#                 # Analyze button
#                 if st.button("Analyze Pool", key="analyze_curve"):
#                     with st.spinner(f"Analyzing {selected_pair}..."):
#                         bid_data, ask_data, spot_prices, pair_name = analyze_curve_pool(selected_pair)
                        
#                         if bid_data is not None and ask_data is not None:
#                             # Display metrics
#                             col1, col2 = st.columns(2)
                            
#                             with col1:
#                                 total_bid_liquidity = sum([x[1] for x in bid_data]) / 1e6
#                                 st.metric("Total Bid Liquidity", f"${total_bid_liquidity:,.2f}M")
                            
#                             with col2:
#                                 total_ask_liquidity = sum([x[1] for x in ask_data]) / 1e6
#                                 st.metric("Total Ask Liquidity", f"${total_ask_liquidity:,.2f}M")
                            
#                             st.metric("Spot Price", f"{spot_prices[0]:.6f}")
                            
#                             # Display chart
#                             st.subheader("Market Depth")
#                             st.pyplot(plot_curve_market_depth(bid_data, ask_data, spot_prices, pair_name))
                            
#                             # Show data
#                             with st.expander("View Bid Data"):
#                                 bid_df = pd.DataFrame(bid_data, columns=['Price Impact', 'Liquidity'])
#                                 st.dataframe(bid_df)
                            
#                             with st.expander("View Ask Data"):
#                                 ask_df = pd.DataFrame(ask_data, columns=['Price Impact', 'Liquidity'])
#                                 st.dataframe(ask_df)
#             else:
#                 st.warning("No Curve pools found in configuration")
#         else:
#             st.error("Failed to load Curve pools configuration")
    
#     # Display logs in sidebar
#     with st.sidebar:
#         st.header("Settings & Logs")
        
#         # API keys
#         st.subheader("API Keys")
#         dune_api_key = st.text_input(
#             "Dune API Key",
#             type="password",
#             help="Required for Uniswap analysis. Get one at https://dune.com/settings/api"
#         )
        
#         # Logs
#         st.subheader("Log Messages")
#         if st.session_state['log_messages']:
#             st.text(st.session_state['log_messages'])
        
#         if st.session_state['dune_message']:
#             st.text(st.session_state['dune_message'])
        
#         # About section
#         st.subheader("About")
#         st.markdown("""
#         This app analyzes market depth and liquidity distribution for:
#         - Uniswap V3/V4 pools (using Dune Analytics)
#         - Curve pools (using DeFiRisk API)
        
#         **Note:** For Uniswap analysis, a Dune API key is required.
#         """)

# if __name__ == "__main__":
#     main()


import streamlit as st
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import requests
import time
from typing import Dict, Any, Optional, List, Tuple
from curve_liquidity_monitoring import MarketDepthFetcher as CurveMarketDepthFetcher

# Set page config
st.set_page_config(
    page_title="DeFi Market Depth Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stSelectbox>div>div>select {
        padding: 0.5rem;
    }
    .stSlider>div>div>div>div {
        background-color: #4CAF50;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-title {
        font-size: 1rem;
        font-weight: 600;
        color: #555;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #333;
    }
    .tab-content {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize classes from the provided scripts
class DuneClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.dune.com/api/v1"
        self.headers = {
            "X-Dune-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def execute_query_by_id(self, query_id: int, parameters: Dict = None, performance: str = "medium") -> Optional[str]:
        """Execute an existing query by ID on Dune Analytics"""
        url = f"{self.base_url}/query/{query_id}/execute"
        
        payload = {"performance": performance}
        if parameters:
            payload["query_parameters"] = parameters
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            execution_id = result.get("execution_id")
            
            if execution_id:
                st.session_state['dune_message'] = f"Query execution submitted successfully. Execution ID: {execution_id}"
                return execution_id
            else:
                st.session_state['dune_message'] = "Failed to get execution ID from response"
                return None
                
        except requests.exceptions.RequestException as e:
            st.session_state['dune_message'] = f"Error executing query: {e}"
            return None
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get the status of a query execution"""
        url = f"{self.base_url}/execution/{execution_id}/status"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.session_state['dune_message'] = f"Error getting execution status: {e}"
            return {"state": "FAILED", "error": str(e)}
    
    def get_execution_results(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the results of a completed query execution"""
        url = f"{self.base_url}/execution/{execution_id}/results"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.session_state['dune_message'] = f"Error getting execution results: {e}"
            return None
    
    def wait_for_completion(self, execution_id: str, max_wait_time: int = 300, 
                          poll_interval: int = 5) -> Optional[Dict[str, Any]]:
        """Wait for query execution to complete and return results"""
        start_time = time.time()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        while time.time() - start_time < max_wait_time:
            elapsed = time.time() - start_time
            progress = min(elapsed / max_wait_time, 1.0)
            progress_bar.progress(progress)
            
            status = self.get_execution_status(execution_id)
            state = status.get("state", "UNKNOWN")
            
            status_text.text(f"Query status: {state} ({(elapsed/60):.1f} minutes elapsed)")
            
            if state == "QUERY_STATE_COMPLETED":
                progress_bar.progress(1.0)
                status_text.text("Query completed successfully!")
                return self.get_execution_results(execution_id)
            elif state == "QUERY_STATE_FAILED":
                progress_bar.progress(1.0)
                status_text.text(f"Query failed: {status.get('error', 'Unknown error')}")
                return None
            elif state in ["QUERY_STATE_EXECUTING", "QUERY_STATE_PENDING"]:
                time.sleep(poll_interval)
            else:
                time.sleep(poll_interval)
        
        progress_bar.progress(1.0)
        status_text.text(f"Query timed out after {max_wait_time} seconds")
        return None

    def create_and_execute_query(self, query_sql: str, name: str = "API Query") -> Optional[str]:
        """Alternative approach: Try to create and execute in one go"""
        try:
            url = f"{self.base_url}/execution"
            payload = {
                "query_sql": query_sql,
                "performance": "medium"
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                execution_id = result.get("execution_id")
                if execution_id:
                    st.session_state['dune_message'] = f"Query submitted via direct execution. Execution ID: {execution_id}"
                    return execution_id
        except:
            pass
        
        try:
            url = f"{self.base_url}/query"
            payload = {
                "query_sql": query_sql,
                "name": name,
                "is_private": False
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                query_id = result.get("query_id")
                if query_id:
                    return self.execute_query_by_id(query_id)
        except Exception as e:
            st.session_state['dune_message'] = f"Query creation failed: {e}"
        
        return None

class MarketDepthCalculator:
    def __init__(self, token0_symbol, token1_symbol, token0_decimals, token1_decimals, 
                 token0_price_usd, token1_price_usd, tick_spacing=60):
        self.token0_symbol = token0_symbol
        self.token1_symbol = token1_symbol
        self.token0_decimals = token0_decimals
        self.token1_decimals = token1_decimals
        self.token0_price_usd = token0_price_usd
        self.token1_price_usd = token1_price_usd
        self.tick_spacing = tick_spacing

    def calculate_token_amounts(self, liquidity, sqrt_price_lower, sqrt_price_upper, sqrt_price_current):
        """Calculate token amounts for a liquidity position"""
        liquidity = float(liquidity)
        
        if sqrt_price_current <= sqrt_price_lower:
            amount0 = liquidity * (1/sqrt_price_lower - 1/sqrt_price_upper)
            amount1 = 0
        elif sqrt_price_current >= sqrt_price_upper:
            amount0 = 0
            amount1 = liquidity * (sqrt_price_upper - sqrt_price_lower)
        else:
            amount0 = liquidity * (1/sqrt_price_current - 1/sqrt_price_upper)
            amount1 = liquidity * (sqrt_price_current - sqrt_price_lower)
        
        return amount0, amount1

    def gen_market_depth(self, df, current_tick, current_sqrt_price, delta):
        """Calculate market depth for a given price change percentage"""
        if delta > 0:
            target_sqrt_price = current_sqrt_price * np.sqrt(1 + delta)
            target_tick = current_tick + int(np.log(1 + delta) / np.log(1.0001))
        else:
            target_sqrt_price = current_sqrt_price * np.sqrt(1 + delta)
            target_tick = current_tick + int(np.log(1 + delta) / np.log(1.0001))
        
        total_amount0 = 0
        total_amount1 = 0
        
        for _, position in df.iterrows():
            tick_lower = int(position['tick_lower'])
            tick_upper = int(position['tick_upper'])
            liquidity = float(position['net_liquidity'])
            
            if liquidity <= 0:
                continue
            
            if delta > 0:
                if tick_upper <= current_tick or tick_lower >= target_tick:
                    continue
            else:
                if tick_upper <= target_tick or tick_lower >= current_tick:
                    continue
            
            sqrt_price_lower = 1.0001 ** (tick_lower / 2)
            sqrt_price_upper = 1.0001 ** (tick_upper / 2)
            
            amount0_current, amount1_current = self.calculate_token_amounts(
                liquidity, sqrt_price_lower, sqrt_price_upper, current_sqrt_price
            )
            
            amount0_target, amount1_target = self.calculate_token_amounts(
                liquidity, sqrt_price_lower, sqrt_price_upper, target_sqrt_price
            )
            
            delta_amount0 = abs(amount0_target - amount0_current)
            delta_amount1 = abs(amount1_target - amount1_current)
            
            total_amount0 += delta_amount0
            total_amount1 += delta_amount1
        
        amount0_decimal = total_amount0 / (10 ** self.token0_decimals)
        amount1_decimal = total_amount1 / (10 ** self.token1_decimals)
        
        return amount0_decimal, amount1_decimal

    def pipe_market_depth(self, df, current_tick, current_sqrt_price_x96, pctchg):
        """Main function to calculate market depth at multiple percentage levels"""
        current_sqrt_price = float(current_sqrt_price_x96) / (2 ** 96)
        
        results = []
        
        for pct in pctchg:
            amount0, amount1 = self.gen_market_depth(df, current_tick, current_sqrt_price, pct)
            
            market_depth_usd = (amount0 * self.token0_price_usd) + (amount1 * self.token1_price_usd)
            
            results.append({
                'pct': pct,
                'marketdepth_token0': amount0,
                'marketdepth_token1': amount1,
                'marketdepth_usd': market_depth_usd
            })
        
        return pd.DataFrame(results)

    def calculate_tvl(self, df, current_tick, current_sqrt_price):
        """Calculate Total Value Locked (TVL) in the pool"""
        total_token0 = 0
        total_token1 = 0
        
        for _, position in df.iterrows():
            tick_lower = int(position['tick_lower'])
            tick_upper = int(position['tick_upper'])
            liquidity = float(position['net_liquidity'])
            
            if liquidity <= 0:
                continue
                
            sqrt_price_lower = 1.0001 ** (tick_lower / 2)
            sqrt_price_upper = 1.0001 ** (tick_upper / 2)
            
            amount0, amount1 = self.calculate_token_amounts(
                liquidity, sqrt_price_lower, sqrt_price_upper, current_sqrt_price
            )
            
            total_token0 += amount0 / (10 ** self.token0_decimals)
            total_token1 += amount1 / (10 ** self.token1_decimals)
        
        token0_value_usd = total_token0 * self.token0_price_usd
        token1_value_usd = total_token1 * self.token1_price_usd
        total_value_usd = token0_value_usd + token1_value_usd
        
        return {
            'token0_amount': total_token0,
            'token1_amount': total_token1,
            'token0_value_usd': token0_value_usd,
            'token1_value_usd': token1_value_usd,
            'total_value_usd': total_value_usd
        }

    def tick_to_price(self, tick):
        """Convert tick to price (token1/token0)"""
        return 1.0001 ** tick

    def prepare_liquidity_distribution(self, df, current_tick, current_sqrt_price, tick_spacing=None):
        """Prepare liquidity distribution data for visualization"""
        if tick_spacing is None:
            tick_spacing = self.tick_spacing
        
        # Calculate current values for each position
        positions_with_values = []
        
        for _, position in df.iterrows():
            tick_lower = int(position['tick_lower'])
            tick_upper = int(position['tick_upper'])
            liquidity = float(position['net_liquidity'])
            
            if liquidity <= 0:
                continue
            
            # Calculate current token amounts
            sqrt_price_lower = 1.0001 ** (tick_lower / 2)
            sqrt_price_upper = 1.0001 ** (tick_upper / 2)
            
            amount0, amount1 = self.calculate_token_amounts(
                liquidity, sqrt_price_lower, sqrt_price_upper, current_sqrt_price
            )
            
            # Convert to decimal amounts
            amount0_decimal = amount0 / (10 ** self.token0_decimals)
            amount1_decimal = amount1 / (10 ** self.token1_decimals)
            
            # Calculate USD value
            usd_value = (amount0_decimal * self.token0_price_usd) + (amount1_decimal * self.token1_price_usd)
            
            # Calculate price range
            price_lower = self.tick_to_price(tick_lower)
            price_upper = self.tick_to_price(tick_upper)
            price_mid = np.sqrt(price_lower * price_upper)  # Geometric mean
            
            # Calculate distance from current price
            current_price = self.tick_to_price(current_tick)
            distance_from_current = (price_mid - current_price) / current_price
            
            positions_with_values.append({
                'tick_lower': tick_lower,
                'tick_upper': tick_upper,
                'price_lower': price_lower,
                'price_upper': price_upper,
                'price_mid': price_mid,
                'liquidity': liquidity,
                'amount0': amount0_decimal,
                'amount1': amount1_decimal,
                'usd_value': usd_value,
                'distance_from_current': distance_from_current,
                'is_active': tick_lower <= current_tick <= tick_upper
            })
        
        return pd.DataFrame(positions_with_values)

def load_pools_from_json(v3_filename="pools_uni_v3.json", v4_filename="pools_uni_v4.json"):
    """Load pool data from both V3 and V4 JSON files"""
    all_pools = []
    
    # Load V3 pools
    try:
        with open(v3_filename, 'r') as f:
            v3_data = json.load(f)
        v3_pools = v3_data.get('pools', []) if 'pools' in v3_data else v3_data
        for pool in v3_pools:
            pool['version'] = 'v3'
            all_pools.append(pool)
        st.session_state['log_messages'] = f"Loaded {len(v3_pools)} Uniswap V3 pools"
    except FileNotFoundError:
        st.session_state['log_messages'] = f"Warning: File '{v3_filename}' not found!"
    except json.JSONDecodeError:
        st.session_state['log_messages'] = f"Error: Invalid JSON in '{v3_filename}'!"
    
    # Load V4 pools
    try:
        with open(v4_filename, 'r') as f:
            v4_data = json.load(f)
        v4_pools = v4_data if isinstance(v4_data, list) else v4_data.get('pools', [])
        for pool in v4_pools:
            pool['version'] = 'v4'
            pool['poolAddress'] = pool.get('poolAddress')  # This is actually the pool ID for V4
            all_pools.append(pool)
        st.session_state['log_messages'] = f"Loaded {len(v4_pools)} Uniswap V4 pools"
    except FileNotFoundError:
        st.session_state['log_messages'] = f"Warning: File '{v4_filename}' not found!"
    except json.JSONDecodeError:
        st.session_state['log_messages'] = f"Error: Invalid JSON in '{v4_filename}'!"
    
    return all_pools

def generate_dune_query_v3(pool_address):
    """Generate the Dune SQL query for Uniswap V3 pools"""
    return f"""
-- Uniswap V3 Market Depth Analysis Query
WITH current_positions AS (
  SELECT 
    tickLower as tick_lower,
    tickUpper as tick_upper,
    amount as liquidity,
    evt_tx_hash,
    evt_block_number,
    evt_block_time,
    CAST(amount AS INT256) as liquidity_delta
  FROM uniswap_v3_ethereum.uniswapv3pool_evt_mint m
  WHERE m.contract_address = {pool_address}
  
  UNION ALL
  
  SELECT 
    tickLower as tick_lower,
    tickUpper as tick_upper,
    amount as liquidity,
    evt_tx_hash,
    evt_block_number,
    evt_block_time,
    -CAST(amount AS INT256) as liquidity_delta
  FROM uniswap_v3_ethereum.uniswapv3pool_evt_burn b
  WHERE b.contract_address = {pool_address}
),
net_liquidity AS (
  SELECT 
    tick_lower,
    tick_upper,
    SUM(liquidity_delta) as net_liquidity
  FROM current_positions
  GROUP BY tick_lower, tick_upper
  HAVING SUM(liquidity_delta) > 0
),
current_price AS (
  SELECT 
    sqrtPriceX96 as sqrt_price_x96,
    tick,
    evt_block_number,
    evt_block_time
  FROM uniswap_v3_ethereum.uniswapv3pool_evt_swap s
  WHERE s.contract_address = {pool_address}
  ORDER BY evt_block_number DESC, evt_index DESC
  LIMIT 1
)
SELECT 
  nl.tick_lower,
  nl.tick_upper,
  nl.net_liquidity,
  cp.sqrt_price_x96,
  cp.tick as current_tick,
  cp.evt_block_time as price_timestamp,
  CAST(cp.sqrt_price_x96 AS DOUBLE) / POWER(2, 96) as sqrt_price,
  POWER(CAST(cp.sqrt_price_x96 AS DOUBLE) / POWER(2, 96), 2) as current_price
FROM net_liquidity nl
CROSS JOIN current_price cp
WHERE nl.net_liquidity > 0
ORDER BY nl.tick_lower
"""

def generate_dune_query_v4(pool_id):
    """Generate the Dune SQL query for Uniswap V4 pools"""
    return f"""
-- Uniswap V4 Market Depth Analysis Query
WITH current_positions AS (
  SELECT 
    tickLower as tick_lower,
    tickUpper as tick_upper,
    liquidityDelta as liquidity_delta,
    evt_tx_hash,
    evt_block_number,
    evt_block_time,
    id as pool_id
  FROM uniswap_v4_ethereum.poolmanager_evt_modifyliquidity ml
  WHERE ml.contract_address = 0x000000000004444c5dc75cb358380d2e3de08a90
    AND ml.id = {pool_id}
),
net_liquidity AS (
  SELECT 
    tick_lower,
    tick_upper,
    SUM(liquidity_delta) as net_liquidity
  FROM current_positions
  GROUP BY tick_lower, tick_upper
  HAVING SUM(liquidity_delta) > 0
),
current_price AS (
  SELECT 
    sqrtPriceX96 as sqrt_price_x96,
    tick,
    evt_block_number,
    evt_block_time
  FROM uniswap_v4_ethereum.poolmanager_evt_swap s
  WHERE s.contract_address = 0x000000000004444c5dc75cb358380d2e3de08a90
    AND s.id = {pool_id}
  ORDER BY evt_block_number DESC, evt_index DESC
  LIMIT 1
)
SELECT 
  nl.tick_lower,
  nl.tick_upper,
  nl.net_liquidity,
  cp.sqrt_price_x96,
  cp.tick as current_tick,
  cp.evt_block_time as price_timestamp,
  CAST(cp.sqrt_price_x96 AS DOUBLE) / POWER(2, 96) as sqrt_price,
  POWER(CAST(cp.sqrt_price_x96 AS DOUBLE) / POWER(2, 96), 2) as current_price
FROM net_liquidity nl
CROSS JOIN current_price cp
WHERE nl.net_liquidity > 0
ORDER BY nl.tick_lower
"""

def get_token_price_from_coingecko(coingecko_id, token_symbol):
    """Fetch current token price from CoinGecko API"""
    if not coingecko_id:
        st.session_state['log_messages'] = f"No CoinGecko ID available for {token_symbol}"
        return get_manual_token_price(token_symbol)
    
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if coingecko_id in data and 'usd' in data[coingecko_id]:
            price = data[coingecko_id]['usd']
            st.session_state['log_messages'] = f"Fetched {token_symbol} price from CoinGecko: ${price}"
            return float(price)
        else:
            st.session_state['log_messages'] = f"Price not found for {token_symbol} ({coingecko_id})"
            return get_manual_token_price(token_symbol)
            
    except requests.exceptions.RequestException as e:
        st.session_state['log_messages'] = f"Error fetching price for {token_symbol} from CoinGecko: {e}"
        return get_manual_token_price(token_symbol)
    except (KeyError, ValueError) as e:
        st.session_state['log_messages'] = f"Error parsing price data for {token_symbol}: {e}"
        return get_manual_token_price(token_symbol)

def get_manual_token_price(token_symbol):
    """Fallback to manual price entry with smart defaults"""
    default_prices = {
        'USDC': 1.0,
        'USDT': 1.0,
        'DAI': 1.0,
        'FRAX': 1.0,
        'LUSD': 1.0,
        'BOLD': 1.0,
        'USD0': 1.0,
        'USD0++': 1.0,
        'OUSD': 1.0,
        'WETH': 2600.0,
        'ETH': 2600.0,
        'WBTC': 65000.0,
        'BTC': 65000.0,
        'syrupUSDC': 1.0,
    }
    
    if token_symbol in default_prices:
        default_price = default_prices[token_symbol]
        return default_price
    else:
        return 1.0  # Default fallback price

def plot_market_depth_bars(market_depth, token0_symbol, token1_symbol, version):
    """Plot the market depth as bar chart"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Filter for key price impact levels
    key_levels = [-0.05, -0.02, -0.01, -0.005, -0.001, 0.001, 0.005, 0.01, 0.02, 0.05]
    filtered_data = market_depth[market_depth['pct'].isin(key_levels)]
    
    # Create labels and colors
    labels = [f"{pct*100:+.1f}%" for pct in filtered_data['pct']]
    colors = ['red' if pct < 0 else 'green' for pct in filtered_data['pct']]
    
    bars = ax.bar(labels, filtered_data['marketdepth_usd'], color=colors, alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for bar, value in zip(bars, filtered_data['marketdepth_usd']):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'${value:,.0f}', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('Price Impact (%)')
    ax.set_ylabel('Market Depth (USD)')
    ax.set_title(f'{token0_symbol}/{token1_symbol} Market Depth Profile [Uniswap {version.upper()}]')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig

def plot_active_liquidity_pie(liquidity_df, token0_symbol, token1_symbol, version):
    """Plot active vs inactive liquidity as pie chart"""
    #fig, ax = plt.subplots(figsize=(8, 8))
    fig, ax = plt.subplots(figsize=(2, 2))
    
    active_liquidity = liquidity_df[liquidity_df['is_active']]['usd_value'].sum()
    inactive_liquidity = liquidity_df[~liquidity_df['is_active']]['usd_value'].sum()
    
    sizes = [active_liquidity, inactive_liquidity]
    labels = [f'Active\n${active_liquidity:,.0f}', f'Out of Range\n${inactive_liquidity:,.0f}']
    colors = ['lightgreen', 'lightcoral']
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                                     startangle=90, textprops={'fontsize': 12})
    
    ax.set_title(f'{token0_symbol}/{token1_symbol} Active Liquidity [Uniswap {version.upper()}]', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Make percentage text bold and white
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    # Make labels bold
    for text in texts:
        text.set_fontweight('bold')
        text.set_fontsize(11)
    
    return fig

def plot_liquidity_by_distance(liquidity_df, token0_symbol, token1_symbol, version):
    """Plot liquidity distribution by distance from current price"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create distance bins from -100% to +100% in 10% increments
    distance_bins = np.linspace(-1, 1, 21)
    
    ax.hist(liquidity_df['distance_from_current'], bins=distance_bins, 
            weights=liquidity_df['usd_value'], alpha=0.7, color='skyblue', 
            edgecolor='darkblue', linewidth=0.5)
    
    # Add vertical line at current price (distance = 0)
    ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Current Price')
    
    ax.set_xlabel('Distance from Current Price (%)')
    ax.set_ylabel('Total Liquidity (USD)')
    ax.set_title(f'{token0_symbol}/{token1_symbol} Liquidity by Distance [Uniswap {version.upper()}]')
    
    # Format x-axis as percentages
    ax.set_xticks(np.arange(-1, 1.1, 0.2))
    ax.set_xticklabels([f'{int(x*100)}%' for x in np.arange(-1, 1.1, 0.2)])
    
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig

def analyze_uniswap_pool(selected_pool, dune_api_key):
    """Analyze a selected Uniswap pool"""
    version = selected_pool['version']
    pool_identifier = selected_pool['poolAddress']
    token0 = selected_pool['token0']
    token1 = selected_pool['token1']
    fee_tier = selected_pool['feeTier']
    pool_name = f"{token0['symbol']}/{token1['symbol']}"
    
    st.write(f"### Analyzing {pool_name} [Uniswap {version.upper()}]")
    
    # Get token prices
    token0_price = get_token_price_from_coingecko(token0.get('coingeckoId'), token0['symbol'])
    token1_price = get_token_price_from_coingecko(token1.get('coingeckoId'), token1['symbol'])
    
    # Determine tick spacing
    fee_tier_to_basis_points = {0.001: 1, 0.05: 500, 0.3: 3000, 1.0: 10000}
    fee_basis_points = fee_tier_to_basis_points.get(fee_tier, 3000)
    tick_spacing_map = {1: 1, 500: 10, 3000: 60, 10000: 200}
    tick_spacing = tick_spacing_map.get(fee_basis_points, 60)
    
    # Initialize Dune client
    dune_client = DuneClient(dune_api_key)
    
    # Generate and execute appropriate Dune query
    if version == 'v3':
        query_sql = generate_dune_query_v3(pool_identifier)
    else:  # v4
        query_sql = generate_dune_query_v4(pool_identifier)
    
    with st.spinner(f"Querying {pool_name} liquidity data from Dune Analytics..."):
        execution_id = dune_client.create_and_execute_query(
            query_sql, 
            f"{pool_name} {version.upper()} Market Depth Analysis"
        )
        
        if execution_id is None:
            st.error("Failed to execute Dune query. Please check your API key and try again.")
            return None, None, None
        
        results = dune_client.wait_for_completion(execution_id, max_wait_time=300)
        
        if results is None:
            st.error("Failed to get query results")
            return None, None, None
    
    # Process results
    if 'result' in results and 'rows' in results['result']:
        rows = results['result']['rows']
        
        if not rows:
            st.warning("No liquidity positions found for this pool.")
            return None, None, None
        
        # Convert to DataFrame
        df = pd.DataFrame(rows)
        
        # Ensure numeric types
        df['tick_lower'] = pd.to_numeric(df['tick_lower'], errors='coerce')
        df['tick_upper'] = pd.to_numeric(df['tick_upper'], errors='coerce')
        df['net_liquidity'] = pd.to_numeric(df['net_liquidity'], errors='coerce')
        df['sqrt_price_x96'] = pd.to_numeric(df['sqrt_price_x96'], errors='coerce')
        df['current_tick'] = pd.to_numeric(df['current_tick'], errors='coerce')
        
        # Remove NaN values
        df = df.dropna()
        
        if len(df) == 0:
            st.warning("No valid liquidity positions after data cleaning.")
            return None, None, None
        
        # Extract current state
        current_tick = int(df['current_tick'].iloc[0])
        current_sqrt_price_x96 = int(df['sqrt_price_x96'].iloc[0])
        current_sqrt_price = float(current_sqrt_price_x96) / (2 ** 96)
        
        # Initialize market depth calculator
        calculator = MarketDepthCalculator(
            token0['symbol'], token1['symbol'],
            token0['decimals'], token1['decimals'],
            token0_price, token1_price,
            tick_spacing
        )
        
        # Calculate TVL
        tvl = calculator.calculate_tvl(df, current_tick, current_sqrt_price)
        
        # Prepare liquidity distribution
        liquidity_df = calculator.prepare_liquidity_distribution(df, current_tick, current_sqrt_price, tick_spacing)
        
        # Define percentage changes for market depth calculation
        pctchg = [
            -0.10, -0.06, -0.05, -0.04, -0.02, -0.01, -0.0075, -0.005, -0.004, 
            -0.003, -0.002, -0.001, -0.00075, -0.0005, -0.00025,
            0.00025, 0.0005, 0.00075, 0.001, 0.002, 0.003, 0.004, 0.005, 
            0.0075, 0.01, 0.02, 0.04, 0.05, 0.06, 0.10
        ]
        
        # Calculate market depth
        market_depth = calculator.pipe_market_depth(df, current_tick, current_sqrt_price_x96, pctchg)
        
        return market_depth, liquidity_df, current_tick, tvl
    else:
        st.error(f"Unable to retrieve data for {pool_name}")
        return None, None, None, None

def analyze_curve_pool(pair_name):
    """Analyze a Curve pool"""
    fetcher = CurveMarketDepthFetcher()
    
    # Load pools configuration
    config_loaded = fetcher.load_pools_config("curve_pools_config.json")
    
    if not config_loaded:
        st.error("Failed to load Curve pools configuration")
        return None, None
    
    pool_config = fetcher.get_pool_by_pair_name(pair_name)
    if not pool_config:
        st.error(f"Pool with pair name '{pair_name}' not found")
        return None, None
    
    # Fetch data
    data = fetcher.fetch_market_depth(
        pool_config['pool_address'],
        pool_config['token1_address'],
        pool_config['token2_address']
    )
    
    if not data:
        st.error("Failed to fetch data")
        return None, None
    
    try:
        # Parse data
        bid_data, ask_data, spot_prices = fetcher.parse_market_depth_data(data)
        return bid_data, ask_data, spot_prices, pool_config['pair_name']
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None, None, None, None

def plot_curve_market_depth(bid_data, ask_data, spot_prices, pair_name):
    """Plot Curve market depth"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Prepare data for plotting
    if bid_data:
        bid_impacts, bid_liquidity = zip(*bid_data)
        # Convert to negative price impacts for bids (left side)
        bid_impacts = [-x for x in bid_impacts]
        ax.bar(bid_impacts, [x/1e6 for x in bid_liquidity], 
              width=0.002, color='#4169E1', alpha=0.8, label='Bids')
    
    if ask_data:
        ask_impacts, ask_liquidity = zip(*ask_data)
        ax.bar(ask_impacts, [x/1e6 for x in ask_liquidity], 
              width=0.002, color='#FF1493', alpha=0.8, label='Asks')
    
    # Add spot price line
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.7, linewidth=1)
    
    # Formatting
    ax.set_xlabel('Price Impact (%)', fontsize=12)
    ax.set_ylabel('Liquidity (M USD)', fontsize=12)
    ax.set_title(f'Market Depth - {pair_name}', fontsize=14, fontweight='bold')
    
    # Format x-axis to show percentages
    ax.set_xlim(-0.05, 0.05)
    x_ticks = np.arange(-0.04, 0.05, 0.01)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f'{x:.1%}' for x in x_ticks])
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add spot price annotation
    ax.text(0.02, ax.get_ylim()[1] * 0.9, 
           f'Spot price: {spot_prices[0]:.4f}', 
           fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
    
    # Add legend
    ax.legend()
    
    plt.tight_layout()
    return fig

# def main():
#     """Main Streamlit app function"""
#     st.title("DeFi Market Depth Analyzer")
#     st.markdown("""
#     Analyze market depth and liquidity distribution for Curve and Uniswap V3/V4 pools.
#     """)
    
#     # Initialize session state
#     if 'log_messages' not in st.session_state:
#         st.session_state['log_messages'] = ""
#     if 'dune_message' not in st.session_state:
#         st.session_state['dune_message'] = ""
    
#     # Create tabs for different protocols
#     tab1, tab2 = st.tabs(["Uniswap V3/V4", "Curve"])
    
#     with tab1:
#         st.header("Uniswap V3/V4 Market Depth Analysis")
        
#         # Load pools
#         pools = load_pools_from_json()
        
#         if not pools:
#             st.error("No pools available. Please check your JSON files.")
#             return
        
#         # Split into V3 and V4 pools
#         v3_pools = [p for p in pools if p.get('version') == 'v3']
#         v4_pools = [p for p in pools if p.get('version') == 'v4']
        
#         # Create columns for pool selection and settings
#         col1, col2 = st.columns([3, 1])
        
#         with col1:
#             # Pool selection
#             pool_options = []
#             if v3_pools:
#                 pool_options.append("🦄 Uniswap V3 Pools")
#                 for i, pool in enumerate(v3_pools, 1):
#                     token0 = pool['token0']['symbol']
#                     token1 = pool['token1']['symbol']
#                     fee_tier = pool['feeTier']
#                     pool_options.append(f"{i}. {token0}/{token1} (Fee: {fee_tier}%) [V3]")
            
#             if v4_pools:
#                 pool_options.append("\n🦄 Uniswap V4 Pools")
#                 start_idx = len(v3_pools) + 1
#                 for i, pool in enumerate(v4_pools, start_idx):
#                     token0 = pool['token0']['symbol']
#                     token1 = pool['token1']['symbol']
#                     fee_tier = pool['feeTier']
#                     pool_options.append(f"{i}. {token0}/{token1} (Fee: {fee_tier}%) [V4]")
            
#             selected_option = st.selectbox(
#                 "Select a pool to analyze:",
#                 pool_options,
#                 index=0
#             )
            
#             # Parse selection
#             try:
#                 if selected_option.startswith(("🦄", "\n🦄")):
#                     st.warning("Please select a specific pool from the list")
#                     selected_pool = None
#                 else:
#                     # Extract pool index from selection (e.g., "1. ETH/USDC" -> 0)
#                     pool_index = int(selected_option.split('.')[0]) - 1
#                     selected_pool = pools[pool_index]
#             except:
#                 selected_pool = None
        
#         with col2:
#             # Dune API key input
#             dune_api_key = st.text_input(
#                 "Dune API Key (optional)",
#                 type="password",
#                 help="Required for Uniswap analysis. Get one at https://dune.com/settings/api"
#             )
        
#         if selected_pool:
#             # Display pool info
#             version = selected_pool['version']
#             token0 = selected_pool['token0']
#             token1 = selected_pool['token1']
            
#             st.subheader(f"{token0['symbol']}/{token1['symbol']} [Uniswap {version.upper()}]")
            
#             if version == 'v3':
#                 st.caption(f"Pool Address: {selected_pool['poolAddress']}")
#             else:
#                 st.caption(f"Pool ID: {selected_pool['poolAddress']}")
            
#             st.caption(f"Fee Tier: {selected_pool['feeTier']}%")
            
#             # Analyze button
#             if st.button("Analyze Pool", key="analyze_uniswap"):
#                 if not dune_api_key:
#                     st.warning("Please enter a Dune API key to analyze Uniswap pools")
#                 else:
#                     with st.spinner("Analyzing pool..."):
#                         market_depth, liquidity_df, current_tick, tvl = analyze_uniswap_pool(selected_pool, dune_api_key)
                        
#                         if market_depth is not None and liquidity_df is not None:
#                             # Display metrics
#                             col1, col2, col3 = st.columns(3)
                            
#                             with col1:
#                                 st.metric("Total Value Locked", f"${tvl['total_value_usd']:,.2f}")
#                                 st.metric(f"{token0['symbol']} Amount", f"{tvl['token0_amount']:,.4f}")                            
#                             with col2:
#                                 active_liquidity = liquidity_df[liquidity_df['is_active']]['usd_value'].sum()
#                                 efficiency = (active_liquidity / liquidity_df['usd_value'].sum()) * 100
#                                 st.metric("Active Liquidity", f"${active_liquidity:,.2f}")
#                                 st.metric(f"{token1['symbol']} Amount", f"{tvl['token1_amount']:,.4f}")
                            
#                             with col3:
#                                 st.metric("Liquidity Efficiency", f"{efficiency:.1f}%")
#                                 if tvl['token0_amount'] > 0:
#                                     current_price = tvl['token1_amount'] / tvl['token0_amount']
#                                     st.metric("Current Price", f"1 {token0['symbol']} = {current_price:.6f} {token1['symbol']}")
                            
#                             # Display charts in columns
#                             col1, col2 = st.columns(2)
                            
#                             with col1:
#                                 st.subheader("Market Depth Profile")
#                                 st.pyplot(plot_market_depth_bars(market_depth, token0['symbol'], token1['symbol'], version))
                                
#                             with col2:
#                                 st.subheader("Active Liquidity Distribution")
#                                 st.pyplot(plot_active_liquidity_pie(liquidity_df, token0['symbol'], token1['symbol'], version))
                            
#                             st.subheader("Liquidity by Distance from Current Price")
#                             st.pyplot(plot_liquidity_by_distance(liquidity_df, token0['symbol'], token1['symbol'], version))
                            
#                             # Show data tables
#                             with st.expander("View Market Depth Data"):
#                                 st.dataframe(market_depth)
                            
#                             with st.expander("View Liquidity Distribution Data"):
#                                 st.dataframe(liquidity_df)
    
#     with tab2:
#         st.header("Curve Market Depth Analysis")
        
#         # Initialize Curve fetcher
#         fetcher = CurveMarketDepthFetcher()
        
#         # Load pools configuration
#         config_loaded = fetcher.load_pools_config("curve_pools_config.json")
        
#         if config_loaded:
#             # Get available pairs
#             pairs = fetcher.list_available_pairs()
            
#             if pairs:
#                 # Pair selection
#                 selected_pair = st.selectbox(
#                     "Select a Curve pool to analyze:",
#                     pairs,
#                     index=0
#                 )
                
#                 # Analyze button
#                 if st.button("Analyze Pool", key="analyze_curve"):
#                     with st.spinner(f"Analyzing {selected_pair}..."):
#                         bid_data, ask_data, spot_prices, pair_name = analyze_curve_pool(selected_pair)
                        
#                         if bid_data is not None and ask_data is not None:
#                             # Display metrics
#                             col1, col2 = st.columns(2)
                            
#                             with col1:
#                                 total_bid_liquidity = sum([x[1] for x in bid_data]) / 1e6
#                                 st.metric("Total Bid Liquidity", f"${total_bid_liquidity:,.2f}M")
                            
#                             with col2:
#                                 total_ask_liquidity = sum([x[1] for x in ask_data]) / 1e6
#                                 st.metric("Total Ask Liquidity", f"${total_ask_liquidity:,.2f}M")
                            
#                             st.metric("Spot Price", f"{spot_prices[0]:.6f}")
                            
#                             # Display chart
#                             st.subheader("Market Depth")
#                             st.pyplot(plot_curve_market_depth(bid_data, ask_data, spot_prices, pair_name))
                            
#                             # Show data
#                             with st.expander("View Bid Data"):
#                                 bid_df = pd.DataFrame(bid_data, columns=['Price Impact', 'Liquidity'])
#                                 st.dataframe(bid_df)
                            
#                             with st.expander("View Ask Data"):
#                                 ask_df = pd.DataFrame(ask_data, columns=['Price Impact', 'Liquidity'])
#                                 st.dataframe(ask_df)
#             else:
#                 st.warning("No Curve pools found in configuration")
#         else:
#             st.error("Failed to load Curve pools configuration")
    
#     # Display logs in sidebar
#     with st.sidebar:
#         st.header("Settings & Logs")
        
#         # API keys
#         st.subheader("API Keys")
#         dune_api_key = st.text_input(
#             "Dune API Key",
#             type="password",
#             help="Required for Uniswap analysis. Get one at https://dune.com/settings/api"
#         )
        
#         # Logs
#         st.subheader("Log Messages")
#         if st.session_state['log_messages']:
#             st.text(st.session_state['log_messages'])
        
#         if st.session_state['dune_message']:
#             st.text(st.session_state['dune_message'])
        
#         # About section
#         st.subheader("About")
#         st.markdown("""
#         This app analyzes market depth and liquidity distribution for:
#         - Uniswap V3/V4 pools (using Dune Analytics)
#         - Curve pools (using DeFiRisk API)
        
#         **Note:** For Uniswap analysis, a Dune API key is required.
#         """)

# if __name__ == "__main__":
#     main()

def main():
    """Main Streamlit app function"""
    st.title("DeFi Market Depth Analyzer")
    st.markdown("""
    Analyze market depth and liquidity distribution for Curve and Uniswap V3/V4 pools.
    """)

    # Initialize session state
    if 'log_messages' not in st.session_state:
        st.session_state['log_messages'] = ""
    if 'dune_message' not in st.session_state:
        st.session_state['dune_message'] = ""

    # Create tabs for different protocols
    tab1, tab2 = st.tabs(["Uniswap V3/V4", "Curve"])

    with tab1:
        st.header("Uniswap V3/V4 Market Depth Analysis")

        # Load pools
        pools = load_pools_from_json()

        if not pools:
            st.error("No pools available. Please check your JSON files.")
            return

        # Split into V3 and V4 pools
        v3_pools = [p for p in pools if p.get('version') == 'v3']
        v4_pools = [p for p in pools if p.get('version') == 'v4']

        # Create columns for pool selection and settings
        col1, col2 = st.columns([3, 1])

        with col1:
            # Pool selection
            pool_options = []
            if v3_pools:
                pool_options.append("🦄 Uniswap V3 Pools")
                for i, pool in enumerate(v3_pools, 1):
                    token0 = pool['token0']['symbol']
                    token1 = pool['token1']['symbol']
                    fee_tier = pool['feeTier']
                    pool_options.append(f"{i}. {token0}/{token1} (Fee: {fee_tier}%) [V3]")

            if v4_pools:
                pool_options.append("\n🦄 Uniswap V4 Pools")
                start_idx = len(v3_pools) + 1
                for i, pool in enumerate(v4_pools, start_idx):
                    token0 = pool['token0']['symbol']
                    token1 = pool['token1']['symbol']
                    fee_tier = pool['feeTier']
                    pool_options.append(f"{i}. {token0}/{token1} (Fee: {fee_tier}%) [V4]")

            selected_option = st.selectbox(
                "Select a pool to analyze:",
                pool_options,
                index=0
            )

            # Parse selection
            try:
                if selected_option.startswith(("🦄", "\n🦄")):
                    st.warning("Please select a specific pool from the list")
                    selected_pool = None
                else:
                    # Extract pool index from selection (e.g., "1. ETH/USDC" -> 0)
                    pool_index = int(selected_option.split('.')[0]) - 1
                    selected_pool = pools[pool_index]
            except:
                selected_pool = None

        with col2:
            # Dune API key input
            dune_api_key = st.text_input(
                "Dune API Key (optional)",
                type="password",
                help="Required for Uniswap analysis. Get one at https://dune.com/settings/api"
            )

        if selected_pool:
            # Display pool info
            version = selected_pool['version']
            token0 = selected_pool['token0']
            token1 = selected_pool['token1']

            st.subheader(f"{token0['symbol']}/{token1['symbol']} [Uniswap {version.upper()}]")

            if version == 'v3':
                st.caption(f"Pool Address: {selected_pool['poolAddress']}")
            else:
                st.caption(f"Pool ID: {selected_pool['poolAddress']}")

            st.caption(f"Fee Tier: {selected_pool['feeTier']}%")

            # Analyze button
            if st.button("Analyze Pool", key="analyze_uniswap"):
                if not dune_api_key:
                    st.warning("Please enter a Dune API key to analyze Uniswap pools")
                else:
                    with st.spinner("Analyzing pool..."):
                        market_depth, liquidity_df, current_tick, tvl = analyze_uniswap_pool(selected_pool, dune_api_key)

                        if market_depth is not None and liquidity_df is not None:
                            # Display metrics
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("Total Value Locked", f"${tvl['total_value_usd']:,.2f}")
                                st.metric(f"{token0['symbol']} Amount", f"{tvl['token0_amount']:,.4f}")
                            with col2:
                                active_liquidity = liquidity_df[liquidity_df['is_active']]['usd_value'].sum()
                                efficiency = (active_liquidity / liquidity_df['usd_value'].sum()) * 100
                                st.metric("Active Liquidity", f"${active_liquidity:,.2f}")
                                st.metric(f"{token1['symbol']} Amount", f"{tvl['token1_amount']:,.4f}")

                            with col3:
                                st.metric("Liquidity Efficiency", f"{efficiency:.1f}%")
                                if tvl['token0_amount'] > 0:
                                    current_price = tvl['token1_amount'] / tvl['token0_amount']
                                    st.metric("Current Price", f"1 {token0['symbol']} = {current_price:.6f} {token1['symbol']}")

                            # Display charts sequentially
                            st.subheader("Market Depth Profile")
                            st.pyplot(plot_market_depth_bars(market_depth, token0['symbol'], token1['symbol'], version))

                            st.subheader("Active Liquidity Distribution")
                            st.pyplot(plot_active_liquidity_pie(liquidity_df, token0['symbol'], token1['symbol'], version))

                            st.subheader("Liquidity by Distance from Current Price")
                            st.pyplot(plot_liquidity_by_distance(liquidity_df, token0['symbol'], token1['symbol'], version))

                            # Show data tables
                            with st.expander("View Market Depth Data"):
                                st.dataframe(market_depth)

                            with st.expander("View Liquidity Distribution Data"):
                                st.dataframe(liquidity_df)

    with tab2:
        st.header("Curve Market Depth Analysis")

        # Initialize Curve fetcher
        fetcher = CurveMarketDepthFetcher()

        # Load pools configuration
        config_loaded = fetcher.load_pools_config("curve_pools_config.json")

        if config_loaded:
            # Get available pairs
            pairs = fetcher.list_available_pairs()

            if pairs:
                # Pair selection
                selected_pair = st.selectbox(
                    "Select a Curve pool to analyze:",
                    pairs,
                    index=0
                )

                # Analyze button
                if st.button("Analyze Pool", key="analyze_curve"):
                    with st.spinner(f"Analyzing {selected_pair}..."):
                        bid_data, ask_data, spot_prices, pair_name = analyze_curve_pool(selected_pair)

                        if bid_data is not None and ask_data is not None:
                            # Display metrics
                            col1, col2 = st.columns(2)

                            with col1:
                                total_bid_liquidity = sum([x[1] for x in bid_data]) / 1e6
                                st.metric("Total Bid Liquidity", f"${total_bid_liquidity:,.2f}M")

                            with col2:
                                total_ask_liquidity = sum([x[1] for x in ask_data]) / 1e6
                                st.metric("Total Ask Liquidity", f"${total_ask_liquidity:,.2f}M")

                            st.metric("Spot Price", f"{spot_prices[0]:.6f}")

                            # Display chart
                            st.subheader("Market Depth")
                            st.pyplot(plot_curve_market_depth(bid_data, ask_data, spot_prices, pair_name))

                            # Show data
                            with st.expander("View Bid Data"):
                                bid_df = pd.DataFrame(bid_data, columns=['Price Impact', 'Liquidity'])
                                st.dataframe(bid_df)

                            with st.expander("View Ask Data"):
                                ask_df = pd.DataFrame(ask_data, columns=['Price Impact', 'Liquidity'])
                                st.dataframe(ask_df)
            else:
                st.warning("No Curve pools found in configuration")
        else:
            st.error("Failed to load Curve pools configuration")

    # Display logs in sidebar
    with st.sidebar:
        st.header("Settings & Logs")

        # API keys
        st.subheader("API Keys")
        dune_api_key = st.text_input(
            "Dune API Key",
            type="password",
            help="Required for Uniswap analysis. Get one at https://dune.com/settings/api"
        )

        # Logs
        st.subheader("Log Messages")
        if st.session_state['log_messages']:
            st.text(st.session_state['log_messages'])

        if st.session_state['dune_message']:
            st.text(st.session_state['dune_message'])

        # About section
        st.subheader("About")
        st.markdown("""
        This app analyzes market depth and liquidity distribution for:
        - Uniswap V3/V4 pools (using Dune Analytics)
        - Curve pools (using DeFiRisk API)

        **Note:** For Uniswap analysis, a Dune API key is required.
        """)

if __name__ == "__main__":
    main()

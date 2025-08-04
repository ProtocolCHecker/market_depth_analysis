import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, List, Optional, Dict
import os
import time
import random

class MarketDepthFetcher:
    """
    A generic class to fetch and visualize market depth data from DeFiRisk API
    """
    
    def __init__(self, base_url: str = "https://services.defirisk.sentora.com/metric/ethereum/curve_v2/market_depth"):
        self.base_url = base_url
        self.pools_config = None
        # Add headers to mimic browser requests
        # self.headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        #     'Accept': 'application/json, text/plain, */*',
        #     'Accept-Language': 'en-US,en;q=0.9',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Connection': 'keep-alive',
        #     'Cache-Control': 'no-cache',
        #     'Pragma': 'no-cache'}
    
    def load_pools_config(self, config_path: str = "pools_config.json") -> Dict:
        """
        Load pools configuration from JSON file
        
        Args:
            config_path: Path to the JSON configuration file
            
        Returns:
            Dictionary containing pools configuration
        """
        try:
            with open(config_path, 'r') as f:
                self.pools_config = json.load(f)
            return self.pools_config
        except FileNotFoundError:
            print(f"Configuration file {config_path} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON configuration: {e}")
            return {}
    
    def get_pool_by_pair_name(self, pair_name: str) -> Optional[Dict]:
        """
        Get pool configuration by pair name
        
        Args:
            pair_name: The trading pair name (e.g., "lvlUSD/USDC")
            
        Returns:
            Pool configuration dictionary or None if not found
        """
        if not self.pools_config:
            print("No pools configuration loaded. Please call load_pools_config() first.")
            return None
        
        for pool in self.pools_config.get('pools', []):
            if pool['pair_name'].lower() == pair_name.lower():
                return pool
        
        print(f"Pool with pair name '{pair_name}' not found")
        return None
    
    def list_available_pairs(self) -> List[str]:
        """
        List all available trading pairs from the configuration
        
        Returns:
            List of pair names
        """
        if not self.pools_config:
            return []
        
        return [pool['pair_name'] for pool in self.pools_config.get('pools', [])]
    
    def construct_url(self, pool_address: str, token1_address: str, token2_address: str) -> str:
        """
        Construct the API URL from pool and token addresses
        
        Args:
            pool_address: The liquidity pool contract address
            token1_address: First token contract address
            token2_address: Second token contract address
            
        Returns:
            Complete API URL string
        """
        # Convert all addresses to lowercase - this is the key fix!
        pool_address = pool_address.lower()
        token1_address = token1_address.lower()
        token2_address = token2_address.lower()
        
        return f"{self.base_url}/{pool_address}/{token1_address}/{token2_address}"
    
    def fetch_market_depth(self, pool_address: str, token1_address: str, token2_address: str, 
                          max_retries: int = 3, retry_delay: float = 1.0) -> Optional[dict]:
        """
        Fetch market depth data from the API with retry logic and better error handling
        
        Args:
            pool_address: The liquidity pool contract address
            token1_address: First token contract address
            token2_address: Second token contract address
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            JSON response as dictionary or None if request fails
        """
        url = self.construct_url(pool_address, token1_address, token2_address)
        
        for attempt in range(max_retries):
            try:
                print(f"Attempting to fetch data (attempt {attempt + 1}/{max_retries})...")
                print(f"URL: {url}")
                
                # Add a small random delay to avoid rate limiting
                if attempt > 0:
                    delay = retry_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                    print(f"Waiting {delay:.2f} seconds before retry...")
                    time.sleep(delay)
                
                #response = requests.get(url, headers=self.headers, timeout=30)
                response = requests.get(url, timeout=30)
                
                # Print response details for debugging
                print(f"Response status code: {response.status_code}")
                #print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 500:
                    print(f"Server error (500) - this might be a temporary issue with the API")
                    if attempt < max_retries - 1:
                        continue
                elif response.status_code == 429:
                    print(f"Rate limited (429) - waiting longer before retry")
                    time.sleep(5)
                    if attempt < max_retries - 1:
                        continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout as e:
                print(f"Request timeout on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response on attempt {attempt + 1}: {e}")
                print(f"Response content: {response.text[:500]}...")
                if attempt < max_retries - 1:
                    continue
        
        print(f"All {max_retries} attempts failed")
        return None
    
    def parse_market_depth_data(self, data: dict) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]], Tuple[float, float]]:
        """
        Parse the market depth data from API response
        
        Args:
            data: JSON response from API
            
        Returns:
            Tuple containing (bid_data, ask_data, spot_prices)
        """
        if not data or 'metric' not in data:
            raise ValueError("Invalid data format")
        
        metric = data['metric']
        
        # Extract bid and ask data
        bid_data = [(point[0], point[1]) for point in metric[0] if point[1] > 0]
        ask_data = [(point[0], point[1]) for point in metric[1] if point[1] > 0]
        
        # Extract spot prices
        spot_prices = (float(metric[2][0][0]), float(metric[2][0][1]))
        
        return bid_data, ask_data, spot_prices
    
    def plot_market_depth(self, bid_data: List[Tuple[float, float]], ask_data: List[Tuple[float, float]], 
                         spot_prices: Tuple[float, float], pair_name: str = "Token Pair") -> None:
        """
        Create a market depth visualization similar to the provided screenshot
        
        Args:
            bid_data: List of (price_impact, liquidity) tuples for bids
            ask_data: List of (price_impact, liquidity) tuples for asks
            spot_prices: Tuple of (price1, price2) spot prices
            pair_name: Name of the trading pair for the title
        """
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
        plt.show()
    
    def run_complete_analysis(self, pool_address: str, token1_address: str, token2_address: str, 
                            pair_name: str = "Token Pair") -> None:
        """
        Complete workflow: fetch data, parse it, and create visualization
        
        Args:
            pool_address: The liquidity pool contract address
            token1_address: First token contract address
            token2_address: Second token contract address
            pair_name: Name of the trading pair for display
        """
        print(f"Fetching market depth data for {pair_name}...")
        
        # Fetch data with retry logic
        data = self.fetch_market_depth(pool_address, token1_address, token2_address)
        if not data:
            print("Failed to fetch data after all retry attempts")
            return
        
        print("Data fetched successfully!")
        print(f"Last metric date: {data.get('lastMetricDate', 'N/A')}")
        
        try:
            # Parse data
            bid_data, ask_data, spot_prices = self.parse_market_depth_data(data)
            
            print(f"Parsed {len(bid_data)} bid levels and {len(ask_data)} ask levels")
            print(f"Spot prices: {spot_prices[0]:.6f} / {spot_prices[1]:.6f}")
            
            # Create visualization
            self.plot_market_depth(bid_data, ask_data, spot_prices, pair_name)
            
        except Exception as e:
            print(f"Error processing data: {e}")
    
    def analyze_pair_by_name(self, pair_name: str) -> None:
        """
        Analyze a trading pair by its name using the loaded configuration
        
        Args:
            pair_name: Name of the trading pair (e.g., "lvlUSD/USDC")
        """
        pool_config = self.get_pool_by_pair_name(pair_name)
        if not pool_config:
            return
        
        self.run_complete_analysis(
            pool_address=pool_config['pool_address'],
            token1_address=pool_config['token1_address'],
            token2_address=pool_config['token2_address'],
            pair_name=pool_config['pair_name']
        )
    
    def analyze_all_pairs(self) -> None:
        """
        Analyze all trading pairs from the configuration
        """
        if not self.pools_config:
            print("No pools configuration loaded. Please call load_pools_config() first.")
            return
        
        for pool in self.pools_config.get('pools', []):
            print(f"\n{'='*50}")
            self.run_complete_analysis(
                pool_address=pool['pool_address'],
                token1_address=pool['token1_address'],
                token2_address=pool['token2_address'],
                pair_name=pool['pair_name']
            )
            
            # Ask user if they want to continue to next pair
            user_input = input("\nPress Enter to continue to next pair, or 'q' to quit: ")
            if user_input.lower() == 'q':
                break

# Example usage
if __name__ == "__main__":
    # Initialize the fetcher
    fetcher = MarketDepthFetcher()
    
    # Load pools configuration
    config_loaded = fetcher.load_pools_config("curve_pools_config.json")
    
    if config_loaded:
        # Show available pairs
        print("Available trading pairs:")
        pairs = fetcher.list_available_pairs()
        for i, pair in enumerate(pairs, 1):
            print(f"{i}. {pair}")
        
        print("\n" + "="*50)
        
        # Example 1: Analyze a specific pair by name
        fetcher.analyze_pair_by_name("USD0/USD0++")
        
        # Example 2: Analyze a different pair
        # fetcher.analyze_pair_by_name("lvlUSD/USDC")
        
        # Example 3: Analyze all pairs (uncomment to run)
        # fetcher.analyze_all_pairs()
    
    else:
        # Fallback to manual configuration
        print("Using manual configuration...")
        pool_address = "0x1220868672d5b10f3e1cb9ab519e4d0b08545ea4"
        token1_address = "0x7c1156e515aa1a2e851674120074968c905aaf37"
        token2_address = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
        
        fetcher.run_complete_analysis(
            pool_address=pool_address,
            token1_address=token1_address, 
            token2_address=token2_address,
            pair_name="lvlUSD/USDC"
        )


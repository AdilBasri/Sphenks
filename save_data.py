# save_data.py
import json
import os

class SaveManager:
    """Manages save/load operations for player progression data."""
    
    def __init__(self, save_file='save.json'):
        self.save_file = save_file
        self.data = self._load_or_create()
    
    def _get_default_data(self):
        """Returns the default save data structure."""
        return {
            'total_debt': 1000000,
            'debt_paid': 0,
            'unlocked_items': [],
            'settings': {
                'fullscreen': False,
                'volume': 0.5,
                'language': 'EN'
            }
        }
    
    def _load_or_create(self):
        """Load existing save file or create new one with defaults."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                # Ensure all required keys exist (for backwards compatibility)
                default = self._get_default_data()
                for key in default:
                    if key not in data:
                        data[key] = default[key]
                return data
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, return defaults
                return self._get_default_data()
        else:
            # Create new save file
            default = self._get_default_data()
            self.save_data(default)
            return default
    
    def get_data(self):
        """Returns the current save data."""
        return self.data
    
    def save_data(self, data=None):
        """Save data to disk. If no data provided, saves current state."""
        if data is not None:
            self.data = data
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.data, f, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")
    
    def pay_debt(self, amount):
        """
        Pay down debt by the given amount.
        
        Args:
            amount: The amount to pay towards the debt
            
        Returns:
            dict: Updated debt information {'debt_paid', 'remaining_debt'}
        """
        if amount > 0:
            self.data['debt_paid'] += amount
            self.save_data()
        
        remaining = max(0, self.data['total_debt'] - self.data['debt_paid'])
        
        return {
            'debt_paid': self.data['debt_paid'],
            'remaining_debt': remaining
        }
    
    def get_remaining_debt(self):
        """Returns how much debt is still unpaid."""
        return max(0, self.data['total_debt'] - self.data['debt_paid'])
    
    def unlock_item(self, item_id):
        """Add an item to the unlocked items list."""
        if item_id not in self.data['unlocked_items']:
            self.data['unlocked_items'].append(item_id)
            self.save_data()
    
    def is_unlocked(self, item_id):
        """Check if an item is unlocked."""
        return item_id in self.data['unlocked_items']
    
    def update_setting(self, key, value):
        """Update a specific setting."""
        if key in self.data['settings']:
            self.data['settings'][key] = value
            self.save_data()

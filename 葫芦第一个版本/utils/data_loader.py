# utils/data_loader.py
import json
import os

class DataLoader:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), '../data')
        
    def load_echo_data(self):
        """加载声骸套装数据"""
        with open(os.path.join(self.data_path, 'echo.json'), 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_cost_rules(self):
        """加载COST词条规则"""
        with open(os.path.join(self.data_path, 'cost.json'), 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_default_rules(self):
        """加载默认锁定/弃置规则"""
        with open(os.path.join(self.data_path, 'default_rules.json'), 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_all_cost_attrs(self):
        """获取所有cost类型的全部词条"""
        cost_data = self.load_cost_rules()
        return {
            "cost1": cost_data["cost1"],
            "cost3": cost_data["cost3"],
            "cost4": cost_data["cost4"],
            "attr": cost_data["attr"]
        }
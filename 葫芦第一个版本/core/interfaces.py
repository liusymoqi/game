# [file name]: core/interfaces.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class IEchoSorter(ABC):
    """声骸整理核心操作接口"""
    @abstractmethod
    def start_sorting(self, rules: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def pause_sorting(self) -> None:
        pass

class IGameController(ABC):
    """游戏控制基础接口"""
    @abstractmethod
    def activate_window(self) -> bool:
        pass
    
    @abstractmethod
    def send_key(self, key: str) -> bool:
        pass
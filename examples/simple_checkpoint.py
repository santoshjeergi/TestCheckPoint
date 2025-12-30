"""
Simple Checkpoint Example in Python

This example demonstrates a basic checkpoint system for a simple game.
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional


class GameState:
    """Represents the state of a game"""
    
    def __init__(self):
        self.player_name = ""
        self.level = 1
        self.score = 0
        self.health = 100
        self.inventory = []
        self.position = {"x": 0, "y": 0}
    
    def to_dict(self) -> Dict:
        """Convert game state to dictionary"""
        return {
            "player_name": self.player_name,
            "level": self.level,
            "score": self.score,
            "health": self.health,
            "inventory": self.inventory,
            "position": self.position
        }
    
    def from_dict(self, data: Dict):
        """Load game state from dictionary"""
        self.player_name = data.get("player_name", "")
        self.level = data.get("level", 1)
        self.score = data.get("score", 0)
        self.health = data.get("health", 100)
        self.inventory = data.get("inventory", [])
        self.position = data.get("position", {"x": 0, "y": 0})


class CheckpointManager:
    """Manages game checkpoints"""
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def save_checkpoint(self, game_state: GameState, slot: int = 1) -> bool:
        """
        Save game state to a checkpoint
        
        Args:
            game_state: Current game state to save
            slot: Save slot number (1-3)
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            checkpoint_data = {
                "game_state": game_state.to_dict(),
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            filepath = os.path.join(self.save_dir, f"save_slot_{slot}.json")
            
            with open(filepath, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            print(f"✓ Game saved to slot {slot}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to save game: {e}")
            return False
    
    def load_checkpoint(self, slot: int = 1) -> Optional[GameState]:
        """
        Load game state from a checkpoint
        
        Args:
            slot: Save slot number to load (1-3)
        
        Returns:
            GameState if successful, None otherwise
        """
        try:
            filepath = os.path.join(self.save_dir, f"save_slot_{slot}.json")
            
            if not os.path.exists(filepath):
                print(f"✗ No save found in slot {slot}")
                return None
            
            with open(filepath, 'r') as f:
                checkpoint_data = json.load(f)
            
            game_state = GameState()
            game_state.from_dict(checkpoint_data["game_state"])
            
            timestamp = checkpoint_data.get("timestamp", "Unknown")
            print(f"✓ Game loaded from slot {slot} (saved: {timestamp})")
            
            return game_state
            
        except Exception as e:
            print(f"✗ Failed to load game: {e}")
            return None
    
    def list_saves(self):
        """List all available save slots"""
        print("\n=== Available Saves ===")
        
        for slot in range(1, 4):
            filepath = os.path.join(self.save_dir, f"save_slot_{slot}.json")
            
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    game_data = data["game_state"]
                    timestamp = data.get("timestamp", "Unknown")
                    
                    print(f"Slot {slot}: {game_data['player_name']} - "
                          f"Level {game_data['level']}, "
                          f"Score {game_data['score']}")
                    print(f"         Saved: {timestamp}")
                except:
                    print(f"Slot {slot}: [Corrupted save]")
            else:
                print(f"Slot {slot}: [Empty]")
        
        print("=" * 30)
    
    def delete_save(self, slot: int) -> bool:
        """Delete a save slot"""
        try:
            filepath = os.path.join(self.save_dir, f"save_slot_{slot}.json")
            
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✓ Deleted save in slot {slot}")
                return True
            else:
                print(f"✗ No save found in slot {slot}")
                return False
                
        except Exception as e:
            print(f"✗ Failed to delete save: {e}")
            return False


def demo():
    """Demonstrate checkpoint functionality"""
    print("=== Checkpoint Demo ===\n")
    
    # Create checkpoint manager
    manager = CheckpointManager()
    
    # Create initial game state
    game = GameState()
    game.player_name = "Hero"
    game.level = 1
    game.score = 0
    game.health = 100
    game.inventory = ["sword"]
    game.position = {"x": 0, "y": 0}
    
    print(f"Starting game: {game.player_name}, Level {game.level}")
    
    # Save to slot 1
    manager.save_checkpoint(game, slot=1)
    
    # Simulate gameplay progress
    print("\n--- Playing game ---")
    game.level = 5
    game.score = 1500
    game.health = 75
    game.inventory.extend(["shield", "potion"])
    game.position = {"x": 100, "y": 200}
    
    print(f"Current progress: Level {game.level}, Score {game.score}")
    
    # Save to slot 2
    manager.save_checkpoint(game, slot=2)
    
    # Continue playing
    print("\n--- Continuing game ---")
    game.level = 10
    game.score = 5000
    game.health = 50
    
    print(f"Current progress: Level {game.level}, Score {game.score}")
    
    # List all saves
    print()
    manager.list_saves()
    
    # Load from earlier checkpoint
    print("\n--- Loading earlier save ---")
    loaded_game = manager.load_checkpoint(slot=2)
    
    if loaded_game:
        print(f"Restored to: Level {loaded_game.level}, Score {loaded_game.score}")
        print(f"Inventory: {loaded_game.inventory}")
        print(f"Position: {loaded_game.position}")


if __name__ == "__main__":
    demo()

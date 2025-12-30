"""
Machine Learning Checkpoint Example

Demonstrates how to use checkpoints during model training.
This is a simplified example for educational purposes.
"""

import json
import os
import time
from typing import Dict, List, Optional


class SimpleModel:
    """A simple model class for demonstration"""
    
    def __init__(self, input_size: int = 10, hidden_size: int = 5, output_size: int = 2):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        # In real implementation, these would be actual weights
        self.weights = {
            "layer1": [[0.1] * input_size for _ in range(hidden_size)],
            "layer2": [[0.1] * hidden_size for _ in range(output_size)]
        }
    
    def get_state(self) -> Dict:
        """Get model state for checkpointing"""
        return {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "output_size": self.output_size,
            "weights": self.weights
        }
    
    def load_state(self, state: Dict):
        """Load model state from checkpoint"""
        self.input_size = state["input_size"]
        self.hidden_size = state["hidden_size"]
        self.output_size = state["output_size"]
        self.weights = state["weights"]


class TrainingCheckpoint:
    """Manages checkpoints during model training"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.best_metric = float('inf')
    
    def save_checkpoint(
        self, 
        model: SimpleModel,
        epoch: int,
        train_loss: float,
        val_loss: float,
        metrics: Dict,
        is_best: bool = False
    ) -> str:
        """
        Save a training checkpoint
        
        Args:
            model: The model to save
            epoch: Current epoch number
            train_loss: Training loss
            val_loss: Validation loss
            metrics: Additional metrics
            is_best: Whether this is the best model so far
        
        Returns:
            Path to saved checkpoint
        """
        checkpoint = {
            "epoch": epoch,
            "model_state": model.get_state(),
            "train_loss": train_loss,
            "val_loss": val_loss,
            "metrics": metrics,
            "timestamp": time.time()
        }
        
        # Save regular checkpoint
        filename = f"checkpoint_epoch_{epoch:03d}.json"
        filepath = os.path.join(self.checkpoint_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        print(f"✓ Checkpoint saved: {filename}")
        
        # Save best model separately
        if is_best:
            best_path = os.path.join(self.checkpoint_dir, "best_model.json")
            with open(best_path, 'w') as f:
                json.dump(checkpoint, f, indent=2)
            print(f"✓ New best model saved! (val_loss: {val_loss:.4f})")
        
        return filepath
    
    def load_checkpoint(self, epoch: int = None, best: bool = False) -> Optional[Dict]:
        """
        Load a checkpoint
        
        Args:
            epoch: Specific epoch to load (or None for latest)
            best: Load best model instead
        
        Returns:
            Checkpoint data or None
        """
        try:
            if best:
                filepath = os.path.join(self.checkpoint_dir, "best_model.json")
            elif epoch is not None:
                filename = f"checkpoint_epoch_{epoch:03d}.json"
                filepath = os.path.join(self.checkpoint_dir, filename)
            else:
                # Load latest checkpoint
                checkpoints = [f for f in os.listdir(self.checkpoint_dir) 
                             if f.startswith("checkpoint_epoch_")]
                if not checkpoints:
                    return None
                latest = sorted(checkpoints)[-1]
                filepath = os.path.join(self.checkpoint_dir, latest)
            
            with open(filepath, 'r') as f:
                checkpoint = json.load(f)
            
            print(f"✓ Loaded checkpoint from epoch {checkpoint['epoch']}")
            return checkpoint
            
        except Exception as e:
            print(f"✗ Failed to load checkpoint: {e}")
            return None
    
    def cleanup_old_checkpoints(self, keep_last: int = 5):
        """Keep only the N most recent checkpoints"""
        checkpoints = [f for f in os.listdir(self.checkpoint_dir) 
                      if f.startswith("checkpoint_epoch_")]
        
        if len(checkpoints) <= keep_last:
            return
        
        # Sort and keep only recent ones
        checkpoints.sort()
        to_delete = checkpoints[:-keep_last]
        
        for filename in to_delete:
            filepath = os.path.join(self.checkpoint_dir, filename)
            os.remove(filepath)
        
        print(f"✓ Cleaned up {len(to_delete)} old checkpoints")


def simulate_training():
    """Simulate model training with checkpoints"""
    print("=== ML Training with Checkpoints ===\n")
    
    # Initialize model and checkpoint manager
    model = SimpleModel(input_size=10, hidden_size=5, output_size=2)
    checkpoint_mgr = TrainingCheckpoint()
    
    # Training parameters
    num_epochs = 20
    save_every = 5
    best_val_loss = float('inf')
    
    print(f"Training for {num_epochs} epochs...")
    print(f"Saving checkpoint every {save_every} epochs\n")
    
    # Training loop
    for epoch in range(1, num_epochs + 1):
        # Simulate training (in reality, this would be actual training)
        time.sleep(0.1)  # Simulate computation time
        
        # Simulate decreasing loss with some noise
        train_loss = 1.0 / (epoch + 1) + (epoch % 3) * 0.01
        val_loss = 1.2 / (epoch + 1) + (epoch % 4) * 0.015
        
        # Calculate metrics
        metrics = {
            "accuracy": min(0.99, 0.5 + epoch * 0.02),
            "learning_rate": 0.001 * (0.95 ** epoch)
        }
        
        # Print progress
        print(f"Epoch {epoch:2d}/{num_epochs} - "
              f"train_loss: {train_loss:.4f}, "
              f"val_loss: {val_loss:.4f}, "
              f"acc: {metrics['accuracy']:.4f}")
        
        # Save checkpoint at intervals
        is_best = val_loss < best_val_loss
        
        if epoch % save_every == 0 or is_best:
            checkpoint_mgr.save_checkpoint(
                model=model,
                epoch=epoch,
                train_loss=train_loss,
                val_loss=val_loss,
                metrics=metrics,
                is_best=is_best
            )
        
        if is_best:
            best_val_loss = val_loss
    
    print("\n--- Training Complete ---")
    
    # Cleanup old checkpoints
    print("\nCleaning up old checkpoints...")
    checkpoint_mgr.cleanup_old_checkpoints(keep_last=3)
    
    # Demonstrate loading
    print("\n--- Loading Best Model ---")
    best_checkpoint = checkpoint_mgr.load_checkpoint(best=True)
    
    if best_checkpoint:
        print(f"Best model from epoch {best_checkpoint['epoch']}")
        print(f"Validation loss: {best_checkpoint['val_loss']:.4f}")
        print(f"Metrics: {best_checkpoint['metrics']}")
        
        # Restore model state
        model.load_state(best_checkpoint['model_state'])
        print("✓ Model state restored")
    
    # Demonstrate resuming training
    print("\n--- Resuming Training Example ---")
    latest_checkpoint = checkpoint_mgr.load_checkpoint()
    
    if latest_checkpoint:
        start_epoch = latest_checkpoint['epoch'] + 1
        print(f"Can resume training from epoch {start_epoch}")


def demonstrate_recovery():
    """Demonstrate recovery from training interruption"""
    print("\n=== Training Recovery Demo ===\n")
    
    model = SimpleModel()
    checkpoint_mgr = TrainingCheckpoint(checkpoint_dir="recovery_checkpoints")
    
    print("Simulating training interruption...\n")
    
    # Train for a few epochs
    for epoch in range(1, 6):
        train_loss = 1.0 / (epoch + 1)
        val_loss = 1.2 / (epoch + 1)
        metrics = {"accuracy": 0.5 + epoch * 0.05}
        
        print(f"Epoch {epoch}/10 - loss: {train_loss:.4f}")
        
        checkpoint_mgr.save_checkpoint(
            model, epoch, train_loss, val_loss, metrics
        )
        
        if epoch == 5:
            print("\n⚠ Training interrupted! (simulated crash)\n")
            break
    
    # Recover and resume
    print("Recovering from checkpoint...")
    checkpoint = checkpoint_mgr.load_checkpoint()
    
    if checkpoint:
        model.load_state(checkpoint['model_state'])
        start_epoch = checkpoint['epoch'] + 1
        
        print(f"Resuming from epoch {start_epoch}\n")
        
        # Continue training
        for epoch in range(start_epoch, 11):
            train_loss = 1.0 / (epoch + 1)
            val_loss = 1.2 / (epoch + 1)
            metrics = {"accuracy": 0.5 + epoch * 0.05}
            
            print(f"Epoch {epoch}/10 - loss: {train_loss:.4f}")
            
            checkpoint_mgr.save_checkpoint(
                model, epoch, train_loss, val_loss, metrics
            )
        
        print("\n✓ Training completed successfully after recovery!")


if __name__ == "__main__":
    # Run training simulation
    simulate_training()
    
    # Run recovery demonstration
    print("\n" + "=" * 50 + "\n")
    demonstrate_recovery()

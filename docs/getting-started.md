# Getting Started with Checkpoints

## Introduction

This tutorial will guide you through implementing checkpoints in your applications, from basic concepts to advanced patterns.

## Prerequisites

- Basic programming knowledge in Python, JavaScript, or similar language
- Understanding of file I/O operations
- Familiarity with JSON data format

## Tutorial Outline

1. [Basic Checkpoint Implementation](#basic-checkpoint-implementation)
2. [Adding Metadata](#adding-metadata)
3. [Implementing Undo/Redo](#implementing-undoredo)
4. [Auto-Save Functionality](#auto-save-functionality)
5. [Error Handling](#error-handling)
6. [Performance Optimization](#performance-optimization)

---

## Basic Checkpoint Implementation

### Step 1: Define Your State

First, identify what data needs to be saved in a checkpoint.

```python
# Example: Simple application state
app_state = {
    'user_id': 123,
    'current_page': 'dashboard',
    'settings': {
        'theme': 'dark',
        'language': 'en'
    },
    'last_action': 'view_report'
}
```

### Step 2: Create a Save Function

```python
import json
import os

def save_checkpoint(state, filepath):
    """Save state to a checkpoint file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write state to file
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"✓ Checkpoint saved: {filepath}")
        return True
    except Exception as e:
        print(f"✗ Error saving checkpoint: {e}")
        return False
```

### Step 3: Create a Load Function

```python
def load_checkpoint(filepath):
    """Load state from a checkpoint file"""
    try:
        if not os.path.exists(filepath):
            print(f"✗ Checkpoint not found: {filepath}")
            return None
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        print(f"✓ Checkpoint loaded: {filepath}")
        return state
    except Exception as e:
        print(f"✗ Error loading checkpoint: {e}")
        return None
```

### Step 4: Use the Checkpoint System

```python
# Save current state
save_checkpoint(app_state, 'checkpoints/app_state.json')

# Load saved state
restored_state = load_checkpoint('checkpoints/app_state.json')

if restored_state:
    app_state = restored_state
    print("State restored successfully!")
```

### Exercise 1

Create a simple note-taking application that saves checkpoints of your notes.

**Requirements:**
- Save notes to a checkpoint
- Load notes from a checkpoint
- Support multiple checkpoint files

---

## Adding Metadata

Enhance your checkpoints with metadata like timestamps, versions, and descriptions.

```python
from datetime import datetime

def save_checkpoint_with_metadata(state, filepath, description=""):
    """Save checkpoint with metadata"""
    checkpoint = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'description': description,
            'checksum': compute_checksum(state)  # Optional
        },
        'data': state
    }
    
    with open(filepath, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    return True

def load_checkpoint_with_metadata(filepath):
    """Load checkpoint and return both data and metadata"""
    with open(filepath, 'r') as f:
        checkpoint = json.load(f)
    
    return {
        'data': checkpoint['data'],
        'metadata': checkpoint['metadata']
    }
```

### Exercise 2

Add metadata to your note-taking app from Exercise 1:
- Timestamp when the note was saved
- Note title/description
- Version number

---

## Implementing Undo/Redo

Create a history-based checkpoint system for undo/redo functionality.

```python
class CheckpointHistory:
    """Manage checkpoint history for undo/redo"""
    
    def __init__(self, max_history=50):
        self.history = []
        self.current_index = -1
        self.max_history = max_history
    
    def save(self, state):
        """Save a new checkpoint"""
        import copy
        
        # Remove any "future" history if we're not at the end
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Add new checkpoint
        self.history.append(copy.deepcopy(state))
        self.current_index += 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
    
    def undo(self):
        """Go back one checkpoint"""
        if self.current_index > 0:
            self.current_index -= 1
            return copy.deepcopy(self.history[self.current_index])
        return None
    
    def redo(self):
        """Go forward one checkpoint"""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return copy.deepcopy(self.history[self.current_index])
        return None
    
    def can_undo(self):
        return self.current_index > 0
    
    def can_redo(self):
        return self.current_index < len(self.history) - 1

# Usage
history = CheckpointHistory()

# Save states
history.save({'text': 'Hello'})
history.save({'text': 'Hello World'})
history.save({'text': 'Hello World!'})

# Undo
previous = history.undo()  # Back to 'Hello World'

# Redo
next_state = history.redo()  # Forward to 'Hello World!'
```

### Exercise 3

Add undo/redo functionality to your note-taking app:
- Keep a history of the last 10 changes
- Implement undo button
- Implement redo button
- Show current position in history

---

## Auto-Save Functionality

Implement automatic checkpoint saving at regular intervals.

```python
import threading
import time

class AutoSaveManager:
    """Manage automatic checkpoint saving"""
    
    def __init__(self, save_function, interval_seconds=60):
        self.save_function = save_function
        self.interval = interval_seconds
        self.running = False
        self.thread = None
    
    def start(self):
        """Start auto-save"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._auto_save_loop)
        self.thread.daemon = True
        self.thread.start()
        print(f"✓ Auto-save started (every {self.interval}s)")
    
    def stop(self):
        """Stop auto-save"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("✓ Auto-save stopped")
    
    def _auto_save_loop(self):
        """Background loop for auto-saving"""
        while self.running:
            time.sleep(self.interval)
            if self.running:  # Check again after sleep
                try:
                    self.save_function()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Auto-save completed")
                except Exception as e:
                    print(f"Auto-save failed: {e}")

# Usage
def save_my_work():
    save_checkpoint(app_state, 'checkpoints/autosave.json')

auto_save = AutoSaveManager(save_my_work, interval_seconds=30)
auto_save.start()

# Work on your application...

# Stop when done
auto_save.stop()
```

### Exercise 4

Add auto-save to your note-taking app:
- Auto-save every 30 seconds
- Show last auto-save time
- Allow user to enable/disable auto-save

---

## Error Handling

Implement robust error handling for checkpoint operations.

```python
class CheckpointError(Exception):
    """Base exception for checkpoint errors"""
    pass

class CheckpointSaveError(CheckpointError):
    """Error saving checkpoint"""
    pass

class CheckpointLoadError(CheckpointError):
    """Error loading checkpoint"""
    pass

def safe_save_checkpoint(state, filepath):
    """Save checkpoint with comprehensive error handling"""
    import tempfile
    import shutil
    
    try:
        # Validate state
        if not isinstance(state, dict):
            raise CheckpointSaveError("State must be a dictionary")
        
        # Create temp file first (atomic save)
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            json.dump(state, tmp, indent=2)
            temp_path = tmp.name
        
        # Move temp file to final location (atomic operation)
        shutil.move(temp_path, filepath)
        
        return True
        
    except (IOError, OSError) as e:
        raise CheckpointSaveError(f"Failed to write checkpoint: {e}")
    except (TypeError, ValueError) as e:
        raise CheckpointSaveError(f"Invalid state data: {e}")
    finally:
        # Clean up temp file if it still exists
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass

def safe_load_checkpoint(filepath):
    """Load checkpoint with error handling and validation"""
    try:
        if not os.path.exists(filepath):
            raise CheckpointLoadError(f"Checkpoint file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        # Validate loaded data
        if not isinstance(state, dict):
            raise CheckpointLoadError("Invalid checkpoint format")
        
        return state
        
    except json.JSONDecodeError as e:
        raise CheckpointLoadError(f"Corrupted checkpoint file: {e}")
    except (IOError, OSError) as e:
        raise CheckpointLoadError(f"Failed to read checkpoint: {e}")
```

### Exercise 5

Add error handling to your note-taking app:
- Handle missing files gracefully
- Validate checkpoint data before loading
- Show user-friendly error messages
- Implement backup/recovery mechanism

---

## Performance Optimization

Optimize checkpoint performance for large applications.

### Compression

```python
import gzip

def save_compressed_checkpoint(state, filepath):
    """Save checkpoint with compression"""
    with gzip.open(filepath, 'wt') as f:
        json.dump(state, f)

def load_compressed_checkpoint(filepath):
    """Load compressed checkpoint"""
    with gzip.open(filepath, 'rt') as f:
        return json.load(f)
```

### Incremental Checkpoints

```python
def save_incremental_checkpoint(old_state, new_state, filepath):
    """Save only the differences between states"""
    delta = {}
    
    for key in new_state:
        if key not in old_state or old_state[key] != new_state[key]:
            delta[key] = new_state[key]
    
    checkpoint = {
        'type': 'incremental',
        'delta': delta,
        'timestamp': datetime.now().isoformat()
    }
    
    with open(filepath, 'w') as f:
        json.dump(checkpoint, f)
```

### Async Saving

```python
import asyncio

async def async_save_checkpoint(state, filepath):
    """Save checkpoint asynchronously"""
    loop = asyncio.get_event_loop()
    
    def _save():
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    # Run in executor to not block
    await loop.run_in_executor(None, _save)
    print("Checkpoint saved asynchronously")
```

---

## Best Practices Summary

1. **Always validate** data before saving and after loading
2. **Use atomic saves** (temp file + move) to prevent corruption
3. **Add metadata** for debugging and auditing
4. **Limit history size** to manage memory usage
5. **Handle errors gracefully** and inform users
6. **Test recovery** scenarios regularly
7. **Document** checkpoint format and versioning
8. **Consider compression** for large states
9. **Implement cleanup** for old checkpoints
10. **Use appropriate intervals** for auto-save

---

## Final Project

Build a complete application with checkpoint functionality:

**Project: Task Manager with Checkpoints**

Features to implement:
1. Create, edit, and delete tasks
2. Save/load task list from checkpoints
3. Undo/redo functionality
4. Auto-save every 60 seconds
5. Multiple save slots
6. Export/import functionality
7. Error handling and recovery
8. Checkpoint history viewer

---

## Additional Resources

- [Memento Design Pattern](https://refactoring.guru/design-patterns/memento)
- [Python Pickle Module](https://docs.python.org/3/library/pickle.html)
- [JSON Best Practices](https://www.json.org/json-en.html)
- [File I/O Best Practices](https://docs.python.org/3/tutorial/inputoutput.html)

## Next Steps

- Explore the [examples](../examples/) directory for complete implementations
- Read about [ML Checkpoints](ml-checkpoints.md) for machine learning applications
- Learn about [Database Checkpoints](database-checkpoints.md) for data systems
- Study [Checkpoint Patterns](checkpoint-patterns.md) for advanced techniques

Happy Learning! 🎓

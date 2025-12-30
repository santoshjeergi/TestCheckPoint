# Checkpoint Design Patterns

## Overview

This guide covers common design patterns and best practices for implementing checkpoints across different systems and applications.

## Core Checkpoint Patterns

### 1. Memento Pattern

The Memento pattern is the foundational design pattern for checkpoints.

```python
from datetime import datetime
from typing import Any, List

class Memento:
    """Stores the state of an object at a point in time"""
    
    def __init__(self, state: Any):
        self._state = state
        self._timestamp = datetime.now()
    
    def get_state(self) -> Any:
        return self._state
    
    def get_timestamp(self) -> datetime:
        return self._timestamp

class Originator:
    """The object whose state we want to save"""
    
    def __init__(self):
        self._state = None
    
    def set_state(self, state: Any):
        """Set current state"""
        print(f"Setting state to: {state}")
        self._state = state
    
    def save_to_memento(self) -> Memento:
        """Create a memento of current state"""
        print(f"Saving state: {self._state}")
        return Memento(self._state)
    
    def restore_from_memento(self, memento: Memento):
        """Restore state from memento"""
        self._state = memento.get_state()
        print(f"Restored state: {self._state}")

class Caretaker:
    """Manages mementos (checkpoints)"""
    
    def __init__(self):
        self._mementos: List[Memento] = []
    
    def add_memento(self, memento: Memento):
        """Save a new checkpoint"""
        self._mementos.append(memento)
    
    def get_memento(self, index: int) -> Memento:
        """Retrieve a checkpoint"""
        return self._mementos[index]
    
    def get_latest(self) -> Memento:
        """Get most recent checkpoint"""
        return self._mementos[-1] if self._mementos else None

# Usage
originator = Originator()
caretaker = Caretaker()

# Change state and save checkpoints
originator.set_state("State 1")
caretaker.add_memento(originator.save_to_memento())

originator.set_state("State 2")
caretaker.add_memento(originator.save_to_memento())

originator.set_state("State 3")
caretaker.add_memento(originator.save_to_memento())

# Restore to previous state
originator.restore_from_memento(caretaker.get_memento(1))
```

### 2. Command Pattern with Checkpointing

Combine command pattern with checkpoints for undo/redo functionality.

```python
from abc import ABC, abstractmethod
from typing import List

class Command(ABC):
    """Abstract command interface"""
    
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

class Document:
    """Document that can be modified"""
    
    def __init__(self):
        self.content = ""
    
    def insert(self, text: str, position: int):
        self.content = self.content[:position] + text + self.content[position:]
    
    def delete(self, position: int, length: int):
        return self.content[position:position + length]

class InsertCommand(Command):
    """Command to insert text"""
    
    def __init__(self, document: Document, text: str, position: int):
        self.document = document
        self.text = text
        self.position = position
    
    def execute(self):
        self.document.insert(self.text, self.position)
    
    def undo(self):
        # Delete the inserted text
        self.document.delete(self.position, len(self.text))

class CommandManager:
    """Manages commands and checkpoints"""
    
    def __init__(self):
        self.history: List[Command] = []
        self.current = -1
    
    def execute(self, command: Command):
        """Execute command and save to history"""
        # Remove commands after current position
        self.history = self.history[:self.current + 1]
        
        command.execute()
        self.history.append(command)
        self.current += 1
    
    def undo(self):
        """Undo last command"""
        if self.current >= 0:
            self.history[self.current].undo()
            self.current -= 1
    
    def redo(self):
        """Redo previously undone command"""
        if self.current < len(self.history) - 1:
            self.current += 1
            self.history[self.current].execute()
    
    def create_checkpoint(self) -> int:
        """Create a checkpoint at current position"""
        return self.current
    
    def restore_checkpoint(self, checkpoint: int):
        """Restore to a checkpoint"""
        while self.current > checkpoint:
            self.undo()
        while self.current < checkpoint:
            self.redo()

# Usage
doc = Document()
manager = CommandManager()

# Execute commands
manager.execute(InsertCommand(doc, "Hello", 0))
manager.execute(InsertCommand(doc, " World", 5))

checkpoint1 = manager.create_checkpoint()

manager.execute(InsertCommand(doc, "!", 11))

# Restore to checkpoint
manager.restore_checkpoint(checkpoint1)
```

### 3. Snapshot Pattern

Regular automated snapshots of system state.

```python
import time
import threading
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class Snapshot:
    """Represents a system snapshot"""
    data: dict
    timestamp: float
    version: int

class SnapshotManager:
    """Manages periodic snapshots"""
    
    def __init__(self, 
                 get_state_func: Callable,
                 interval_seconds: int = 60,
                 max_snapshots: int = 10):
        self.get_state_func = get_state_func
        self.interval = interval_seconds
        self.max_snapshots = max_snapshots
        self.snapshots: List[Snapshot] = []
        self.version = 0
        self.running = False
        self.thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start periodic snapshots"""
        self.running = True
        self.thread = threading.Thread(target=self._snapshot_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop periodic snapshots"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _snapshot_loop(self):
        """Background loop for taking snapshots"""
        while self.running:
            self.take_snapshot()
            time.sleep(self.interval)
    
    def take_snapshot(self):
        """Take a snapshot of current state"""
        state = self.get_state_func()
        snapshot = Snapshot(
            data=state,
            timestamp=time.time(),
            version=self.version
        )
        
        self.snapshots.append(snapshot)
        self.version += 1
        
        # Keep only max_snapshots
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)
        
        print(f"Snapshot {snapshot.version} taken at {snapshot.timestamp}")
    
    def get_latest_snapshot(self) -> Optional[Snapshot]:
        """Get most recent snapshot"""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_snapshot_by_version(self, version: int) -> Optional[Snapshot]:
        """Get snapshot by version number"""
        for snapshot in self.snapshots:
            if snapshot.version == version:
                return snapshot
        return None
    
    def restore_latest(self) -> Optional[dict]:
        """Restore from latest snapshot"""
        snapshot = self.get_latest_snapshot()
        return snapshot.data if snapshot else None

# Usage
def get_app_state():
    return {'users': 100, 'transactions': 500, 'uptime': time.time()}

snapshot_mgr = SnapshotManager(
    get_state_func=get_app_state,
    interval_seconds=30,
    max_snapshots=5
)

# snapshot_mgr.start()  # Start automatic snapshots
# Manual snapshot
snapshot_mgr.take_snapshot()
```

### 4. Copy-on-Write Pattern

Efficient checkpointing using copy-on-write semantics.

```python
import copy
from typing import Any, Dict

class CopyOnWriteCheckpoint:
    """Checkpoint using copy-on-write for efficiency"""
    
    def __init__(self, initial_state: Dict):
        self._original = initial_state
        self._modified = {}
        self._deleted = set()
    
    def get(self, key: str) -> Any:
        """Get value with copy-on-write"""
        if key in self._deleted:
            raise KeyError(f"Key '{key}' has been deleted")
        
        if key in self._modified:
            return self._modified[key]
        
        return self._original.get(key)
    
    def set(self, key: str, value: Any):
        """Set value (copy-on-write)"""
        if key in self._deleted:
            self._deleted.remove(key)
        self._modified[key] = value
    
    def delete(self, key: str):
        """Delete key"""
        self._deleted.add(key)
        if key in self._modified:
            del self._modified[key]
    
    def commit(self) -> Dict:
        """Commit changes and return new state"""
        new_state = copy.deepcopy(self._original)
        
        # Apply modifications
        for key, value in self._modified.items():
            new_state[key] = value
        
        # Apply deletions
        for key in self._deleted:
            if key in new_state:
                del new_state[key]
        
        return new_state
    
    def rollback(self):
        """Discard all changes"""
        self._modified.clear()
        self._deleted.clear()
    
    def has_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        return bool(self._modified or self._deleted)

# Usage
original = {'name': 'John', 'age': 30, 'city': 'NYC'}
checkpoint = CopyOnWriteCheckpoint(original)

# Make changes
checkpoint.set('age', 31)
checkpoint.set('country', 'USA')
checkpoint.delete('city')

# Check changes
if checkpoint.has_changes():
    new_state = checkpoint.commit()
    print(f"New state: {new_state}")
```

### 5. Incremental Checkpoint Pattern

Only save changes since last checkpoint.

```python
import json
from typing import Any, Dict, List
from datetime import datetime

class IncrementalCheckpoint:
    """Checkpoint that stores only deltas"""
    
    def __init__(self, base_state: Dict):
        self.base_state = base_state
        self.deltas: List[Dict] = []
    
    def compute_delta(self, old_state: Dict, new_state: Dict) -> Dict:
        """Compute difference between states"""
        delta = {
            'added': {},
            'modified': {},
            'deleted': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Find added and modified keys
        for key, value in new_state.items():
            if key not in old_state:
                delta['added'][key] = value
            elif old_state[key] != value:
                delta['modified'][key] = {
                    'old': old_state[key],
                    'new': value
                }
        
        # Find deleted keys
        for key in old_state:
            if key not in new_state:
                delta['deleted'].append(key)
        
        return delta
    
    def save_checkpoint(self, current_state: Dict):
        """Save incremental checkpoint"""
        last_state = self.reconstruct_state()
        delta = self.compute_delta(last_state, current_state)
        
        if delta['added'] or delta['modified'] or delta['deleted']:
            self.deltas.append(delta)
            print(f"Incremental checkpoint saved: {len(self.deltas)}")
        else:
            print("No changes detected, checkpoint skipped")
    
    def reconstruct_state(self, up_to_checkpoint: int = None) -> Dict:
        """Reconstruct state from base and deltas"""
        state = copy.deepcopy(self.base_state)
        
        checkpoints_to_apply = (
            self.deltas[:up_to_checkpoint + 1] 
            if up_to_checkpoint is not None 
            else self.deltas
        )
        
        for delta in checkpoints_to_apply:
            # Apply additions
            state.update(delta['added'])
            
            # Apply modifications
            for key, change in delta['modified'].items():
                state[key] = change['new']
            
            # Apply deletions
            for key in delta['deleted']:
                if key in state:
                    del state[key]
        
        return state
    
    def compact(self):
        """Compact deltas into new base state"""
        self.base_state = self.reconstruct_state()
        self.deltas.clear()
        print("Checkpoints compacted")

# Usage
base = {'x': 1, 'y': 2}
inc_checkpoint = IncrementalCheckpoint(base)

# Save changes
state1 = {'x': 1, 'y': 3, 'z': 4}
inc_checkpoint.save_checkpoint(state1)

state2 = {'x': 2, 'y': 3, 'z': 4}
inc_checkpoint.save_checkpoint(state2)

# Reconstruct state
reconstructed = inc_checkpoint.reconstruct_state(up_to_checkpoint=0)
print(f"State at checkpoint 0: {reconstructed}")
```

## Best Practices Summary

### 1. Choose the Right Pattern
- **Simple applications**: File-based memento
- **Undo/redo**: Command pattern
- **Real-time systems**: Snapshot pattern
- **Large states**: Copy-on-write or incremental
- **Distributed systems**: Event sourcing with checkpoints

### 2. Performance Considerations
```python
# Good: Lazy evaluation
def create_checkpoint(self):
    return {'ref': id(self.state), 'timestamp': time.time()}

# Bad: Eager deep copy every time
def create_checkpoint(self):
    return copy.deepcopy(self.state)  # Expensive!
```

### 3. Storage Management
```python
class CheckpointRotation:
    """Rotate old checkpoints to manage storage"""
    
    def __init__(self, max_checkpoints=10):
        self.max_checkpoints = max_checkpoints
        self.checkpoints = []
    
    def add(self, checkpoint):
        self.checkpoints.append(checkpoint)
        
        if len(self.checkpoints) > self.max_checkpoints:
            # Keep first, last, and evenly distributed middle points
            to_keep = [0]  # Always keep first
            step = len(self.checkpoints) // (self.max_checkpoints - 2)
            to_keep.extend(range(step, len(self.checkpoints) - 1, step))
            to_keep.append(len(self.checkpoints) - 1)  # Always keep last
            
            self.checkpoints = [self.checkpoints[i] for i in to_keep]
```

### 4. Validation and Integrity
```python
import hashlib

class CheckpointWithHash:
    """Checkpoint with integrity checking"""
    
    def __init__(self, state):
        self.state = state
        self.hash = self._compute_hash(state)
    
    def _compute_hash(self, state):
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def verify(self):
        """Verify checkpoint integrity"""
        return self.hash == self._compute_hash(self.state)
```

### 5. Async and Non-Blocking
```python
import asyncio

class AsyncCheckpointPattern:
    """Non-blocking checkpoint operations"""
    
    async def save_async(self, state, filepath):
        """Save checkpoint without blocking"""
        # Offload to thread pool for I/O
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_sync, state, filepath)
    
    def _save_sync(self, state, filepath):
        with open(filepath, 'w') as f:
            json.dump(state, f)
```

## Anti-Patterns to Avoid

### ❌ Not Handling Checkpoint Failures
```python
# Bad: No error handling
def save_checkpoint(state):
    with open('checkpoint.json', 'w') as f:
        json.dump(state, f)  # What if disk is full?

# Good: Handle failures gracefully
def save_checkpoint(state):
    try:
        with open('checkpoint.json', 'w') as f:
            json.dump(state, f)
        return True
    except IOError as e:
        print(f"Checkpoint save failed: {e}")
        return False
```

### ❌ Blocking on Large Checkpoints
```python
# Bad: Blocking save
checkpoint = create_large_checkpoint()  # Blocks for seconds

# Good: Async save
await save_checkpoint_async(checkpoint)
```

### ❌ No Checkpoint Cleanup
```python
# Bad: Unlimited checkpoints
while True:
    save_checkpoint()  # Fills disk eventually

# Good: Rotation policy
save_checkpoint_with_rotation(max_count=10)
```

## Exercises

1. Implement a text editor with undo/redo using Command pattern
2. Create a snapshot manager with configurable intervals
3. Build an incremental checkpoint system for a key-value store
4. Implement checkpoint compression for large states
5. Design a distributed checkpoint coordinator

## Additional Resources

- [Gang of Four Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns)
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS and Event Sourcing](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)

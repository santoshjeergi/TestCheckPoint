# Application State Management and Checkpoints

## Overview

Application checkpoints allow programs to save their current state so they can:
- Resume after crashes or restarts
- Provide save/load functionality
- Support undo/redo operations
- Enable state migration and updates

## Types of Application Checkpoints

### 1. User Session Checkpoints
Saving user progress and session data

### 2. Application State Snapshots
Complete application state at a point in time

### 3. Transactional Checkpoints
Ensuring atomic operations complete successfully

### 4. Configuration Checkpoints
Versioned configuration states

## Implementation Patterns

### Pattern 1: Simple File-Based Checkpoint

```python
import json
import pickle
from datetime import datetime
from pathlib import Path

class ApplicationCheckpoint:
    """Simple checkpoint manager for application state"""
    
    def __init__(self, checkpoint_dir='checkpoints'):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def save(self, state, name=None):
        """Save application state to a checkpoint"""
        if name is None:
            name = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = self.checkpoint_dir / f"{name}.json"
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"Checkpoint saved: {filepath}")
        return filepath
    
    def load(self, name):
        """Load application state from a checkpoint"""
        filepath = self.checkpoint_dir / f"{name}.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Checkpoint not found: {filepath}")
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        print(f"Checkpoint loaded: {filepath}")
        return state
    
    def list_checkpoints(self):
        """List all available checkpoints"""
        return sorted([f.stem for f in self.checkpoint_dir.glob("*.json")])
    
    def delete(self, name):
        """Delete a checkpoint"""
        filepath = self.checkpoint_dir / f"{name}.json"
        if filepath.exists():
            filepath.unlink()
            print(f"Checkpoint deleted: {filepath}")

# Usage Example
checkpoint_manager = ApplicationCheckpoint()

# Application state
app_state = {
    'user_id': 12345,
    'current_level': 5,
    'score': 1000,
    'inventory': ['sword', 'shield', 'potion'],
    'position': {'x': 100, 'y': 250},
    'settings': {
        'volume': 0.8,
        'difficulty': 'normal'
    }
}

# Save checkpoint
checkpoint_manager.save(app_state, 'game_save_1')

# Load checkpoint
loaded_state = checkpoint_manager.load('game_save_1')

# List checkpoints
checkpoints = checkpoint_manager.list_checkpoints()
print(f"Available checkpoints: {checkpoints}")
```

### Pattern 2: Versioned Checkpoints with Rollback

```python
from collections import deque
import copy

class VersionedCheckpoint:
    """Checkpoint manager with version history and rollback support"""
    
    def __init__(self, max_versions=10):
        self.max_versions = max_versions
        self.versions = deque(maxlen=max_versions)
        self.current_version = -1
    
    def save_checkpoint(self, state):
        """Save a new version of the state"""
        # If we're not at the latest version, remove future versions
        if self.current_version < len(self.versions) - 1:
            versions_to_remove = len(self.versions) - self.current_version - 1
            for _ in range(versions_to_remove):
                self.versions.pop()
        
        # Save new version
        self.versions.append(copy.deepcopy(state))
        self.current_version = len(self.versions) - 1
        
        return self.current_version
    
    def undo(self):
        """Go back to previous version"""
        if self.current_version > 0:
            self.current_version -= 1
            return copy.deepcopy(self.versions[self.current_version])
        return None
    
    def redo(self):
        """Go forward to next version"""
        if self.current_version < len(self.versions) - 1:
            self.current_version += 1
            return copy.deepcopy(self.versions[self.current_version])
        return None
    
    def get_current(self):
        """Get current version"""
        if self.versions:
            return copy.deepcopy(self.versions[self.current_version])
        return None
    
    def rollback_to(self, version_number):
        """Rollback to a specific version"""
        if 0 <= version_number < len(self.versions):
            self.current_version = version_number
            return copy.deepcopy(self.versions[self.current_version])
        return None

# Usage Example
checkpoint = VersionedCheckpoint(max_versions=5)

# Initial state
document = {'text': 'Hello', 'cursor': 5}
checkpoint.save_checkpoint(document)

# Edit 1
document = {'text': 'Hello World', 'cursor': 11}
checkpoint.save_checkpoint(document)

# Edit 2
document = {'text': 'Hello World!', 'cursor': 12}
checkpoint.save_checkpoint(document)

# Undo
previous_state = checkpoint.undo()
print(f"After undo: {previous_state}")

# Redo
next_state = checkpoint.redo()
print(f"After redo: {next_state}")
```

### Pattern 3: Database-Backed Checkpoints

```python
import sqlite3
import json
from datetime import datetime

class DatabaseCheckpoint:
    """Checkpoint manager using SQLite for persistence"""
    
    def __init__(self, db_path='checkpoints.db'):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Create checkpoints table if it doesn't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    state TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            conn.commit()
    
    def save(self, name, state, metadata=None):
        """Save checkpoint to database"""
        state_json = json.dumps(state)
        metadata_json = json.dumps(metadata) if metadata else None
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    'INSERT INTO checkpoints (name, state, metadata) VALUES (?, ?, ?)',
                    (name, state_json, metadata_json)
                )
                conn.commit()
                print(f"Checkpoint '{name}' saved to database")
            except sqlite3.IntegrityError:
                # Update existing checkpoint
                conn.execute(
                    'UPDATE checkpoints SET state = ?, metadata = ?, created_at = CURRENT_TIMESTAMP WHERE name = ?',
                    (state_json, metadata_json, name)
                )
                conn.commit()
                print(f"Checkpoint '{name}' updated in database")
    
    def load(self, name):
        """Load checkpoint from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT state, metadata FROM checkpoints WHERE name = ?',
                (name,)
            )
            row = cursor.fetchone()
            
            if row:
                state = json.loads(row[0])
                metadata = json.loads(row[1]) if row[1] else None
                return {'state': state, 'metadata': metadata}
            return None
    
    def list_all(self):
        """List all checkpoints"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT name, created_at FROM checkpoints ORDER BY created_at DESC'
            )
            return cursor.fetchall()
    
    def delete(self, name):
        """Delete a checkpoint"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM checkpoints WHERE name = ?', (name,))
            conn.commit()
            print(f"Checkpoint '{name}' deleted")

# Usage Example
db_checkpoint = DatabaseCheckpoint('app_checkpoints.db')

# Save checkpoint
app_state = {
    'users': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}],
    'config': {'theme': 'dark', 'language': 'en'}
}
metadata = {'version': '1.0', 'author': 'admin'}
db_checkpoint.save('production_state', app_state, metadata)

# Load checkpoint
loaded = db_checkpoint.load('production_state')
print(f"Loaded state: {loaded['state']}")
print(f"Metadata: {loaded['metadata']}")
```

### Pattern 4: Async Checkpoint with Background Saving

```python
import asyncio
import json
from pathlib import Path
from datetime import datetime

class AsyncCheckpoint:
    """Asynchronous checkpoint manager for non-blocking saves"""
    
    def __init__(self, checkpoint_dir='async_checkpoints'):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.save_queue = asyncio.Queue()
        self.running = False
    
    async def start_background_saver(self):
        """Start background task for processing save queue"""
        self.running = True
        while self.running:
            try:
                save_task = await asyncio.wait_for(
                    self.save_queue.get(), 
                    timeout=1.0
                )
                await self._save_to_disk(save_task['name'], save_task['state'])
            except asyncio.TimeoutError:
                continue
    
    async def _save_to_disk(self, name, state):
        """Actually write checkpoint to disk"""
        filepath = self.checkpoint_dir / f"{name}.json"
        
        # Simulate async I/O
        await asyncio.sleep(0.1)
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"Async checkpoint saved: {filepath}")
    
    async def save(self, state, name=None):
        """Queue a checkpoint save (non-blocking)"""
        if name is None:
            name = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        await self.save_queue.put({'name': name, 'state': state})
        print(f"Checkpoint '{name}' queued for saving")
    
    async def load(self, name):
        """Load checkpoint from disk"""
        filepath = self.checkpoint_dir / f"{name}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        return state
    
    def stop(self):
        """Stop background saver"""
        self.running = False

# Usage Example
async def main():
    checkpoint = AsyncCheckpoint()
    
    # Start background saver
    saver_task = asyncio.create_task(checkpoint.start_background_saver())
    
    # Queue multiple saves
    for i in range(5):
        state = {'iteration': i, 'data': f'Data at step {i}'}
        await checkpoint.save(state, f'checkpoint_{i}')
        await asyncio.sleep(0.5)
    
    # Wait for queue to empty
    await asyncio.sleep(2)
    
    # Stop background saver
    checkpoint.stop()
    await saver_task

# Run async example
# asyncio.run(main())
```

## Best Practices

### 1. Atomic Saves
```python
import tempfile
import shutil

def atomic_save(state, filepath):
    """Save checkpoint atomically to prevent corruption"""
    # Write to temporary file first
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        json.dump(state, tmp, indent=2)
        tmp_path = tmp.name
    
    # Atomic move
    shutil.move(tmp_path, filepath)
```

### 2. Compression for Large States
```python
import gzip

def save_compressed(state, filepath):
    """Save checkpoint with compression"""
    with gzip.open(filepath, 'wt') as f:
        json.dump(state, f)

def load_compressed(filepath):
    """Load compressed checkpoint"""
    with gzip.open(filepath, 'rt') as f:
        return json.load(f)
```

### 3. Validation and Schema Checking
```python
def validate_checkpoint(state, schema):
    """Validate checkpoint against schema"""
    required_keys = schema.get('required', [])
    for key in required_keys:
        if key not in state:
            raise ValueError(f"Missing required key: {key}")
    return True
```

### 4. Auto-Save Mechanism
```python
import time
import threading

class AutoSaveCheckpoint:
    def __init__(self, save_interval=60):
        self.save_interval = save_interval
        self.state = {}
        self.running = False
        self.thread = None
    
    def start_auto_save(self):
        self.running = True
        self.thread = threading.Thread(target=self._auto_save_loop)
        self.thread.start()
    
    def _auto_save_loop(self):
        while self.running:
            time.sleep(self.save_interval)
            self.save_checkpoint()
    
    def save_checkpoint(self):
        # Save logic here
        print(f"Auto-save triggered at {datetime.now()}")
    
    def stop_auto_save(self):
        self.running = False
        if self.thread:
            self.thread.join()
```

## Exercises

1. Implement a checkpoint system for a text editor with undo/redo
2. Create an auto-save feature that saves every 5 minutes
3. Build a checkpoint manager that keeps the last 10 versions
4. Implement checkpoint encryption for sensitive application state
5. Create a checkpoint migration system for handling schema changes

## Common Use Cases

- **Game Save Systems**: Player progress and game state
- **Document Editors**: Auto-save and version history
- **Web Applications**: Session management and crash recovery
- **Data Processing**: Resume long-running jobs
- **Configuration Management**: Rollback configuration changes

## Additional Resources

- [Design Patterns for State Management](https://refactoring.guru/design-patterns/memento)
- [Redis for Session Checkpoints](https://redis.io/docs/manual/persistence/)
- [Application State Best Practices](https://12factor.net/config)

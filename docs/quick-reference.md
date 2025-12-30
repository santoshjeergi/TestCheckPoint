# Checkpoint Quick Reference Guide

## 📝 Quick Commands

### Python

```python
# Save checkpoint
import json
with open('checkpoint.json', 'w') as f:
    json.dump(state, f, indent=2)

# Load checkpoint
with open('checkpoint.json', 'r') as f:
    state = json.load(f)

# Pickle (for Python objects)
import pickle
with open('checkpoint.pkl', 'wb') as f:
    pickle.dump(obj, f)

with open('checkpoint.pkl', 'rb') as f:
    obj = pickle.load(f)
```

### JavaScript/Node.js

```javascript
// Save checkpoint
const fs = require('fs').promises;
await fs.writeFile('checkpoint.json', JSON.stringify(state, null, 2));

// Load checkpoint
const data = await fs.readFile('checkpoint.json', 'utf-8');
const state = JSON.parse(data);

// Synchronous
const fs = require('fs');
fs.writeFileSync('checkpoint.json', JSON.stringify(state, null, 2));
const state = JSON.parse(fs.readFileSync('checkpoint.json', 'utf-8'));
```

### PyTorch

```python
import torch

# Save model checkpoint
torch.save({
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}, 'checkpoint.pth')

# Load checkpoint
checkpoint = torch.load('checkpoint.pth')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
epoch = checkpoint['epoch']
loss = checkpoint['loss']
```

### TensorFlow/Keras

```python
# Save checkpoint
model.save_weights('checkpoint.h5')

# Load checkpoint
model.load_weights('checkpoint.h5')

# Full model save
model.save('model_checkpoint.h5')
model = keras.models.load_model('model_checkpoint.h5')
```

### SQL Databases

```sql
-- PostgreSQL
CHECKPOINT;

-- MySQL
FLUSH TABLES;

-- SQL Server
CHECKPOINT;
```

## 🔧 Common Patterns

### Pattern 1: Basic Save/Load

```python
class CheckpointManager:
    def save(self, state, filepath):
        with open(filepath, 'w') as f:
            json.dump(state, f)
    
    def load(self, filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
```

### Pattern 2: Undo/Redo

```python
class History:
    def __init__(self):
        self.history = []
        self.index = -1
    
    def save(self, state):
        self.history = self.history[:self.index + 1]
        self.history.append(copy.deepcopy(state))
        self.index += 1
    
    def undo(self):
        if self.index > 0:
            self.index -= 1
            return self.history[self.index]
    
    def redo(self):
        if self.index < len(self.history) - 1:
            self.index += 1
            return self.history[self.index]
```

### Pattern 3: Auto-Save

```python
import threading
import time

class AutoSave:
    def __init__(self, save_func, interval=60):
        self.save_func = save_func
        self.interval = interval
        self.running = False
    
    def start(self):
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()
    
    def _loop(self):
        while self.running:
            time.sleep(self.interval)
            self.save_func()
    
    def stop(self):
        self.running = False
```

### Pattern 4: Best Model Tracking

```python
class BestModelCheckpoint:
    def __init__(self):
        self.best_metric = float('inf')
    
    def save_if_best(self, model, metric, filepath):
        if metric < self.best_metric:
            self.best_metric = metric
            save_checkpoint(model, filepath)
            return True
        return False
```

## 🎯 Best Practices Checklist

- [ ] Save checkpoints at regular intervals
- [ ] Include metadata (timestamp, version, etc.)
- [ ] Validate data before saving and after loading
- [ ] Handle errors gracefully
- [ ] Use atomic saves (temp file → move)
- [ ] Implement cleanup for old checkpoints
- [ ] Compress large checkpoints
- [ ] Document checkpoint format
- [ ] Test recovery scenarios
- [ ] Version your checkpoint format

## ⚠️ Common Mistakes

### ❌ Don't Do This

```python
# No error handling
def save(state):
    with open('checkpoint.json', 'w') as f:
        json.dump(state, f)  # What if disk is full?

# Blocking on large saves
save_checkpoint(huge_state)  # UI freezes

# No version tracking
save_checkpoint(state)  # Can't track which version

# Unlimited checkpoints
while True:
    save_checkpoint(state)  # Fills disk!
```

### ✅ Do This Instead

```python
# With error handling
def save(state):
    try:
        with tempfile.NamedTemporaryFile('w', delete=False) as tmp:
            json.dump(state, tmp)
            tmp_path = tmp.name
        shutil.move(tmp_path, 'checkpoint.json')
        return True
    except Exception as e:
        print(f"Save failed: {e}")
        return False

# Async save
async def save_async(state):
    await asyncio.to_thread(save, state)

# With version
checkpoint = {
    'version': '1.0',
    'timestamp': datetime.now().isoformat(),
    'data': state
}

# With rotation
def save_with_rotation(state, max_count=10):
    save(state)
    cleanup_old_checkpoints(max_count)
```

## 📊 Decision Tree

**When to use which checkpoint strategy?**

```
Do you need undo/redo?
├─ Yes → Use History Pattern
└─ No
    ├─ Is the state large?
    │   ├─ Yes → Use Incremental/Compressed checkpoints
    │   └─ No → Use Simple file-based checkpoints
    └─ Do you need real-time saves?
        ├─ Yes → Use Auto-save pattern
        └─ No → Manual checkpoint triggering
```

## 🔍 Debugging Checkpoints

### Check if checkpoint exists

```python
import os
if os.path.exists('checkpoint.json'):
    print("Checkpoint found")
else:
    print("No checkpoint")
```

### Validate checkpoint

```python
def validate_checkpoint(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        required_keys = ['version', 'timestamp', 'data']
        for key in required_keys:
            if key not in data:
                return False, f"Missing key: {key}"
        
        return True, "Valid"
    except Exception as e:
        return False, str(e)
```

### Inspect checkpoint

```python
import json
with open('checkpoint.json', 'r') as f:
    checkpoint = json.load(f)
    print(json.dumps(checkpoint, indent=2))
```

## 📚 Related Concepts

- **Memento Pattern**: Design pattern for checkpoints
- **Event Sourcing**: Store all changes as events
- **CQRS**: Command Query Responsibility Segregation
- **WAL**: Write-Ahead Logging (databases)
- **Snapshot Testing**: Testing using saved states
- **State Machine**: Managing application states

## 🔗 Resources

### Documentation
- [Getting Started Guide](getting-started.md)
- [Database Checkpoints](database-checkpoints.md)
- [ML Checkpoints](ml-checkpoints.md)
- [App Checkpoints](app-checkpoints.md)
- [Design Patterns](checkpoint-patterns.md)

### Examples
- [Simple Checkpoint](../examples/simple_checkpoint.py)
- [ML Training](../examples/ml_training_checkpoint.py)
- [JavaScript Example](../examples/checkpoint_example.js)

## 💡 Tips

1. **Start Simple**: Begin with basic save/load, add features as needed
2. **Test Early**: Test recovery scenarios from the beginning
3. **Be Consistent**: Use consistent naming and structure
4. **Document Format**: Document your checkpoint format for future reference
5. **Version Everything**: Include version numbers in checkpoints
6. **Think About Size**: Consider compression for large states
7. **Plan for Migration**: Design for format changes over time
8. **Monitor Performance**: Track checkpoint save/load times
9. **Secure Sensitive Data**: Encrypt checkpoints with sensitive information
10. **Automate Testing**: Create tests for checkpoint functionality

## 🎓 Learning Path

1. **Beginner**: Start with [Getting Started](getting-started.md)
2. **Intermediate**: Study [Design Patterns](checkpoint-patterns.md)
3. **Advanced**: Explore domain-specific implementations
   - [Database Checkpoints](database-checkpoints.md)
   - [ML Checkpoints](ml-checkpoints.md)
   - [App Checkpoints](app-checkpoints.md)
4. **Practice**: Build projects using the [examples](../examples/)

---

**Need help?** Check the [documentation](../docs/) or explore the [examples](../examples/)!

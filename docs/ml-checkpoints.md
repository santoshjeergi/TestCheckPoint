# Machine Learning Model Checkpoints

## Overview

In machine learning, checkpoints are saved snapshots of a model's state during training. They allow you to:
- Resume training if interrupted
- Save the best model during training
- Experiment with different training strategies
- Deploy models at specific training stages

## Why ML Checkpoints Are Essential

1. **Training Interruption**: Resume from where you left off if training crashes
2. **Best Model Selection**: Save the model with best validation performance
3. **Resource Optimization**: Don't waste GPU hours retraining from scratch
4. **Experimentation**: Compare models from different epochs
5. **Production Deployment**: Use the best checkpoint for inference

## What Gets Saved in a Checkpoint?

A complete checkpoint typically includes:
- Model weights and architecture
- Optimizer state
- Learning rate scheduler state
- Current epoch/step number
- Training metrics history
- Random state for reproducibility

## Framework-Specific Examples

### PyTorch Checkpoints

```python
import torch
import torch.nn as nn
import torch.optim as optim

# Define a simple model
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# Training setup
model = SimpleModel()
optimizer = optim.Adam(model.parameters(), lr=0.001)
epoch = 0
best_loss = float('inf')

# Save checkpoint
def save_checkpoint(model, optimizer, epoch, loss, filepath):
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }
    torch.save(checkpoint, filepath)
    print(f"Checkpoint saved at epoch {epoch}")

# Load checkpoint
def load_checkpoint(model, optimizer, filepath):
    checkpoint = torch.load(filepath)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    loss = checkpoint['loss']
    print(f"Checkpoint loaded from epoch {epoch}")
    return epoch, loss

# Usage during training
for epoch in range(100):
    # Training code here
    train_loss = 0.5  # placeholder
    
    # Save checkpoint every 10 epochs
    if epoch % 10 == 0:
        save_checkpoint(model, optimizer, epoch, train_loss, 
                       f'checkpoint_epoch_{epoch}.pth')
    
    # Save best model
    if train_loss < best_loss:
        best_loss = train_loss
        save_checkpoint(model, optimizer, epoch, train_loss, 
                       'best_model.pth')
```

### TensorFlow/Keras Checkpoints

```python
import tensorflow as tf
from tensorflow import keras

# Define model
model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(784,)),
    keras.layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Checkpoint callback - saves best model
checkpoint_callback = keras.callbacks.ModelCheckpoint(
    filepath='model_checkpoint.h5',
    save_best_only=True,
    monitor='val_loss',
    mode='min',
    verbose=1
)

# Checkpoint callback - saves every epoch
checkpoint_callback_all = keras.callbacks.ModelCheckpoint(
    filepath='checkpoint_epoch_{epoch:02d}.h5',
    save_freq='epoch',
    verbose=1
)

# Custom checkpoint callback for more control
class CustomCheckpoint(keras.callbacks.Callback):
    def __init__(self, filepath):
        super(CustomCheckpoint, self).__init__()
        self.filepath = filepath
    
    def on_epoch_end(self, epoch, logs=None):
        if epoch % 5 == 0:  # Save every 5 epochs
            self.model.save_weights(
                self.filepath.format(epoch=epoch)
            )
            print(f"\nSaved checkpoint at epoch {epoch}")

# Training with checkpoints
# model.fit(x_train, y_train, 
#           epochs=50, 
#           validation_data=(x_val, y_val),
#           callbacks=[checkpoint_callback])

# Load checkpoint
# model = keras.models.load_model('model_checkpoint.h5')
```

### Hugging Face Transformers

```python
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer

# Model setup
model = AutoModelForSequenceClassification.from_pretrained('bert-base-uncased')

# Training arguments with checkpoint configuration
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    save_steps=500,                 # Save checkpoint every 500 steps
    save_total_limit=2,             # Keep only 2 most recent checkpoints
    load_best_model_at_end=True,    # Load best model at end
    metric_for_best_model='accuracy',
    evaluation_strategy='steps',
    eval_steps=500,
)

# Trainer automatically handles checkpointing
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=eval_dataset,
# )

# Resume from checkpoint
# trainer.train(resume_from_checkpoint='./results/checkpoint-1000')
```

## Best Practices

### 1. Save Strategy
```python
# Save multiple types of checkpoints
- Regular intervals (every N epochs)
- Best model (based on validation metric)
- Last model (most recent state)
- Milestone checkpoints (end of each phase)
```

### 2. Checkpoint Naming
```python
# Use descriptive names with metadata
'model_epoch{epoch:03d}_loss{loss:.4f}.pth'
'checkpoint_2024-01-15_14-30-00.h5'
'best_model_acc0.95.pth'
```

### 3. Storage Management
```python
# Keep limited number of checkpoints
save_total_limit = 3  # Keep only 3 most recent

# Delete old checkpoints
import os
import glob

def cleanup_old_checkpoints(directory, keep_last=3):
    checkpoints = sorted(glob.glob(f'{directory}/checkpoint_*.pth'))
    for checkpoint in checkpoints[:-keep_last]:
        os.remove(checkpoint)
```

### 4. Validation Before Saving
```python
# Only save if validation improves
if val_loss < best_val_loss:
    save_checkpoint(model, optimizer, epoch, val_loss, 'best_model.pth')
    best_val_loss = val_loss
```

### 5. Include Metadata
```python
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'best_loss': best_loss,
    'training_config': config,
    'timestamp': datetime.now().isoformat(),
    'random_state': random.getstate(),
}
```

## Common Patterns

### Early Stopping with Checkpoints
```python
class EarlyStoppingWithCheckpoint:
    def __init__(self, patience=5, delta=0):
        self.patience = patience
        self.delta = delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
    
    def __call__(self, val_loss, model, path):
        if self.best_loss is None:
            self.best_loss = val_loss
            save_checkpoint(model, path)
        elif val_loss > self.best_loss - self.delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            save_checkpoint(model, path)
            self.counter = 0
```

### Distributed Training Checkpoints
```python
# Save only from main process
if torch.distributed.get_rank() == 0:
    save_checkpoint(model, optimizer, epoch, loss, filepath)
```

## Exercises

1. Implement a training loop with checkpoint saving every 5 epochs
2. Create a callback that saves only when validation accuracy improves
3. Write a function to resume training from the last checkpoint
4. Implement checkpoint cleanup to keep only the 3 best models
5. Add checkpointing to a multi-GPU training setup

## Troubleshooting

### Issue: Checkpoint Files Too Large
**Solution**: Save only model weights, not optimizer state if not resuming training
```python
torch.save(model.state_dict(), 'model_weights_only.pth')
```

### Issue: Can't Resume Training
**Solution**: Ensure you save and load all necessary components
```python
# Must include optimizer, scheduler, and epoch
checkpoint = {
    'model': model.state_dict(),
    'optimizer': optimizer.state_dict(),
    'scheduler': scheduler.state_dict(),
    'epoch': epoch,
}
```

## Additional Resources

- [PyTorch: Saving and Loading Models](https://pytorch.org/tutorials/beginner/saving_loading_models.html)
- [TensorFlow: Save and Load Models](https://www.tensorflow.org/tutorials/keras/save_and_load)
- [Hugging Face: Training and Fine-tuning](https://huggingface.co/docs/transformers/training)

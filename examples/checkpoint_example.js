// Checkpoint Example in JavaScript/Node.js
// Demonstrates checkpoint implementation for a simple application

const fs = require('fs').promises;
const path = require('path');

/**
 * Application state manager with checkpoint support
 */
class ApplicationCheckpoint {
    constructor(checkpointDir = 'checkpoints') {
        this.checkpointDir = checkpointDir;
        this.state = {};
        this.history = [];
        this.maxHistory = 10;
    }

    /**
     * Initialize checkpoint directory
     */
    async initialize() {
        try {
            await fs.mkdir(this.checkpointDir, { recursive: true });
            console.log('✓ Checkpoint directory initialized');
        } catch (error) {
            console.error('✗ Failed to initialize checkpoint directory:', error.message);
        }
    }

    /**
     * Save current state to a checkpoint
     */
    async saveCheckpoint(name = null) {
        const timestamp = new Date().toISOString();
        const checkpointName = name || `checkpoint_${Date.now()}`;

        const checkpoint = {
            name: checkpointName,
            timestamp: timestamp,
            state: JSON.parse(JSON.stringify(this.state)) // Deep clone
        };

        try {
            const filepath = path.join(this.checkpointDir, `${checkpointName}.json`);
            await fs.writeFile(filepath, JSON.stringify(checkpoint, null, 2));
            
            console.log(`✓ Checkpoint saved: ${checkpointName}`);
            
            // Add to history
            this.history.push({
                name: checkpointName,
                timestamp: timestamp,
                filepath: filepath
            });

            // Cleanup old checkpoints
            if (this.history.length > this.maxHistory) {
                await this.cleanupOldCheckpoints();
            }

            return checkpointName;
        } catch (error) {
            console.error('✗ Failed to save checkpoint:', error.message);
            return null;
        }
    }

    /**
     * Load state from a checkpoint
     */
    async loadCheckpoint(name) {
        try {
            const filepath = path.join(this.checkpointDir, `${name}.json`);
            const data = await fs.readFile(filepath, 'utf-8');
            const checkpoint = JSON.parse(data);

            this.state = checkpoint.state;
            console.log(`✓ Checkpoint loaded: ${name}`);
            console.log(`  Saved at: ${checkpoint.timestamp}`);

            return true;
        } catch (error) {
            console.error(`✗ Failed to load checkpoint ${name}:`, error.message);
            return false;
        }
    }

    /**
     * List all available checkpoints
     */
    async listCheckpoints() {
        try {
            const files = await fs.readdir(this.checkpointDir);
            const checkpoints = [];

            for (const file of files) {
                if (file.endsWith('.json')) {
                    const filepath = path.join(this.checkpointDir, file);
                    const data = await fs.readFile(filepath, 'utf-8');
                    const checkpoint = JSON.parse(data);
                    checkpoints.push({
                        name: checkpoint.name,
                        timestamp: checkpoint.timestamp,
                        file: file
                    });
                }
            }

            return checkpoints.sort((a, b) => 
                new Date(b.timestamp) - new Date(a.timestamp)
            );
        } catch (error) {
            console.error('✗ Failed to list checkpoints:', error.message);
            return [];
        }
    }

    /**
     * Delete a specific checkpoint
     */
    async deleteCheckpoint(name) {
        try {
            const filepath = path.join(this.checkpointDir, `${name}.json`);
            await fs.unlink(filepath);
            console.log(`✓ Deleted checkpoint: ${name}`);
            return true;
        } catch (error) {
            console.error(`✗ Failed to delete checkpoint ${name}:`, error.message);
            return false;
        }
    }

    /**
     * Cleanup old checkpoints, keeping only the most recent ones
     */
    async cleanupOldCheckpoints() {
        const checkpoints = await this.listCheckpoints();
        
        if (checkpoints.length > this.maxHistory) {
            const toDelete = checkpoints.slice(this.maxHistory);
            
            for (const checkpoint of toDelete) {
                await this.deleteCheckpoint(checkpoint.name);
            }
            
            console.log(`✓ Cleaned up ${toDelete.length} old checkpoints`);
        }
    }

    /**
     * Update application state
     */
    setState(newState) {
        this.state = { ...this.state, ...newState };
    }

    /**
     * Get current state
     */
    getState() {
        return { ...this.state };
    }
}

/**
 * Auto-save functionality
 */
class AutoSaveManager {
    constructor(checkpointManager, intervalSeconds = 60) {
        this.checkpointManager = checkpointManager;
        this.interval = intervalSeconds * 1000;
        this.timer = null;
        this.enabled = false;
    }

    start() {
        if (this.enabled) {
            console.log('Auto-save already running');
            return;
        }

        this.enabled = true;
        console.log(`✓ Auto-save enabled (every ${this.interval / 1000}s)`);

        this.timer = setInterval(async () => {
            console.log('\n[Auto-save triggered]');
            await this.checkpointManager.saveCheckpoint('autosave');
        }, this.interval);
    }

    stop() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
            this.enabled = false;
            console.log('✓ Auto-save disabled');
        }
    }
}

/**
 * Demo function
 */
async function demo() {
    console.log('=== Checkpoint Demo ===\n');

    // Create checkpoint manager
    const checkpoint = new ApplicationCheckpoint('demo_checkpoints');
    await checkpoint.initialize();

    // Set initial state
    checkpoint.setState({
        user: 'Alice',
        score: 0,
        level: 1,
        items: ['sword']
    });

    console.log('\nInitial state:', checkpoint.getState());

    // Save checkpoint
    await checkpoint.saveCheckpoint('game_start');

    // Simulate progress
    console.log('\n--- Game Progress ---');
    checkpoint.setState({
        score: 100,
        level: 2,
        items: ['sword', 'shield']
    });

    console.log('After progress:', checkpoint.getState());
    await checkpoint.saveCheckpoint('level_2');

    // More progress
    checkpoint.setState({
        score: 250,
        level: 3,
        items: ['sword', 'shield', 'potion']
    });

    console.log('After more progress:', checkpoint.getState());
    await checkpoint.saveCheckpoint('level_3');

    // List checkpoints
    console.log('\n--- Available Checkpoints ---');
    const checkpoints = await checkpoint.listCheckpoints();
    checkpoints.forEach((cp, index) => {
        console.log(`${index + 1}. ${cp.name} (${cp.timestamp})`);
    });

    // Load earlier checkpoint
    console.log('\n--- Loading Earlier Checkpoint ---');
    await checkpoint.loadCheckpoint('level_2');
    console.log('Restored state:', checkpoint.getState());

    // Demonstrate auto-save
    console.log('\n--- Auto-Save Demo ---');
    const autoSave = new AutoSaveManager(checkpoint, 2); // Every 2 seconds
    
    autoSave.start();
    
    // Simulate some activity
    setTimeout(() => {
        checkpoint.setState({ score: 300 });
        console.log('State updated:', checkpoint.getState());
    }, 3000);

    setTimeout(() => {
        checkpoint.setState({ score: 400, level: 4 });
        console.log('State updated:', checkpoint.getState());
    }, 5000);

    setTimeout(() => {
        autoSave.stop();
        console.log('\n=== Demo Complete ===');
    }, 7000);
}

/**
 * Example of undo/redo functionality
 */
class UndoRedoCheckpoint {
    constructor() {
        this.history = [];
        this.currentIndex = -1;
    }

    saveState(state) {
        // Remove any states after current index
        this.history = this.history.slice(0, this.currentIndex + 1);
        
        // Add new state
        this.history.push(JSON.parse(JSON.stringify(state)));
        this.currentIndex++;

        console.log(`State saved (${this.currentIndex + 1} states in history)`);
    }

    undo() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            console.log(`Undo: moved to state ${this.currentIndex + 1}`);
            return JSON.parse(JSON.stringify(this.history[this.currentIndex]));
        }
        console.log('Nothing to undo');
        return null;
    }

    redo() {
        if (this.currentIndex < this.history.length - 1) {
            this.currentIndex++;
            console.log(`Redo: moved to state ${this.currentIndex + 1}`);
            return JSON.parse(JSON.stringify(this.history[this.currentIndex]));
        }
        console.log('Nothing to redo');
        return null;
    }

    getCurrentState() {
        return this.currentIndex >= 0 
            ? JSON.parse(JSON.stringify(this.history[this.currentIndex]))
            : null;
    }
}

/**
 * Undo/Redo demo
 */
async function undoRedoDemo() {
    console.log('\n=== Undo/Redo Demo ===\n');

    const checkpoint = new UndoRedoCheckpoint();

    // Save states
    checkpoint.saveState({ text: 'Hello' });
    checkpoint.saveState({ text: 'Hello World' });
    checkpoint.saveState({ text: 'Hello World!' });

    console.log('Current:', checkpoint.getCurrentState());

    // Undo
    let state = checkpoint.undo();
    console.log('After undo:', state);

    state = checkpoint.undo();
    console.log('After undo:', state);

    // Redo
    state = checkpoint.redo();
    console.log('After redo:', state);
}

// Run demos
if (require.main === module) {
    (async () => {
        await demo();
        await undoRedoDemo();
    })();
}

module.exports = {
    ApplicationCheckpoint,
    AutoSaveManager,
    UndoRedoCheckpoint
};

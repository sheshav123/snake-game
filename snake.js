// Snake Game JavaScript Implementation
class SnakeGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.scoreElement = document.getElementById('score');
        this.gameOverElement = document.getElementById('gameOver');
        this.finalScoreElement = document.getElementById('finalScore');
        
        // Game constants
        this.GRID_SIZE = 20;
        this.GRID_WIDTH = this.canvas.width / this.GRID_SIZE;
        this.GRID_HEIGHT = this.canvas.height / this.GRID_SIZE;
        
        // Colors
        this.colors = {
            background: '#000000',
            snake: '#00FF00',
            snakeHead: '#00CC00',
            food: '#FF0000',
            grid: '#333333'
        };
        
        // Game state
        this.reset();
        
        // Event listeners
        this.setupEventListeners();
        
        // Start game loop
        this.gameLoop();
    }
    
    reset() {
        this.direction = { x: 1, y: 0 };
        this.nextDirection = { x: 1, y: 0 };
        this.snake = [
            { x: Math.floor(this.GRID_WIDTH / 2), y: Math.floor(this.GRID_HEIGHT / 2) },
            { x: Math.floor(this.GRID_WIDTH / 2) - 1, y: Math.floor(this.GRID_HEIGHT / 2) }
        ];
        this.food = this.generateFood();
        this.score = 0;
        this.gameOver = false;
        this.paused = false;
        this.lastMoveTime = 0;
        this.moveInterval = 150; // milliseconds
        
        this.updateScore();
        this.gameOverElement.style.display = 'none';
    }
    
    generateFood() {
        let food;
        do {
            food = {
                x: Math.floor(Math.random() * this.GRID_WIDTH),
                y: Math.floor(Math.random() * this.GRID_HEIGHT)
            };
        } while (this.snake.some(segment => segment.x === food.x && segment.y === food.y));
        
        return food;
    }
    
    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            if (this.gameOver || this.paused) {
                if (e.code === 'Space') {
                    this.togglePause();
                }
                return;
            }
            
            switch (e.code) {
                case 'ArrowUp':
                    if (this.direction.y !== 1) {
                        this.nextDirection = { x: 0, y: -1 };
                    }
                    break;
                case 'ArrowDown':
                    if (this.direction.y !== -1) {
                        this.nextDirection = { x: 0, y: 1 };
                    }
                    break;
                case 'ArrowLeft':
                    if (this.direction.x !== 1) {
                        this.nextDirection = { x: -1, y: 0 };
                    }
                    break;
                case 'ArrowRight':
                    if (this.direction.x !== -1) {
                        this.nextDirection = { x: 1, y: 0 };
                    }
                    break;
                case 'Space':
                    this.togglePause();
                    break;
            }
            e.preventDefault();
        });
    }
    
    update(currentTime) {
        if (this.gameOver || this.paused) return;
        
        if (currentTime - this.lastMoveTime < this.moveInterval) return;
        
        this.lastMoveTime = currentTime;
        
        // Update direction
        this.direction = { ...this.nextDirection };
        
        // Calculate new head position
        const head = { ...this.snake[0] };
        head.x += this.direction.x;
        head.y += this.direction.y;
        
        // Wrap around screen edges
        head.x = (head.x + this.GRID_WIDTH) % this.GRID_WIDTH;
        head.y = (head.y + this.GRID_HEIGHT) % this.GRID_HEIGHT;
        
        // Check collision with self
        if (this.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
            this.gameOver = true;
            this.showGameOver();
            return;
        }
        
        // Add new head
        this.snake.unshift(head);
        
        // Check if food is eaten
        if (head.x === this.food.x && head.y === this.food.y) {
            this.score++;
            this.updateScore();
            this.food = this.generateFood();
            
            // Increase speed slightly
            this.moveInterval = Math.max(80, this.moveInterval - 2);
        } else {
            // Remove tail if no food eaten
            this.snake.pop();
        }
    }
    
    draw() {
        // Clear canvas
        this.ctx.fillStyle = this.colors.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid
        this.ctx.strokeStyle = this.colors.grid;
        this.ctx.lineWidth = 1;
        for (let x = 0; x <= this.canvas.width; x += this.GRID_SIZE) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = 0; y <= this.canvas.height; y += this.GRID_SIZE) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
        
        // Draw snake
        this.snake.forEach((segment, index) => {
            this.ctx.fillStyle = index === 0 ? this.colors.snakeHead : this.colors.snake;
            this.ctx.fillRect(
                segment.x * this.GRID_SIZE,
                segment.y * this.GRID_SIZE,
                this.GRID_SIZE,
                this.GRID_SIZE
            );
            
            // Add border to snake segments
            this.ctx.strokeStyle = '#006600';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(
                segment.x * this.GRID_SIZE,
                segment.y * this.GRID_SIZE,
                this.GRID_SIZE,
                this.GRID_SIZE
            );
        });
        
        // Draw food
        this.ctx.fillStyle = this.colors.food;
        this.ctx.fillRect(
            this.food.x * this.GRID_SIZE,
            this.food.y * this.GRID_SIZE,
            this.GRID_SIZE,
            this.GRID_SIZE
        );
        
        // Draw pause message
        if (this.paused && !this.gameOver) {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            this.ctx.fillStyle = 'white';
            this.ctx.font = '30px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('PAUSED', this.canvas.width / 2, this.canvas.height / 2);
            this.ctx.fillText('Press SPACE to continue', this.canvas.width / 2, this.canvas.height / 2 + 40);
        }
    }
    
    gameLoop(currentTime = 0) {
        this.update(currentTime);
        this.draw();
        requestAnimationFrame((time) => this.gameLoop(time));
    }
    
    updateScore() {
        this.scoreElement.textContent = this.score;
    }
    
    showGameOver() {
        this.finalScoreElement.textContent = this.score;
        this.gameOverElement.style.display = 'block';
    }
    
    togglePause() {
        if (!this.gameOver) {
            this.paused = !this.paused;
        }
    }
    
    restart() {
        this.reset();
    }
}

// Global functions for HTML buttons
let game;

function togglePause() {
    if (game) {
        game.togglePause();
    }
}

function restartGame() {
    if (game) {
        game.restart();
    }
}

// Start the game when page loads
window.addEventListener('load', () => {
    game = new SnakeGame();
});
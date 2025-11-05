# 🐍 Snake Game

A classic Snake game implementation available in both Python (pygame) and Web (HTML5 Canvas) versions.

## 🎮 Play Online

**[Play the game here!](https://yourusername.github.io/snake-game)**

## 🚀 Features

- **Smooth gameplay** with responsive controls
- **Score tracking** with increasing difficulty
- **Pause/Resume** functionality
- **Wrap-around edges** - snake appears on opposite side when hitting boundaries
- **Clean, modern UI** with grid visualization
- **Cross-platform** - Python desktop version and web browser version

## 🎯 How to Play

### Controls
- **Arrow Keys**: Move the snake (Up, Down, Left, Right)
- **Spacebar**: Pause/Resume the game
- **R Key**: Restart game (when game over)
- **P Key**: Pause/Resume (Python version)
- **ESC**: Exit game (Python version)

### Objective
- Control the snake to eat the red food
- Each food eaten increases your score and snake length
- Avoid hitting the snake's own body
- The game gets faster as your score increases

## 💻 Local Installation

### Python Version (Desktop)

#### Requirements
- Python 3.6+
- pygame library

#### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/snake-game.git
cd snake-game

# Install pygame
pip install pygame

# Run the game
python "snake_game copy2.py"
```

### Web Version (Browser)

Simply open `index.html` in any modern web browser, or visit the GitHub Pages link above.

## 🛠️ Technical Details

### Python Version
- Built with **pygame** library
- Object-oriented design with clean separation of concerns
- Enum-based direction system for better code organization
- Modular game state management

### Web Version
- Pure **HTML5 Canvas** and **JavaScript**
- Responsive design that works on desktop and mobile
- Smooth animations using `requestAnimationFrame`
- Modern ES6+ JavaScript features

## 📁 Project Structure

```
snake-game/
├── snake_game copy2.py    # Python/pygame version
├── index.html             # Web version HTML
├── snake.js              # Web version JavaScript
├── README.md             # This file
└── docs/                 # Additional documentation
```

## 🎨 Customization

The game is easily customizable:

- **Colors**: Modify color constants in either version
- **Speed**: Adjust FPS (Python) or moveInterval (JavaScript)
- **Grid Size**: Change GRID_SIZE for different game scales
- **Window Size**: Modify WINDOW_WIDTH and WINDOW_HEIGHT

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🎯 Future Enhancements

- [ ] High score persistence
- [ ] Multiple difficulty levels
- [ ] Power-ups and special foods
- [ ] Multiplayer mode
- [ ] Mobile touch controls
- [ ] Sound effects and music
- [ ] Different game modes (walls, obstacles)

## 📞 Contact

Created by [Your Name] - feel free to contact me!

---

⭐ **Star this repository if you enjoyed the game!** ⭐
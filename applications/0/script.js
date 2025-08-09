document.addEventListener('DOMContentLoaded', () => {
    const cells = document.querySelectorAll('.cell');
    const gameStatus = document.querySelector('.game-status');
    const resetButton = document.querySelector('.reset-button');
    let currentPlayer = 'X';
    let gameActive = true;
    let gameState = ['', '', '', '', '', '', '', '', ''];

    const winningConditions = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
    ];

    cells.forEach(cell => {
        cell.addEventListener('click', () => {
            const cellIndex = parseInt(cell.getAttribute('data-index'));

            if (gameState[cellIndex] !== '' || !gameActive) {
                return;
            }

            gameState[cellIndex] = currentPlayer;
            cell.textContent = currentPlayer;

            checkForWin();
            checkForDraw();
            currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
        });
    });

    resetButton.addEventListener('click', resetGame);

    function checkForWin() {
        for (let condition of winningConditions) {
            if (gameState[condition[0]] !== '' &&
                gameState[condition[0]] === gameState[condition[1]] &&
                gameState[condition[1]] === gameState[condition[2]]) {
                gameStatus.textContent = `Player ${gameState[condition[0]]} wins!`;
                gameActive = false;
                return;
            }
        }
    }

    function checkForDraw() {
        if (!gameState.includes('') && gameActive) {
            gameStatus.textContent = 'It\'s a draw!';
            gameActive = false;
        }
    }

    function resetGame() {
        gameActive = true;
        currentPlayer = 'X';
        gameState = ['', '', '', '', '', '', '', '', ''];
        cells.forEach(cell => cell.textContent = '');
        gameStatus.textContent = '';
    }
});

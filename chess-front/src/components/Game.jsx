import { useState, useEffect } from 'react';
import config from '../config'
import { useParams } from "react-router-dom";


function Game() {
    const [isGameLoaded, setIsGameLoaded] = useState(false);
    const [board, setBoard] = useState(null);
    const { gameid } = useParams();

    useEffect(() => {
        const ws = new WebSocket(`${config.WS_BASE_URL}ws/game/${gameid}`);

        ws.onopen = () => {
            console.log("connected to game");
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data)
            if (data.action === 'game_ready') {
                console.log("game loaded");
                setIsGameLoaded(true);
                generateBoard(data.board)
            };
        };

        ws.onerror = (error) => {
            console.log("WebSocket error: ", error);
        };

    }, [gameid]);

    const generateBoard = (boardData) => {
        const display_board = []
        for (let i = 0; i < boardData.length; i++) {
            for (let j = 0; j < boardData[i].length; j++) {

                let color = null
                const code = boardData[i][j][0]

                if (code === "N") {
                    if ((i + j) % 2 !== 0) {
                        color = 'bg-black';
                    }
                    else {
                        color = 'bg-white';
                    }
                }
                else if (code === "P1") {
                    color = 'bg-red-500';
                }
                else if (code === "P2") {
                    color = 'bg-green-500';
                }
                else if (code === "K") {
                    color = 'bg-yellow-500';
                }

                display_board.push(
                    <div
                        key={`${i}-${j}`}
                        className={`w-16 h-16 ${color}`}
                        onClick={() => handleSelect(i, j)}
                    ></div>
                );
            }
        }
        console.log("board updated!", boardData)
        setBoard(display_board)
    }

    const handleSelect = (i, j) => {
        console.log(i, j)
    }

    return (
        <>
            <div className="min-h-screen bg-gray-900 flex items-center justify-center p-6 flex-col">
                <div className="grid grid-cols-8">
                    {board}
                </div>
            </div>
        </>
    )
}

export default Game;


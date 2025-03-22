import { useState, useEffect } from 'react';
import config from '../config'
import { useParams } from "react-router-dom";


function Game() {
    const [isGameLoaded, setIsGameLoaded] = useState(false);
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
            };
        };

        ws.onerror = (error) => {
            console.log("WebSocket error: ", error);
        };

    }, [gameid]);

    const board = "WBWBWBWBBWBWBWBWWBWBWBWBBWBWBWBWWBWBWBWBBWBWBWBWWBWBWBWBBWBWBWBW";

    const GenerateBoard = (board) => {
        const display_board = []
        for (let i = 0; i < board.length; i++) {
            const isBlack = board[i] === 'B';
            display_board.push(
                <div
                    key={i}
                    className={`w-16 h-16 ${isBlack ? 'bg-black' : 'bg-white'}`}
                ></div>
            );
        }
        return display_board
    }

    return (
        <>
            <div className="min-h-screen bg-gray-900 flex items-center justify-center p-6 flex-col">
                <div className="grid grid-cols-8">
                    {GenerateBoard(board)}
                </div>
            </div>
        </>
    )
}

export default Game;


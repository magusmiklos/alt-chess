import { useState, useEffect, useRef } from 'react';
import config from '../config'
import { useParams } from "react-router-dom";
import Bpawn from '../assets/Bpawn.png';
import Wpawn from '../assets/Wpawn.png';
import Brook from "../assets/Brook.png";
import Wrook from "../assets/Wrook.png";
import Bbishop from "../assets/Bbishop.png";
import Wbishop from "../assets/Wbishop.png";
import Bking from "../assets/Bking.png";
import Wking from "../assets/Wking.png";
import Bhorse from "../assets/Bhorse.png";
import Whorse from "../assets/Whorse.png";
import Gking from "../assets/Gking.png";

function Game() {
    const [isGameLoaded, setIsGameLoaded] = useState(false);
    const [board, setBoard] = useState(null);
    const [playerOrder, setPlayerOrder] = useState(null);
    const [UIItems, setUIItems] = useState([]);
    const [selectedPiece, setSelectedPiece] = useState(0);
    const [moves, setMoves] = useState([]);
    const [turn, setTurn] = useState(true);

    const { gameid } = useParams();
    const wsRef = useRef(null);
    useEffect(() => {
        console.log("reload ws")
        if (!wsRef.current) {
            const ws = new WebSocket(`${config.WS_BASE_URL}ws/game/${gameid}`);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log("connected to game");
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data)
                if (data.action === 'game_ready') {
                    console.log("game loaded you're player order:", data.order);
                    console.log(data)
                    setIsGameLoaded(true);
                    generateBoard(data.board)
                    setPlayerOrder(data.order)
                    if (data.order) {
                        setUIItems([Wpawn, Whorse, Wbishop, Wrook])
                    }
                    else {
                        setUIItems([Bpawn, Bhorse, Bbishop, Brook])
                    }
                };
                if (data.action === "board_update") {
                    console.log("board update action recived");
                    generateBoard(data.board)

                }
            };

            ws.onerror = (error) => {
                console.log("WebSocket error: ", error);
            };

            ws.onclose = (event) => {
                console.log("WebSocket closed: ", event);
            };


        }
    }, [gameid]);

    const generateBoard = (boardData) => {
        const display_board = []
        for (let i = 0; i < boardData.length; i++) {
            for (let j = 0; j < boardData[i].length; j++) {

                let color = null
                const code = boardData[i][j][0]
                let piece = null
                let money = null

                if ((i + j) % 2 !== 0) {
                    color = 'bg-gray-600';
                }
                else {
                    color = 'bg-white';
                }

                if (code === "P1") {
                    piece = Wpawn
                    money = boardData[i][j][1]
                }
                else if (code === "P2") {
                    piece = Bpawn
                    money = boardData[i][j][1]
                }
                else if (code === "K") {
                    piece = Gking
                }


                display_board.push(
                    <div
                        key={`${i}-${j}`}
                        className={`w-16 h-16 ${color} flex justify-center items-center relative`}
                        onClick={() => handleSelect(i, j)}
                    >
                        {piece && (<><img src={piece} alt={`Piece at ${i},${j}`} className="w-16 h-16" /><p className="absolute bottom-1 text-xl text-green-500 font-bold">{money}</p></>)}
                    </div>
                );
            }
        }
        console.log("board updated!", boardData)
        setBoard(display_board)
    }

    const handleSelect = (i, j) => {
        setMoves((prevMoves) => [...prevMoves, [i, j]]);
    }

    const handleSelectPiece = (index) => {
        setSelectedPiece(index);
    }

    const handleMove = () => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            const message = {
                action: "move",
                move: moves.slice(-2),
                piece: selectedPiece,
            }

            wsRef.current.send(JSON.stringify(message));
            console.log("sent move to ws")
        }
    }

    return (
        <>
            <div className="min-h-screen bg-gray-900 flex items-center justify-center p-6 flex-col">
                <div className="flex justify-end items-center w-full"><div className={`w-10 h-10 rounded-full ${turn ? "bg-white" : "bg-black"}`} /></div>
                <div className="grid grid-cols-8">
                    {board}
                </div>
                <button onClick={handleMove} className="mt-4 px-6 py-3 bg-gradient-to-r from-gray-800 to-slate-800 text-white font-bold text-lg rounded-2xl">
                    Move
                </button>
                <div className="flex felx-row mt-5">
                    {UIItems.map((item, index) => (
                        <div key={`piece-${index}`} className="cursor-pointer select-none flex justify-center items-center flex-col" onClick={() => handleSelectPiece(index)}>
                            <img
                                src={item}
                                className={`pointer-events-none w-32 h-32 m-2 ${index === selectedPiece ? "outline outline-green-500 outline-5" : ""}`}
                            />
                            <p className="text-6xl text-green-500 font-extrabold mt-3">{index}</p>
                        </div>
                    ))}
                </div>
            </div >
        </>
    )
}

export default Game;


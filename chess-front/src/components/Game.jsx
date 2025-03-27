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
import { useNavigate, Link } from "react-router-dom";

function Game() {
    const [isGameLoaded, setIsGameLoaded] = useState(false);
    const [board, setBoard] = useState(null);
    const [playerOrder, setPlayerOrder] = useState(null);
    const [UIItems, setUIItems] = useState([]);
    const [selectedPiece, setSelectedPiece] = useState(0);
    const [moves, setMoves] = useState([]);
    const [turn, setTurn] = useState(true);
    const [error, setError] = useState(null);
    const [kings, setKings] = useState([]);
    const [gameOver, setGameOver] = useState(0);
    const [usernames, setUsernames] = useState(["Player1", "Player2"]);

    const { username, gameid } = useParams();
    const wsRef = useRef(null);
    useEffect(() => {
        console.log("reload ws")
        if (!wsRef.current) {
            const ws = new WebSocket(`${config.WS_BASE_URL}ws/game/${username}/${gameid}`);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log("connected to game");
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data)
                if (data.action === 'game_ready') {
                    console.log("game loaded you're player order:", data.order);
                    setIsGameLoaded(true);
                    generateBoard(data.board)
                    setPlayerOrder(data.order)
                    setUsernames(data.usernames)
                    console.log("usernames:", data.usernames)
                    if (data.order) {
                        setUIItems([Wpawn, Whorse, Wbishop, Wrook])
                    }
                    else {
                        setUIItems([Bpawn, Bhorse, Bbishop, Brook])
                    }
                };
                if (data.action === 'ready_all') {
                    console.log(data.usernames)
                    setUsernames(data.usernames)
                }
                if (data.action === "board_update") {
                    console.log("board update action recived, turn:", data.turn);
                    generateBoard(data.board);
                    setTurn(data.turn);
                    setKings(data.kings);
                    console.log("capcured kings:", data.kings)

                }
                if (data.action === "game_over") {
                    setGameOver(data.won);
                    console.log("game over player won:", data.won);
                }
                if (data.type === "error") {
                    setError(data.message);
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
                        className={` w-10 h-10 lg:w-16 lg:h-16 ${color} flex justify-center items-center relative`}
                        onClick={() => handleSelect(i, j)}
                    >
                        {piece && (<><img src={piece} alt={`Piece at ${i},${j}`} className=" w-10 h-10 lg:w-16 lg:h-16" /><p className="absolute lg:bottom-1 bottom-0 text-lx lg:text-xl text-green-500 font-bold">{money}</p></>)}
                    </div>
                );
            }
        }
        console.log("board updated!", boardData)
        setBoard(display_board)
    }

    const handleSelect = (i, j) => {
        console.log(i, j);
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
            setError(null);
        }
    }

    return (
        <div className="flex flex-col min-h-screen bg-gray-900">
            <div className="flex justify-end items-center w-full p-5">
                <Link className="text-white ml-5" to='/'>Exit</Link>
            </div>

            <div className="flex-grow flex items-center justify-center flex-col">
                <div>
                    <div className="flex flex-row">
                        {kings.map((item, index) => (
                            <img key={`King ${index}`} src={item === true ? Wking : Bking} alt={`King ${index}`} className=" w-10 h-10 lg:w-16 lg:h-16" />

                        ))}
                    </div>
                    <div className="flex flex-row w-full justify-between items-center my-1">
                        <div className="text-white font-bold">{usernames && usernames.length > 1 && `${usernames[0]} Vs ${usernames[1]}`}</div>
                        <div className={`w-5 h-5 rounded-full ${turn ? "bg-white" : "bg-black"}`} />
                    </div>

                    <div className="relative">
                        <div className="grid grid-cols-8">
                            {board}

                        </div>

                        {gameOver !== 0 && (
                            <div className="absolute inset-0 flex justify-center items-center"><p className="font-bold text-6xl text-green-500">{gameOver === 1 ? ("White won") : ("Black won")}</p></div>)}
                    </div>
                </div>
                <button onClick={handleMove} className="mt-4 px-6 py-3 bg-gradient-to-r from-gray-800 to-slate-800 text-white font-bold text-lg rounded-2xl">
                    Move
                </button>
                {error && (<p className="text-red-500 text-lg">{error}</p>)}
                <div className="flex flex-row mt-5">
                    {UIItems.map((item, index) => (
                        <div key={`piece-${index}`} className="cursor-pointer select-none flex justify-center items-center flex-col" onClick={() => handleSelectPiece(index)}>
                            <img
                                src={item}
                                className={`pointer-events-none w-16 h-16 lg:w-24 lg:h-24 m-2 ${index === selectedPiece ? "outline outline-green-500 outline-5" : ""}`}
                            />
                            <p className="text-3xl lg:text-4xl text-green-500 font-extrabold mt-3">{index}</p>
                        </div>
                    ))}
                </div>
            </div >
        </div>
    )
}

export default Game;


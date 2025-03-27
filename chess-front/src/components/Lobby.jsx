import { useState } from 'react';
import config from '../config'
import { useNavigate } from "react-router-dom";

function Lobby() {
    const [username, setUsername] = useState("");
    const [titleText, setTitleText] = useState("Chess ♟️");
    const [isButtonDisabled, setIsButtonDisabled] = useState(false);

    const navigate = useNavigate();

    const handlePlay = (event) => {
        event.preventDefault();
        setIsButtonDisabled(true);

        const ws = new WebSocket(`${config.WS_BASE_URL}ws/matchmaking/`);

        ws.onopen = () => {
            console.log("connected to matchmaking");
            setTitleText("Waiting for an opponent ⏳")
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data)
            if (data.action === 'match_found') {
                console.log("found a match game_group: ", data.game_group);
                const gameid = data.game_group
                navigate(`/game/${username}/${gameid}`)
            };
        };

        ws.onerror = (error) => {
            console.log("WebSocket error: ", error);
        };

        return () => {
            console.log("Closing WebSocket connection");
            ws.close();
        };
    };


    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center p-6 flex-col">
            <div className="text-6xl font-bold text-white mb-20">{titleText}</div>
            <form onSubmit={handlePlay} className="bg-gray-800 shadow-lg rounded-lg p-8 w-full max-w-sm">
                <h2 className="text-white text-2xl font-bold mb-6 text-center">Join the Game</h2>
                <div className="flex flex-col mb-4">
                    <label htmlFor="username" className="mb-2 text-gray-300">
                        Username
                    </label>
                    <input
                        id="username"
                        type="text"
                        required
                        placeholder="Enter your username"
                        onChange={(e) => setUsername(e.target.value)}
                        className="p-3 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                </div>
                <button
                    type="submit"
                    disabled={isButtonDisabled}
                    className="w-full py-3 mt-4 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-white font-semibold transition duration-200"
                >
                    Play
                </button>
            </form>
        </div>
    )
}

export default Lobby;


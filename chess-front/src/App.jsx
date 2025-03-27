import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Lobby from './components/Lobby'
import Game from './components/Game'


function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Lobby />} />
                <Route path="/game/:username/:gameid" element={<Game />} />
            </Routes>
        </Router>
    );
}

export default App;

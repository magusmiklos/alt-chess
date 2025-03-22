import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Game from './components/Game'


function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Game />} />
            </Routes>
        </Router>
    );
}

export default App;

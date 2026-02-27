import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        {/* Auth routes will be added next */}
      </Routes>
    </Router>
  );
}

export default App;

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import DashboardPage from './pages/DashboardPage';

function App() {
  return (
    <Router basename={import.meta.env.BASE_URL}>
      <Toaster position="top-right" expand={true} richColors />
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        {/* Auth routes will be added next */}
      </Routes>
    </Router>
  );
}

export default App;

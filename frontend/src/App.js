import './App.css';
import AppLayout from './layout/AppLayout';
import Main from './pages/Main/Main';
import UserPrompt from './pages/UserPrompt/UserPrompt';
import RootSelection from './pages/RootSelection/RootSelection';
import { Routes, Route } from 'react-router-dom';


function App() {
  return (
    <div className='App'>
    <Routes>
      <Route path = '/' element={<AppLayout />}>
        <Route index element={<Main />} />
        <Route path='prompt' element={<UserPrompt />} />
        <Route path='root' element={<RootSelection />} />
      </Route>
    </Routes>
    </div>
  );
}

export default App;

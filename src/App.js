import './App.css';
import AppLayout from './layout/AppLayout';
import Main from './pages/Main/Main';
import UserPrompt from './pages/UserPrompt/UserPrompt';
import RootSelection from './pages/RootSelection/RootSelection';
import { Routes, Route } from 'react-router-dom';
import Graph from './pages/Graph/Graph';



function App() {
  return (
    <div className='App'>
    <Routes>
      <Route path = '/' element={<AppLayout />}>
        <Route index element={<Main />} />
        <Route path='prompt' element={<UserPrompt />} />
        <Route path='root' element={<RootSelection />} />
      </Route>
      <Route path='graph' element={<Graph />} />
    </Routes>
    </div>
  );
}

export default App;

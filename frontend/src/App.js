import './App.css';
import AppLayout from './layout/AppLayout';
import Main from './pages/Main/Main';
import UserPrompt from './pages/UserPrompt/UserPrompt';
import RootSelection from './pages/RootSelection/RootSelection';
import { Routes, Route } from 'react-router-dom';
import Graph from './pages/Graph/Graph';
import DetailPage from './pages/Details/DetailPage';
import Manager from './pages/Manage/Manager';
import UploadPage from './pages/Manage/Upload';



function App() {
  return (
    <div className='App'>
    <Routes>
    <Route path="/" element={<Main />} />
    <Route path="/" element={<AppLayout />}>
      <Route path="prompt" element={<UserPrompt />} />
      <Route path="root" element={<RootSelection />} />
    </Route>
      <Route path='graph' element={<Graph />} />
      <Route path="/detail/:id" element={<DetailPage />} />
      <Route path='/manager' element={<Manager />} />
      <Route path="/upload" element={<UploadPage />} />
    </Routes>
    </div>
  );
}

export default App;

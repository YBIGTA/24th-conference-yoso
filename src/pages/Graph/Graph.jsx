import React, {useEffect} from 'react';
import {useDispatch, useSelector} from 'react-redux';
import GraphNetwork from './GraphNetwork';
import Sidebar from './Sidebar';
import {mockdata} from '../../features/graphSlice';
import mockData from './mockData'

import './Graph.style.css';
import VerticalNavbar from '../../layout/Graphnav';


const Graph = () => {
  const dispatch = useDispatch();
  const graphData = useSelector((state) => state.graph.graphdata);
  const status = useSelector((state) => state.graph.status);

  console.log('Graph Data:', graphData);
  console.log('status', status);

  useEffect(() => {
      console.log('function')
      dispatch(mockdata(mockData));
  }, [dispatch, status]);

  if (status === 'loading' || !graphData || !graphData.nodes || !graphData.edges) {
    return <div>Loading...</div>;
  }

  return (
    <div className="graph-page">
      <VerticalNavbar />
      <div className="graph-content">
        <div className="graph-network">
          <GraphNetwork data={graphData} />
        </div>
        <Sidebar />
      </div>
    </div>
  );
};

export default Graph;

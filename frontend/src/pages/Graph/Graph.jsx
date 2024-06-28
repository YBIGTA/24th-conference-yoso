import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import GraphNetwork from './GraphNetwork_option';
import Sidebar from './Sidebar';
import './Graph.style.css';
import VerticalNavbar from '../../layout/Graphnav';

const Graph = () => {
  const dispatch = useDispatch();
  const graphData = useSelector((state) => state.graph.graphdata);
  const status = useSelector((state) => state.graph.status);
  const initialGraph = useSelector((state) => state.graph.initialgraph);

  console.log(graphData)


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




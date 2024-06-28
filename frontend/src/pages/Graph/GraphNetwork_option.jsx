import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import { useSelector, useDispatch } from 'react-redux';
import { highlightNode, fetchGraphResult, getPreviousState, resetGraphData, sortNodes } from '../../features/graphSlice.js'; 
import { fetchPaperSummary } from '../../features/detailSlice';
import { debounce } from 'lodash';
import { useNavigate } from 'react-router-dom';
import { store } from '../../app/store.js';

import { initializeGraph, initializeSimulation, applyBlur, initializeTip, setNodeInitialPosition, initializeLegend } from './Graphutils';

import Accordion from 'react-bootstrap/Accordion';
import char from '../../char2.png';
import './Graph.style.css';

const GraphNetwork = ({ data }) => {
  const svgRef = useRef();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const highlightedNode = useSelector((state) => state.graph.highlightedNode); 
  const previousGraphDataLength = useSelector((state) => state.graph.previousGraphData.length);
  const rootNodeRef = useRef(null);
  const fixedTooltip = useRef(null);
  const [animatingNode, setAnimatingNode] = useState(null);
  const simulationRef = useRef();
  const [manualCentering, setManualCentering] = useState(false);
  const [blurred, setBlurred] = useState(false);
  const prev = useSelector((state) => state.graph.previousGraphData)

  const zoomed = (event) => {
    d3.select(svgRef.current).select('g').attr('transform', event.transform);
  };

  const handleResize = debounce(() => {
    if (svgRef.current && rootNodeRef.current && !manualCentering) {
      const newWidth = svgRef.current.clientWidth;
      const newHeight = svgRef.current.clientHeight;

      rootNodeRef.current.fx = -newWidth * 0.1;
      rootNodeRef.current.fy = -newHeight * 0.1;

      const svg = d3.select(svgRef.current);
      const zoom = d3.zoom().scaleExtent([0.1, 3]).on('zoom', zoomed);
      svg.call(zoom);

      const newScale = Math.min(newWidth / 800, newHeight / 800);

      svg.transition().duration(500)
        .call(zoom.transform, d3.zoomIdentity.translate(newWidth / 2, newHeight / 2).scale(newScale));
    }
  }, 200);

  useEffect(() => {
    window.addEventListener('resize', handleResize);
    handleResize();
    return () => window.removeEventListener('resize', handleResize);
  }, [handleResize, manualCentering]);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const defs = svg.append('defs');
    const filter = defs.append('filter')
      .attr('id', 'shadow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');
    filter.append('feDropShadow')
      .attr('dx', 3)
      .attr('dy', 3)
      .attr('stdDeviation', 5)
      .attr('flood-color', 'rgba(0, 0, 0, 0.5)');

    const blurFilter = defs.append('filter')
      .attr('id', 'blur')
      .append('feGaussianBlur')
      .attr('stdDeviation', 5);

    const containerGroup = svg.append('g');

    const nodes = JSON.parse(JSON.stringify(data.nodes)).map((node) => {
      const newNode = { ...node };
      if (node.root) {
        newNode.fx = -width * 0.1;
        newNode.fy = -height * 0.1;
        rootNodeRef.current = newNode;
      } else {
        newNode.x = (Math.random() - 0.5) * width;
        newNode.y = (Math.random() - 0.5) * height;
      }
      return newNode;
    });

    const rootNode = nodes.find(node => node.root);
    if (rootNode) {
      dispatch(highlightNode(rootNode.id));
    }

    const edges = JSON.parse(JSON.stringify(data.edges)).map((edge) => ({ ...edge }));
    const maxDistance = Math.min(width, height) * 0.6;
    const minDistance = Math.min(width, height) * 0.1;

    const scoreExtent = d3.extent(nodes, (d) => d.score);
    const distanceScale = d3.scaleLinear().domain(scoreExtent).range([maxDistance, minDistance]);

    const tip = initializeTip();
    svg.call(tip);

    // Pass rootNode.id to initializeGraph
    const { link, node, radiusScale } = initializeGraph(containerGroup, nodes, edges, tip, dispatch, fixedTooltip, highlightNode, rootNode.id); 

    const ticked = () => {
      link
        .attr('x1', (d) => Math.max(-width / 2, Math.min(width / 2, d.source.x)))
        .attr('y1', (d) => Math.max(-height / 2, Math.min(height / 2, d.source.y)))
        .attr('x2', (d) => Math.max(-width / 2, Math.min(width / 2, d.target.x)))
        .attr('y2', (d) => Math.max(-height / 2, Math.min(height / 2, d.target.y)));

      node
        .attr('transform', (d) => `translate(${Math.max(-width / 2, Math.min(width / 2, d.x))},${Math.max(-height / 2, Math.min(height / 2, d.y))})`);
    };

    const simulation = initializeSimulation(nodes, edges, ticked, radiusScale, distanceScale);
    simulationRef.current = simulation;

    initializeLegend(nodes);

    const zoom = d3.zoom().scaleExtent([0.1, 3]).on('zoom', (event) => {
      d3.select(svgRef.current).select('g').attr('transform', event.transform);
    });
    svg.call(zoom);
    const newScale = Math.min(width / 800, height / 800);
    svg.transition().duration(500)
      .call(zoom.transform, d3.zoomIdentity.translate(width / 2, height / 2).scale(newScale));

    simulation.nodes(nodes);
    simulation.alpha(0.3).restart();
  
    // Back 버튼 추가
    const buttonGroup = svg.append('g')
      .attr('transform', `translate(40, 535)`)
      .style('cursor', 'pointer')
      .on('click', () => {
        console.log(previousGraphDataLength)
        console.log(prev)
        if (previousGraphDataLength <= 1) {
          dispatch(resetGraphData());
          navigate('/root', { replace: true }); 
        } else {
          dispatch(getPreviousState());
          dispatch(sortNodes('title'))
        }
      })
      
      .on('mouseover', function() {
        d3.select(this).select('rect')
          .attr('fill', '#1A67F8');
        d3.select(this).select('text')
          .attr('fill', '#FFFFFF');
      })
      .on('mouseout', function() {
        d3.select(this).select('rect')
          .attr('fill', '#FFFFFF');
        d3.select(this).select('text')
          .attr('fill', '#1A67F8');
      });

    buttonGroup.append('rect')
      .attr('width', 90)
      .attr('height', 35)
      .attr('fill', '#FFFFFF')
      .attr('stroke', '#1A67F8')
      .attr('rx', 8)
      .attr('y', 70)
      .attr('stroke-width', 1);

    buttonGroup.append('text')
      .attr('x', 43)
      .attr('y', 88)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', '#1A67F8')
      .text('< Back');

  }, [data, dispatch, navigate, previousGraphDataLength]);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const colorScale = d3.scaleLinear().domain(d3.extent(data.nodes, (d) => d.year)).range(['#B2DDFF', '#175CD3']);

    svg.selectAll('circle').attr('fill', (d) => colorScale(d.year))
      .attr('stroke', (d) => d.root ? '#194185' : d.id === highlightedNode ? '#43BA7F' : 'none')
      .attr('stroke-width', (d) => d.root ? 5 : d.id === highlightedNode ? 5 : 1.5)
      .style('filter', (d) => d.id === highlightedNode ? 'url(#shadow)' : 'none');
  }, [highlightedNode, data.nodes]);

  const handleGraphCentering = (id) => {
    const svgElement = svgRef.current;
    setManualCentering(true); 
    setBlurred(true); 
  
    if (svgElement) {
      const { width, height } = svgElement.getBoundingClientRect();
  
      const nodeSelection = d3.select(`[data-id='${id}']`).node();
      if (!nodeSelection) {
        console.error(`Node with id ${id} not found`);
        setBlurred(false);
        setManualCentering(false);
        return;
      }
  
      const transformAttr = d3.select(nodeSelection).attr('transform');
      const translateMatch = transformAttr.match(/translate\(([^,]+),([^,]+)\)/);
      if (!translateMatch) {
        console.error(`Transform attribute not found for node with id ${id}`);
        setBlurred(false);
        setManualCentering(false);
        return;
      }
  
      const x = parseFloat(translateMatch[1]);
      const y = parseFloat(translateMatch[2]);
  
      const zoom = d3.zoom().extent([[0, 0], [300, 300]]).scaleExtent([0.1, 3]).on('zoom', (event) => {
        d3.select(svgElement).select('g').attr('transform', event.transform);
      });
  
      const centerTransform = d3.zoomIdentity.translate(width / 2, height / 2).scale(1).translate(-x, -y);
  
      d3.select(svgElement).call(zoom);
      d3.select(svgElement).transition().duration(1500).call(zoom.transform, centerTransform).on('end', () => {
        setBlurred(false);
        setManualCentering(false);
      });
  
      dispatch(fetchGraphResult({ num_nodes: 10, root_id: id, mode: 'new' })).then((result) => {
        if (fetchGraphResult.fulfilled.match(result)) {
          const state = store.getState();
          const newData = state.graph.graphdata;
  
          const updatedNodes = newData.nodes.map(node => {
            if (node.id === id) {
              return { ...node, fx: x, fy: y };
            }
            return { ...node }; 
          });
  
          const updatedData = { ...newData, nodes: updatedNodes };
          navigate(`/graph`);
        } else {
          console.error(result);
        }
      }).finally(() => {
        setBlurred(false);
        setManualCentering(false);
      });
  
      applyBlur(true, highlightedNode);
      d3.select(`[data-id='${id}']`).style('filter', 'none');
    }
  };
  
  

  window.handleGraphCentering = (id) => {
    handleGraphCentering(id);
    d3.selectAll('.d3-tip').remove();
  };

  window.handleSummaryView = (id) => {
    d3.selectAll('.d3-tip').remove();
    dispatch(fetchPaperSummary(id)).then(() => {
      navigate(`/detail/${id}`);
    });
  };

  return (
    <div className="graph-network" style={{ position: 'relative' }}>
      <h3>Graph Dashboard</h3>
      <Accordion defaultActiveKey="0" className='accordion-container'>
        <Accordion.Header>
          <img src={char} width={20} />
          <span>How to Read this Graph?</span>
        </Accordion.Header>
        <Accordion.Body>
          <p>This graph was constructed by selecting journals that are most similar to your input among those in a citation relationship with the one located in the center.</p>
          <ul>
            <li>The saturation of each node indicate its <b>lateness</b></li>
            <li>The distance between the central node and each node indicates <b>Similarity to your input</b></li>
            <li>The size of each node indicates <b>the number it was cited</b></li>
          </ul>
        </Accordion.Body>
      </Accordion>
      <svg ref={svgRef} width="100%" height="100%" className='network'></svg>
      <div className="legend-container" style={{ position: 'absolute', right: '20px', bottom: '20px' }}></div>
    </div>
  );
};

export default GraphNetwork;



























































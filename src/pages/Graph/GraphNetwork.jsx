import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import { useSelector, useDispatch } from 'react-redux';
import { highlightNode } from '../../features/graphSlice';
import { debounce } from 'lodash';

import Accordion from 'react-bootstrap/Accordion';
import char from '../../char2.png'

const GraphNetwork = ({ data }) => {
  const svgRef = useRef();
  const dispatch = useDispatch();
  const highlightedNode = useSelector((state) => state.graph.highlightedNode || 'root');
  const [dimensions, setDimensions] = useState({ width: 800, height: 800 });
  const [initialNodes, setInitialNodes] = useState([]);

  const zoomed = (event) => {
    d3.select(svgRef.current).selectAll('g').attr('transform', event.transform);
  };


  useEffect(() => {
    const handleResize = debounce(() => {
      if (svgRef.current) {
        setDimensions({
          width: svgRef.current.clientWidth,
          height: svgRef.current.clientHeight,
        });

        const svg = d3.select(svgRef.current);
        const zoom = d3.zoom().scaleExtent([0.1, 3]).on('zoom', zoomed);

        svg.call(zoom);
        svg.transition().duration(500).call(zoom.scaleTo, 1);
      }
    }, 200);

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (!data || !data.nodes || !data.edges) {
      console.error('Data is not in expected format', data);
      return;
    }

    const { width, height } = dimensions;
    const innerWidth = width - 20;
    const innerHeight = height - 20;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous SVG content

    const nodes = data.nodes.map((node) => {
      const newNode = { ...node };
      if (node.id=='root'){
        newNode.x = innerWidth / 2;
        newNode.y = innerHeight / 2;
      } else {
      newNode.x = innerWidth / 2 + (Math.random() - 0.5) * innerWidth / 2;
      newNode.y = innerHeight / 2 + (Math.random() - 0.5) * innerHeight / 2;}
      return newNode;
    });

    setInitialNodes(nodes);
    dispatch(highlightNode('root'))

    //Edges
    const edges = data.edges.map((edge) => ({ ...edge }));

    const maxDistance = Math.min(innerWidth, innerHeight)*0.6;

    const scoreExtent = d3.extent(nodes, d => d.score);
    const distanceScale = d3.scaleLinear()
    .domain(scoreExtent)
    .range([50, maxDistance]);

    const linkForce = d3.forceLink(edges)
    .id((d) => d.id)
    .distance((d) => distanceScale(d.target.score)) 
    .strength(1);

    const chargeForce = d3.forceManyBody().strength(-180);

    const centerForce = d3.forceCenter(innerWidth / 2, innerHeight / 2);

    const simulation = d3.forceSimulation(nodes)
      .force('link', linkForce)
      .force('charge', chargeForce)
      .force('center', centerForce)
      .on('tick', ticked);

    const zoomHandler = d3.zoom()
      .scaleExtent([0.1, 3]) // Set zoom scale
      .on('zoom', zoomed);

    svg.call(zoomHandler);

    // Custom color scale
    const colorScale = d3.scaleLinear()
      .domain(d3.extent(nodes, d => d.year))
      .range(['#B2DDFF', '#175CD3']); 
    
    // 노드 크기 스케일
    const radiusScale = d3.scaleLinear()
    .domain(d3.extent(nodes, d => d.impact))
    .range([12, 25]); // 최소값과 최대값 반지름

    const link = svg.append('g')
      .attr('stroke', '#525151')
      .attr('stroke-opacity', 0.8)
      .selectAll('line')
      .data(edges)
      .enter()
      .append('line')
      .attr('stroke-width', 1);

    const node = svg.append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', (d) => radiusScale(d.impact)) 
      .attr('fill', (d) => (d.id === highlightedNode ? 'red' : colorScale(d.year))) 
      .attr('data-id', (d) => d.id) 
      .on('click', (event, d) => {
        dispatch(highlightNode(d.id));
      });

    node.append('title').text((d) => d.title);

    function ticked() {
        link
          .attr('x1', (d) => Math.max(20, Math.min(innerWidth - 20, d.source.x)))
          .attr('y1', (d) => Math.max(20, Math.min(innerHeight - 20, d.source.y)))
          .attr('x2', (d) => Math.max(20, Math.min(innerWidth - 20, d.target.x)))
          .attr('y2', (d) => Math.max(20, Math.min(innerHeight - 20, d.target.y)));
      
        node
          .attr('cx', (d) => Math.max(20, Math.min(innerWidth - 20, d.x)))
          .attr('cy', (d) => Math.max(20, Math.min(innerHeight - 20, d.y)));
      }

    function zoomed(event) {
      svg.selectAll('g').attr('transform', event.transform);
    }

    simulation.nodes(nodes);
    simulation.alpha(1).restart();

    // Legend
    const legendContainer = d3.select('.legend-container');
    legendContainer.selectAll('*').remove(); 

    const legendWidth = 200;
    const legendHeight = 20;

    const legendSvg = legendContainer.append('svg')
      .attr('width', legendWidth + 40)
      .attr('height', legendHeight + 60);

    const gradient = legendSvg.append('defs')
      .append('linearGradient')
      .attr('id', 'legend-gradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '0%'); 

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#B2DDFF'); 

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#175CD3'); 

    legendSvg.append('rect')
      .attr('x', 20)
      .attr('y', 20)
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#legend-gradient)');

    const legendScale = d3.scaleLinear()
      .domain(d3.extent(nodes, d => d.year))
      .range([0, legendWidth]);

    const legendAxis = d3.axisBottom(legendScale)
      .ticks(6)
      .tickFormat(d3.format("d"));

    legendSvg.append('g')
      .attr('transform', `translate(20, ${legendHeight + 20})`)
      .call(legendAxis);

  }, [data, dimensions, dispatch]);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    const colorScale = d3.scaleLinear()
      .domain(d3.extent(data.nodes, d => d.year))
      .range(['#B2DDFF', '#175CD3']); 

    svg.selectAll('circle').attr('fill', (d) => d.id === highlightedNode ? 'red' : colorScale(d.year));

    if (highlightedNode) {
      svg.select(`circle[data-id='${highlightedNode}']`).attr('fill', 'red');
    }
  }, [highlightedNode, data.nodes]);

  return (
    <div className="graph-network" style={{ position: 'relative' }}>
      <h3>Graph Dashboard</h3>
      <Accordion defaultActiveKey="0" className='accordion-container'>
        <Accordion.Header>
            <img src={char} width={20} />
            <span>How to Read this Graph?</span>
        </Accordion.Header>
        <Accordion.Body>
          <ul>
            <li>각 Node의 진하기는 <b>최신도</b>를 나타냅니다.</li>
            <li>중앙에 위치한 Root Node와 각 Node 사이의 거리는 <b>사용자 입력과의 유사도</b>를 나타냅니다.</li>
            <li>각 Node의 크기는 <b>피인용 수</b>를 나타냅니다.</li>
          </ul>
        </Accordion.Body>
      </Accordion>
      <svg ref={svgRef} width="100%" height="100%" className='network'></svg>
      <div className="legend-container" style={{ position: 'absolute', right: '20px', bottom: '20px' }}></div>
    </div>
  );
};

export default GraphNetwork;




















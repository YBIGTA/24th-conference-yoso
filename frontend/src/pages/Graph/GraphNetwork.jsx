import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import d3Tip from 'd3-tip';
import { useSelector, useDispatch } from 'react-redux';
import { highlightNode, fetchGraphResult } from '../../features/graphSlice.js';
import { debounce } from 'lodash';
import { store } from '../../app/store.js';
import Accordion from 'react-bootstrap/Accordion';
import char from '../../char2.png';

const GraphNetwork = ({ data, setLoading, loading }) => {
  const svgRef = useRef();
  const dispatch = useDispatch();
  const highlightedNode = useSelector((state) => state.graph.highlightedNode);
  const rootNodeRef = useRef(null);
  const fixedTooltip = useRef(null);
  const simulationRef = useRef();

  const zoomed = (event) => {
    d3.select(svgRef.current).select('g').attr('transform', event.transform);
  };

  const handleResize = debounce(() => {
    if (svgRef.current && rootNodeRef.current) {
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
  }, [handleResize]);

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

    const containerGroup = svg.append('g');

    const nodes = data.nodes.map((node) => {
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

    const edges = data.edges.map((edge) => ({ ...edge }));
    const maxDistance = Math.min(width, height) * 0.6;
    const minDistance = Math.min(width, height) * 0.1;

    const scoreExtent = d3.extent(nodes, (d) => d.score);
    const distanceScale = d3.scaleLinear().domain(scoreExtent).range([maxDistance, minDistance]);

    const tip = d3Tip()
      .attr('class', 'd3-tip')
      .offset([10, 0])
      .html((event, d) => {
        return `
          <div style="color: white; padding: 10px; border-radius: 3px; background-color: #1e3a8a; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);">
            <div>Select Action</div>
            <button onclick="window.handleGraphCentering('${d.id}')">이 노드를 Root 노드로 변경</button>
            <button onclick="window.handleSummaryView('${d.id}')">이 논문의 요약 정보 확인하기</button>
          </div>
        `;
      });
    svg.call(tip);

    const { link, node, radiusScale } = initializeGraph(containerGroup, nodes, edges, tip);

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

    const zoom = d3.zoom().scaleExtent([0.1, 3]).on('zoom', zoomed);
    svg.call(zoom);
    const newScale = Math.min(width / 800, height / 800);
    svg.transition().duration(500)
      .call(zoom.transform, d3.zoomIdentity.translate(width / 2, height / 2).scale(newScale));

    simulation.nodes(nodes);
    simulation.alpha(0.3).restart();

  }, [data, dispatch]);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const colorScale = d3.scaleLinear().domain(d3.extent(data.nodes, (d) => d.year)).range(['#B2DDFF', '#175CD3']);

    svg.selectAll('circle').attr('fill', (d) => colorScale(d.year))
      .attr('stroke', (d) => d.root ? '#194185' : d.id === highlightedNode ? '#43BA7F' : 'none')
      .attr('stroke-width', (d) => d.root ? 5 : d.id === highlightedNode ? 5 : 1.5)
      .style('filter', (d) => d.id === highlightedNode ? 'url(#shadow)' : 'none');
  }, [highlightedNode, data.nodes]);

  const initializeGraph = (containerGroup, nodes, edges, tip) => {
    const colorScale = d3.scaleLinear()
      .domain(d3.extent(nodes, (d) => d.year))
      .range(['#B2DDFF', '#175CD3']);

    const radiusScale = d3.scaleLinear()
      .domain(d3.extent(nodes, (d) => d.citations))
      .range([30, 60]);

    const link = containerGroup.append('g')
      .attr('stroke', '#525151')
      .attr('stroke-opacity', 0.8)
      .selectAll('line')
      .data(edges)
      .enter()
      .append('line')
      .attr('stroke-width', 1)
      .attr('class', 'link');

    const node = containerGroup.append('g')
      .selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .attr('transform', (d) => `translate(${d.x},${d.y})`)
      .attr('data-id', (d) => d.id)
      .attr('class', 'node')
      .on('mouseover', function(event, d) {
        if (!fixedTooltip.current || fixedTooltip.current.id !== d.id) {
          tip.show(event, d, this);
        }
        d3.select(this).select('circle').attr('r', (d) => radiusScale(d.citations) * 1.2);
      })
      .on('mouseout', function(event, d) {
        if (!fixedTooltip.current || fixedTooltip.current.id !== d.id) {
          tip.hide(event, d, this);
          d3.select(this).select('circle').attr('r', (d) => radiusScale(d.citations));
        }
      })
      .on('click', function(event, d) {
        if (fixedTooltip.current && fixedTooltip.current.id === d.id) {
          tip.hide(event, d, this);
          fixedTooltip.current = null;
        } else {
          tip.show(event, d, this);
          fixedTooltip.current = d;
        }

        dispatch(highlightNode(d.id));
      });

    node.append('circle')
      .attr('r', (d) => radiusScale(d.citations))
      .attr('fill', (d) => colorScale(d.year))
      .attr('stroke', (d) => d.root ? '#194185' : d.id === highlightedNode ? '#2BB0B8' : 'none')
      .attr('stroke-width', (d) => d.root ? 3 : 1.5)
      .attr('data-id', (d) => d.id)
      .style('filter', (d) => d.id === highlightedNode ? 'url(#shadow)' : 'none');

    node.append('text')
      .attr('dx', 0)
      .attr('dy', (d) => -radiusScale(d.citations) - 10)
      .attr('text-anchor', 'middle')
      .text((d) => `${d.author && d.author[0] ? d.author[0].split(' ')[0] : ''}, ${d.year}`);

    return { link, node, radiusScale };
  };

  const initializeSimulation = (nodes, edges, ticked, radiusScale, distanceScale) => {
    const linkForce = d3.forceLink(edges)
      .id((d) => d.id)
      .distance((d) => {
        const targetNode = nodes.find(node => node.id === d.target.id);
        const baseDistance = distanceScale(targetNode.score);
        return baseDistance;
      })
      .strength(1);

    const chargeForce = d3.forceManyBody().strength(-400);
    const centerForce = d3.forceCenter(0, 0);
    const collisionForce = d3.forceCollide().radius(d => radiusScale(d.citations) + 20);

    return d3.forceSimulation(nodes)
      .force('link', linkForce)
      .force('charge', chargeForce)
      .force('center', centerForce)
      .force('collision', collisionForce)
      .on('tick', ticked);
  };

  const initializeLegend = (nodes) => {
    const legendContainer = d3.select('.legend-container');
    legendContainer.selectAll('*').remove();

    const legendWidth = 180;
    const legendHeight = 20;

    const legendSvg = legendContainer.append('svg')
      .attr('width', legendWidth + 60)
      .attr('height', legendHeight + 60);

    const gradient = legendSvg.append('defs')
      .append('linearGradient')
      .attr('id', 'legend-gradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '0%');

    gradient.append('stop').attr('offset', '0%').attr('stop-color', '#B2DDFF');
    gradient.append('stop').attr('offset', '100%').attr('stop-color', '#175CD3');

    legendSvg.append('rect')
      .attr('x', 48)
      .attr('y', 20)
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#legend-gradient)');

    const yearExtent = d3.extent(nodes, (d) => d.year);
    const legendScale = d3.scaleLinear().domain(yearExtent).range([0, legendWidth]);

    const legendAxis = d3.axisBottom(legendScale)
      .tickValues([yearExtent[0], yearExtent[1]])
      .tickFormat(d3.format('d'));

    legendSvg.append('g')
      .attr('transform', `translate(48, ${legendHeight + 20})`)
      .call(legendAxis);

    legendSvg.append('text')
      .attr('x', 0)
      .attr('y', 20)
      .attr('dy', '1.2em')
      .attr('text-anchor', 'start')
      .style('font-size', '11px')
      .text('Recency');
  };

  const handleGraphCentering = (id) => {
    const svgElement = svgRef.current;
    setLoading(true); // 로딩 상태 활성화
  
    dispatch(fetchGraphResult({ num_nodes: 10, root_id: id, mode: 'new' })).then((result) => {
      if (fetchGraphResult.fulfilled.match(result)) {
        const state = store.getState();
        const newData = state.graph.graphdata;
  
        const newNode = newData.nodes.find(node => node.id === id);
        if (newNode) {
          rootNodeRef.current = { ...newNode };
          dispatch(highlightNode(id));
        }
  
        updateGraph(newData);
      } else {
        console.error(result);
      }
    }).finally(() => {
      setLoading(false); // 로딩 상태 비활성화
    });
  };

  window.handleGraphCentering = (id) => {
    handleGraphCentering(id);
    d3.selectAll('.d3-tip').remove();
  };

  const updateGraph = (newData) => {
    const svg = d3.select(svgRef.current);

    svg.selectAll('.node').remove();
    svg.selectAll('.link').remove();

    const nodes = newData.nodes.map((node) => ({ ...node }));
    const edges = newData.edges.map((edge) => ({ ...edge }));

    const tip = d3Tip()
      .attr('class', 'd3-tip')
      .offset([10, 0])
      .html((event, d) => {
        return `
          <div style="color: white; padding: 10px; border-radius: 3px; background-color: #1e3a8a; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);">
            <div>Select Action</div>
            <button onclick="window.handleGraphCentering('${d.id}')">이 노드를 Root 노드로 변경</button>
            <button onclick="window.handleSummaryView('${d.id}')">이 논문의 요약 정보 확인하기</button>
          </div>
        `;
      });

    svg.call(tip);

    const { link, node, radiusScale } = initializeGraph(svg.select('g'), nodes, edges, tip);

    const ticked = () => {
      link
        .attr('x1', (d) => d.source.x)
        .attr('y1', (d) => d.source.y)
        .attr('x2', (d) => d.target.x)
        .attr('y2', (d) => d.target.y);

      node
        .attr('transform', (d) => `translate(${d.x},${d.y})`);
    };

    const simulation = initializeSimulation(nodes, edges, ticked, radiusScale, d3.scaleLinear());
    simulationRef.current = simulation;

    simulation.nodes(nodes);
    simulation.alpha(0.3).restart();
  };

  window.handleSummaryView = (id) => {
    // Add your logic to handle summary view here
  };

  return (
    <div className="graph-network" style={{ position: 'relative' }}>
      <Accordion defaultActiveKey="0" className={`accordion-container ${loading ? 'loading' : ''}`}>
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
      {!loading && <svg ref={svgRef} width="100%" height="100%" className='network'></svg>}
      <div className="legend-container" style={{ position: 'absolute', right: '20px', bottom: '20px' }}></div>
    </div>
  );
};

export default GraphNetwork;


















































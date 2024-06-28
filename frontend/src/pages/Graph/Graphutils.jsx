import * as d3 from 'd3';
import d3Tip from 'd3-tip';

export const initializeGraph = (containerGroup, nodes, edges, tip, dispatch, fixedTooltip, highlightNode) => {
  const colorScale = d3.scaleLinear()
    .domain(d3.extent(nodes, (d) => d.year))
    .range(['#B2DDFF', '#175CD3']);

  const radiusScale = d3.scaleLinear()
    .domain(d3.extent(nodes, (d) => d.citations))
    .range([37, 65]);

  // edges 배열을 순회하면서 각 node의 isCentralNode 속성을 설정합니다.
  nodes.forEach(node => {
    node.isCentralNode = edges.some(edge => edge.source === node.id);
  });

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
      // edges 배열을 순회하여 중심 노드를 확인합니다.
      const isCentralNode = edges.some(edge => edge.source === d.id);

      if (!fixedTooltip.current || fixedTooltip.current.id !== d.id) {
        if (isCentralNode) {
          tip.html((event, d) => `
            <div style="color: white; border-radius: 3px; background-color: #1e3a8a; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);">
              <button class="tooltip-button" onclick="window.handleSummaryView('${d.id}')">Summary of the Journal</button>
            </div>
          `);
        } else {
          tip.html((event, d) => `
            <div style="color: white; border-radius: 3px; background-color: #1e3a8a; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);">
              <button class="tooltip-button" onclick="window.handleGraphCentering('${d.id}')">Change it as Center</button>
              <button class="tooltip-button" onclick="window.handleSummaryView('${d.id}')">Summary of this Paper</button>
            </div>
          `);
        }
        tip.show(event, d, this);

      } else if (fixedTooltip.current && fixedTooltip.current.id === d.id) {
        // 고정된 툴팁이 있는 경우 다시 보여줌
        tip.show(event, d, this);
      }
      d3.select(this).select('circle').attr('r', (d) => radiusScale(d.citations) * 1.2);
    })
    .on('mouseout', function(event, d) {
      if (!fixedTooltip.current || fixedTooltip.current.id !== d.id) {
        tip.hide(event, d, this);
        console.log(d.citations);
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
    .attr('stroke', (d) => d.root ? '#194185' : 'none')
    .attr('stroke-width', (d) => d.root ? 3 : 1.5)
    .attr('data-id', (d) => d.id)
    .style('filter', 'none');

  node.append('text')
    .attr('dx', 0)
    .attr('dy', (d) => -radiusScale(d.citations) - 15)
    .attr('text-anchor', 'middle')
    .style('font-size', '14px')
    .text((d) => `${d.author && d.author[0] ? d.author[0].split(' ')[0] : ''}, ${d.year}`);

  return { link, node, radiusScale };
};



export const initializeSimulation = (nodes, edges, ticked, radiusScale, distanceScale) => {
  const linkForce = d3.forceLink(edges)
    .id((d) => d.id)
    .distance((d) => {
      const targetNode = nodes.find(node => node.id === d.target.id);
      const baseDistance = distanceScale(targetNode.score);
      return baseDistance;
    })
    .strength(1);

  const chargeForce = d3.forceManyBody().strength(-4000);
  const centerForce = d3.forceCenter(0, 0);
  const collisionForce = d3.forceCollide().radius(d => radiusScale(d.impact) + 20);

  return d3.forceSimulation(nodes)
    .force('link', linkForce)
    .force('charge', chargeForce)
    .force('center', centerForce)
    .force('collision', collisionForce)
    .on('tick', ticked);
};

export const applyBlur = (isBlurred, highlightedNode) => {
  d3.selectAll('.node').style('filter', isBlurred ? 'url(#blur)' : 'none');
  d3.selectAll('.link').style('filter', isBlurred ? 'url(#blur)' : 'none');
  if (highlightedNode) {
    d3.select(`[data-id='${highlightedNode}']`).style('filter', 'none');
  }
};

export const initializeTip = () => d3Tip()
  .attr('class', 'd3-tip')
  .offset([10, 0]);

export const setNodeInitialPosition = (nodes, width, height) => {
  nodes.forEach(node => {
    if (!node.root) {
      node.x = (Math.random() - 0.5) * width;
      node.y = (Math.random - 0.5) * height;
    } else {
      node.fx = -width * 0.1;
      node.fy = -height * 0.1;
    }
  });
};

export const initializeLegend = (nodes) => {
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


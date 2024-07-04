import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Layout, List, Dropdown, Button, Menu } from 'antd';
import { highlightNode, sortNodes } from '../../features/graphSlice';
import { PlusCircleOutlined, MinusCircleOutlined, CaretDownOutlined } from '@ant-design/icons';
import { fetchPaperSummary } from '../../features/detailSlice';
import './Graph.style.css'; 

const { Sider } = Layout;

const Sidebar = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState([]); // 확장된 노드들을 저장합니다
  const dispatch = useDispatch();
  const highlightedNode = useSelector((state) => state.graph.highlightedNode);
  const state = useSelector((state) => state.graph.graphdata);
  const navigate = useNavigate();
  const sortKey = useSelector((state)=> state.graph.sortKey);

  const sortedNodes = [...state.nodes].sort((a, b) => {
    if (sortKey === 'title') {
      if (a.root) return -1; 
      if (b.root) return 1;
      return a.title.localeCompare(b.title); // 제목의 알파벳 순으로 정렬
    }
    return b[sortKey] - a[sortKey]; // 선택된 정렬 키에 따라 정렬
  });

  const toggleSidebarHandler = () => {
    setIsExpanded(!isExpanded);
  };

  const handleNodeClick = (nodeId) => {
    dispatch(highlightNode(nodeId));
  };

  const handleSortChange = ({ key }) => {
    dispatch(sortNodes(key));
  };

  const toggleNodeExpansion = (nodeId) => {
    setExpandedNodes(prevState => 
      prevState.includes(nodeId) 
        ? prevState.filter(id => id !== nodeId) 
        : [...prevState, nodeId]
    );
  };

  const sortMenu = (
    <Menu onClick={handleSortChange}>
      <Menu.Item key="score">
        Similarity
      </Menu.Item>
      <Menu.Item key="year">
        Recency
      </Menu.Item>
      <Menu.Item key="citations">
        Citation
      </Menu.Item>
    </Menu>
  );

  return (
    <Sider
      collapsible
      collapsed={!isExpanded}
      onCollapse={toggleSidebarHandler}
      trigger={null}
      width={550}
      collapsedWidth={330}
      className="sidebar"
    >
      <div className='list-title'>
        <h4>Node List</h4>
        <button
          type="primary"
          onClick={toggleSidebarHandler}
          className='expand-button'
        >
          {isExpanded ? <MinusCircleOutlined /> : <PlusCircleOutlined />}
        </button>
      </div>
      {isExpanded && (
        <div className="sort-buttons">
          <span>Descending Sort By:</span>
          <Dropdown overlay={sortMenu} trigger={['click']}>
            <Button>
              {sortKey === 'score' ? 'Similarity' : sortKey === 'year' ? 'Recency' : sortKey.charAt(0).toUpperCase() + sortKey.slice(1)} <CaretDownOutlined />
            </Button>
          </Dropdown>
        </div>
      )}
      <div className="node-detail-list">
        {sortedNodes.length > 0 ? (
          <List
            dataSource={sortedNodes}
            renderItem={node => (
              <>
                <List.Item
                  key={node.id}
                  className={`node-detail ${highlightedNode === node.id ? 'highlighted' : ''}`}
                  onClick={() => handleNodeClick(node.id)}
                >
                  <List.Item.Meta
                    title={
                      <div className="node-title">
                        {node.root && <div className="root-node">ROOT NODE</div>}
                        {node.title}
                      </div>
                    }
                    className='detail-content'
                    description={
                      isExpanded ? (
                        <div className="expanded-details">
                          <div>
                            <span>{node.author?.length > 1 ? `${node.author[0]} et al` : node.author ? node.author[0] : 'Yiheng Xu et al.'} ({node.year})</span>
                            {expandedNodes.includes(node.id) ? (
                              <MinusCircleOutlined onClick={() => toggleNodeExpansion(node.id)} style={{ marginLeft: 6, marginTop: 10 }} />
                            ) : (
                              <PlusCircleOutlined onClick={() => toggleNodeExpansion(node.id)} style={{ marginLeft: 6, marginTop: 10 }} />
                            )}
                          </div>
                          <button className="view-summary-button" onClick={() => dispatch(fetchPaperSummary(node.id)).then(() => { navigate(`/detail/${node.id}`); })}>View Summary</button>
                        </div>
                      ) : (
                        <div className="collapsed-details">
                          <span>{node.author ? (node.author.length > 1 ? `${node.author[0]} et al` : node.author[0]) : 'Yiheng Xu et al.'}</span>
                          <span>{node.year}</span>
                        </div>
                      )
                    }
                  />
                </List.Item>
                {expandedNodes.includes(node.id) && (
                  <div className="node-extra-details">
                    <span className='extratitle'>{node.title}</span>
                    <span className='authors'>
                      Written by 
                      <span>  {node.author ? node.author.join(', ') : 'Yiheng Xu et al.'}</span>
                      </span>
                    <span className='citation'>
                      | Citation 
                      <span>  {node.citations},  </span> 
                      Similarity 
                      <span>  {node.score}</span>
                      </span>
                    <span className='keywords'>|Keywords| <span>{node.keywords ? node.keywords.join(', ') : 'None'}</span></span>
                  </div>
                )}
              </>
            )}
          />
        ) : (
          <div className="no-data">
            <p>No nodes available</p>
          </div>
        )}
      </div>
    </Sider>
  );
};

export default Sidebar;





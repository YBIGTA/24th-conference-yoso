import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Layout,  List } from 'antd';
import { highlightNode } from '../../features/graphSlice';
import mockData from './mockData';
import { PlusCircleOutlined, MinusCircleOutlined } from '@ant-design/icons';

const { Sider } = Layout;

const Sidebar = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const dispatch = useDispatch();
  const highlightedNode = useSelector((state) => state.graph.highlightedNode);

  const toggleSidebarHandler = () => {
    setIsExpanded(!isExpanded);
  };

  const handleNodeClick = (nodeId) => {
    dispatch(highlightNode(nodeId));
  };

  const sortedNodes = [...mockData.nodes].sort((a, b) => b.score - a.score);

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
      <div className="node-detail-list">
        <List
          dataSource={sortedNodes}
          renderItem={node => (
            <List.Item
              key={node.id}
              className={`node-detail ${highlightedNode === node.id ? 'highlighted' : ''}`}
              onClick={() => handleNodeClick(node.id)}
            >
              <List.Item.Meta
                title={node.title}
                className='detail-content'
                description={
                  isExpanded ? (
                    <>
                      <p>Impact: {node.impact}</p>
                      <p>Score: {node.score}</p>
                      <p> Year : {node.year}</p>
                      <a href="#">View Article</a>
                    </>
                  ) : (
                    <span>{node.title}</span>
                  )
                }
              />
            </List.Item>
          )}
        />
      </div>
    </Sider>
  );
};

export default Sidebar;




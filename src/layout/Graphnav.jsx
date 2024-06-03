import React from 'react';
import { Menu } from 'antd';
import { BranchesOutlined, HomeOutlined, BookOutlined, BulbOutlined } from '@ant-design/icons';
import logo from '../logo.png';

const VerticalNavbar = () => {
  return (
    <div className="vertical-navbar">
      <div className="logo">
        <img src={logo} width={150} />
      </div>
      <Menu
        mode="vertical"
        defaultSelectedKeys={['graph']}
        style={{ height: '100%', borderRight: 0 }}
      >
        <Menu.Item key="graph" icon={<BranchesOutlined />}>
          Graph
        </Menu.Item>
        <Menu.Item key="home" icon={<HomeOutlined />}>
          Home
        </Menu.Item>
        <Menu.Item key="guide" icon={<BookOutlined />}>
          Guide
        </Menu.Item>
        <Menu.Item key="features" icon={<BulbOutlined />}>
          Features
        </Menu.Item>
      </Menu>
      <div className="button-container">
        <button className="custom-button">사용자 입력 확인</button>
        <button className="custom-button">Original Graph</button>
      </div>
    </div>
  );
};

export default VerticalNavbar;

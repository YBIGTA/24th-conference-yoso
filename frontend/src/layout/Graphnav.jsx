import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Menu, Tooltip, Button } from 'antd';
import { getFirstState } from '../features/graphSlice';
import { 
  BranchesOutlined, 
  HomeOutlined, 
  UserOutlined,
  SyncOutlined,
  MenuFoldOutlined, 
  MenuUnfoldOutlined,
  CloseOutlined
} from '@ant-design/icons';
import logo from '../logo.png';
import './Layout.style.css';

const { SubMenu } = Menu;

const VerticalNavbar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKeys, setSelectedKeys] = useState(['graph']); // Default selected key
  const [userPanelVisible, setUserPanelVisible] = useState(false);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const userData = useSelector(state => state.root.query); // Rootslice의 state에서 데이터 가져오기

  const toggleCollapsed = () => {
    setCollapsed(!collapsed);
  };

  const toggleUserPanel = () => {
    setUserPanelVisible(!userPanelVisible);
  };

  const handleMenuClick = (key) => {
    setSelectedKeys([key]); // Set selected key
    if (key === 'user') {
      toggleUserPanel();
    }
  };

  const menuItems = [
    { key: 'graph', icon: <BranchesOutlined />, label: 'Graph' },
    { key: 'original', icon: <SyncOutlined />, label: 'Original Graph' },
    { key: 'user', icon: <UserOutlined />, label: 'My Query' },
    { key: 'home', icon: <HomeOutlined />, label: 'Home' }
  ];

  // 메뉴가 접힌 상태일 때만 'open' 아이템 추가
  if (collapsed) {
    menuItems.unshift({ key: 'open', icon: <MenuUnfoldOutlined />, label: 'Unfold Menu' });
  }

  return (
    <div className="vertical-navbar-container">
      <div className={`vertical-navbar ${collapsed ? 'collapsed' : ''}`}>
        {!collapsed && (
          <div className="logo-container">
            <div className="logo">
              <img src={logo} width={170} />
            </div>
            <Button 
              type="primary" 
              onClick={toggleCollapsed} 
              className="collapse-button"
            >
              <MenuFoldOutlined />
            </Button>
          </div>
        )}
        <Menu
          mode="inline"
          selectedKeys={selectedKeys} // 항상 selectedKeys를 사용하여 강조
          style={{ height: '100%', borderRight: 0 }}
          inlineCollapsed={collapsed}
        >
          {menuItems.map(item => (
            <Menu.Item 
              key={item.key} 
              icon={item.icon} 
              onClick={() => {
                if (item.key === 'open') {
                  toggleCollapsed();
                } else if (item.key=== 'original'){
                  dispatch(getFirstState())
                } else if (item.key ==='home'){
                  navigate('/')
                } else {
                  handleMenuClick(item.key);
                }
              }}
            >
              {collapsed ? (
                <Tooltip placement="right" title={item.label}>
                  <span>{item.label}</span>
                </Tooltip>
              ) : (
                <span>{item.label}</span>
              )}
            </Menu.Item>
          ))}
        </Menu>
      </div>
      {userPanelVisible && (
        <div className="user-panel">
          <Button 
            onClick={toggleUserPanel} 
            type="text" 
            icon={<CloseOutlined />} 
            style={{ position: 'absolute', right: 16, top: 28 }} 
          />
          <h2>My Query</h2>
          <hr className="custom-hr"></hr>
          <div className="user-input-section">
            <div className="user-input-item">
              <label>Domain</label>
              <span>{userData.domain}</span>
            </div>
            <div className="user-input-item">
              <label>Research Problem</label>
              <span>{userData.problem}</span>
            </div>
            <div className="user-input-item">
              <label>Solution</label>
              <span>{userData.solution}</span>
            </div>
          </div>
          <div className="user-input-buttons">
            <Button className="custom-button" type="primary" onClick={() => navigate('/prompt')}>Enter Again</Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VerticalNavbar;
















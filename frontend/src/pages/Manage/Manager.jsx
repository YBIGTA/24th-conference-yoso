import React, { useState, useEffect, useCallback} from 'react';
import {useNavigate} from 'react-router-dom';
import { Table, Tag, Button, Input, Layout, Menu, Pagination } from 'antd';
import { request } from '../../app/axiosInstance.js';
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  SlidersOutlined,
  UploadOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import './Manager.style.css';
import logo from '../../logo.png';

const { Sider, Content } = Layout;
const { Search } = Input;

const Manager = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('1');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);
  const navigate = useNavigate();

  const toggle = () => {
    setCollapsed(!collapsed);
  };

  const handleMenuClick = (e) => {
    setSelectedKey(e.key);
    if (e.key === '2') {
      navigate('/upload');
    }
  };

  const fetchRequests = useCallback(async () => {
    setLoading(true);
    try {
      const response = await request.get('/api/v1/paper/status/all');
      const formattedData = response.data.map((item, index) => ({
        key: index,
        ...item,
      }));
      const uniqueData = removeDuplicateFilenames(formattedData);
      console.log(uniqueData);
      setData(uniqueData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const removeDuplicateFilenames = (data) => {
    const filenameMap = new Map();
    data.forEach(item => {
      filenameMap.set(item.filename, item);
    });
    return Array.from(filenameMap.values());
  };

  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  const handleSearch = (value) => {
    setSearchText(value);
  };

  const filteredData = data.filter(item =>
    item.filename.toLowerCase().includes(searchText.toLowerCase())
  );

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const columns = [
    { title: '#', dataIndex: 'request_id', key: 'request_id' },
    { title: 'Filename', dataIndex: 'filename', key: 'filename' },
    {
      title: 'Requested Date',
      dataIndex: 'requested_date',
      key: 'requested_date',
      render: (requested_date) => new Date(requested_date).toLocaleString(),
      sorter: (a, b) => new Date(a.requested_date) - new Date(b.requested_date),
    },
    {
      title: 'PDF Uploaded',
      dataIndex: 'pdf_uploaded',
      key: 'pdf_uploaded',
      render: (pdf_uploaded) =>
        pdf_uploaded ? <Tag color="green">Done</Tag> : <Tag color="red">False</Tag>,
    },
    {
      title: 'DLA Complete',
      dataIndex: 'bbox_detected',
      key: 'bbox_detected',
      render: (bbox_detected) =>
        bbox_detected ? <Tag color="green">Done</Tag> : <Tag color="red">False</Tag>,
    },
    {
      title: 'Metadata Postprocessed',
      dataIndex: 'metadata_parsed',
      key: 'metadata_parsed',
      render: (metadata_parsed) =>
        metadata_parsed ? <Tag color="green">Done</Tag> : <Tag color="red">False</Tag>,
    },
    {
      title: 'Images Uploaded',
      dataIndex: 'images_uploaded',
      key: 'images_uploaded',
      render: (images_uploaded) =>
        images_uploaded ? <Tag color="green">Done</Tag> : <Tag color="red">False</Tag>,
    },
    {
      title: 'Metadata Stored',
      dataIndex: 'metadata_stored',
      key: 'metadata_stored',
      render: (metadata_stored) =>
        metadata_stored ? <Tag color="green">Done</Tag> : <Tag color="red">False</Tag>,
    },
  ];

  // 현재 페이지에 맞는 데이터 슬라이싱
  const currentData = filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <Layout className="manager-layout">
      <Sider trigger={null} collapsible collapsed={collapsed} className="manager-sider">
        <div className="manager-logo">
          {collapsed ? (
            <MenuUnfoldOutlined className="trigger" onClick={toggle} />
          ) : (
            <div className="logo-header">
              <img src={logo} alt="Brand Logo" className="brand-logo" />
              <MenuFoldOutlined className="trigger" onClick={toggle} />
            </div>
          )}
        </div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[selectedKey]}
          onClick={handleMenuClick}
          className="manager-menu"
        >
          <Menu.Item key="1" icon={<SlidersOutlined />}><span className={collapsed ? 'collapsed-item' : ''}>Dashboard</span></Menu.Item>
          <Menu.Item key="2" icon={<UploadOutlined />}><span className={collapsed ? 'collapsed-item' : ''}>Upload</span></Menu.Item>
          <Menu.Item key="3" icon={<LogoutOutlined />}><span className={collapsed ? 'collapsed-item' : ''}>Logout</span></Menu.Item>
        </Menu>
      </Sider>
      <Layout className="manager-content-layout">
        <Content className="manager-content">
          <div className="manager-header">
            <h1 className="manager-title">Dashboard</h1>
          </div>
          <div className="search-refresh-container">
            <Search
              placeholder="Search Filename"
              onSearch={handleSearch}
              onChange={(e) => handleSearch(e.target.value)}
              className="manager-search"
            />
            <Button type="primary" onClick={fetchRequests} className="manager-refresh">
              Refresh
            </Button>
          </div>
          <div className="table-container">
            <Table
              columns={columns}
              dataSource={currentData}
              loading={loading}
              pagination={false} // 페이지네이션을 false로 설정
              className="manager-table"
            />
            <Pagination
              current={currentPage}
              pageSize={pageSize}
              total={filteredData.length}
              onChange={handlePageChange}
              className="manager-pagination"
            />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default Manager;










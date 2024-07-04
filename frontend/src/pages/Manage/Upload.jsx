import React, { useState } from 'react';
import { Upload, Input, Layout, Menu, message } from 'antd';
import { InboxOutlined, MenuUnfoldOutlined, MenuFoldOutlined, SlidersOutlined, UploadOutlined, LogoutOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './UploadPage.style.css';
import logo from '../../logo.png';

const { Dragger } = Upload;
const { Sider, Content } = Layout;

const UploadPage = () => {
  const [doi, setDoi] = useState('');
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('2');
  const navigate = useNavigate();

  const toggle = () => {
    setCollapsed(!collapsed);
  };

  const handleMenuClick = (e) => {
    setSelectedKey(e.key);
    if (e.key === '1') {
      navigate('/manager');
    }
  };

  const handleDoiChange = (e) => {
    setDoi(e.target.value);
  };

  const uploadProps = {
    name: 'file',
    multiple: false,
    // action: '/api/v1/paper/upload', 
    action: `${process.env.INFERENCE_SERVER_API_URL}/predict?semantic_id=${doi}`,
    onChange(info) {
      const { status } = info.file;
      if (status === 'done') {
        message.success(`${info.file.name} file uploaded successfully.`);
        handleFileUpload(info.file.originFileObj);
      } else if (status === 'error') {
        message.error(`${info.file.name} file upload failed.`);
      }
    },
  };

  const handleFileUpload = async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      // formData.append('doi', doi);
      const uri = `${process.env.INFERENCE_SERVER_API_URL}/predict/${doi}`
      const encoded = encodeURI(uri);
      const response = await axios.post(encoded, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 200) {
        message.success('File and DOI submitted successfully.');
      } else {
        message.error('Failed to submit file and DOI.');
      }
    } catch (error) {
      console.error('Error uploading file and DOI:', error);
      message.error('Error uploading file and DOI.');
    }
  };

  return (
    <Layout className="upload-layout">
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
      <Layout className="upload-content-layout">
        <Content className="upload-content">
          <h1 class="upload-title">Upload Paper</h1>
          <div>
            <span class='desc'>1. Enter DOI of the Paper</span>
          </div>
          <Input
            placeholder="Enter Paper DOI"
            value={doi}
            onChange={handleDoiChange}
            className="upload-input"
          />
          <div>
            <span class='desc2'>2. Upload pdf file</span>
          </div>
          <Dragger {...uploadProps} className="upload-dragger">
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag file to this area to upload</p>
          </Dragger>
        </Content>
      </Layout>
    </Layout>
  );
};

export default UploadPage;


import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Table, Tag, Tooltip } from 'antd';
import { MinusOutlined, PlusOutlined, RadarChartOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import char from '../../char2.png';
import './RootSelection.style.css';

const RootSelection = () => {
  const location = useLocation();
  const initialData = location.state?.data || [];
  const [data, setData] = useState(initialData);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [expandedKeys, setExpandedKeys] = useState([]);

  //response 처리//
  useEffect(() => {
    if (initialData.length >0) {
      const formattedData = initialData.map((item) => ({
        key: item.id,
        title: item.title,
        authors: item.authors,
        keywords: item.keywords,
        citation: 100,
        year: item.year,
    }));

    setData(formattedData);
  }
}, [initialData]);

  const onSelectChange = (selectedKey) => {
    setSelectedRowKeys([selectedKey]);
  };

  const handleExpand = (expanded, record) => {
    setExpandedKeys(expanded ? [record.key] : []);
  };

  const columns = [
    {
      title: 'Select',
      dataIndex: 'select',
      key: 'select',
      width: '5%',
      render: (_, record) => (
        <input
          type="radio"
          name="select"
          checked={selectedRowKeys.includes(record.key)}
          onChange={() => onSelectChange(record.key)}
        />
      )
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      width: '40%'
    },
    {
      title: 'Authors',
      dataIndex: 'authors',
      key: 'authors',
      width: '20%',
      render: (authors) => {
        const displayedAuthors = authors.length > 2
          ? `${authors[0]}, ${authors[1]} et al.`
          : authors.join(', ');
        return authors.length > 2 ? (
          <Tooltip title={authors.join(', ')} placement="bottom" color="#102A56">
            <span className="author">{displayedAuthors}</span>
          </Tooltip>
        ) : (
          <span className="author">{displayedAuthors}</span>
        );
      },
    },
    {
      title: 'Citation',
      dataIndex: 'citation',
      key: 'citation',
      width: '10%', 
      sorter: {
        compare: (a, b) => a.citation - b.citation,
      },
    },
    {
      title: 'Keywords',
      dataIndex: 'keywords',
      key: 'keywords',
      width: '20%', 
      render: (keywords, record) => {
        const isExpanded = expandedKeys.includes(record.key);
        return (
          <div className="keyword-container">
            <Tag className="keyword">{keywords[0]}</Tag>
            {keywords.length > 1 && (
              <button
                className="circle-button"
                onClick={() => handleExpand(!isExpanded, record)}
              >
                {isExpanded ? <MinusOutlined /> : <PlusOutlined />}
              </button>
            )}
          </div>
        );
      },
    },
    {
      title: 'Year',
      dataIndex: 'year',
      key: 'year',
      width: '15%',
      sorter: {
        compare: (a, b) => a.year - b.year,
      },
    },
  ];

  const expandedRowRender = (record) => (
    <div className="expanded-keywords">
      <span>|Keywords| </span>
      {record.keywords.slice(1).join(', ')}
    </div>
  );

  return (
    <div className="root-selection">
      <div className="head">
        <img src={char} className="character" />
        <h2>Select Root : Top 5 Similar Research</h2>
        <Tooltip 
          title={
            <div className="tooltip-content">
              <p>Root 후보는 어떻게 선정되었나요?</p>
              <ul>
                <li>입력하신 연구 분야, 문제, 해결 방안과 선행 연구 Abstract 사이의 유사도를 기반으로 top5를 선정했습니다.</li>
              </ul>
            </div>
          }
          placement="bottomLeft"
          color="#102A56"
        >
          <span><QuestionCircleOutlined className="question" /></span>
        </Tooltip>
      </div>
      <p>
        입력하신 내용과 가장 유사한 선행 연구 목록입니다. <br />
        선택 연구 그래프 생성을 위해 Root Node가 될 핵심 연구를 선택해주세요!
      </p>

      <div className="default-sort">
        <span style={{ fontStyle: 'italic' }}>
          * Default sort <Tag color="blue">Descending</Tag> <Tag color="blue">Similarity</Tag>
        </span>
      </div>

      <div className="table">
        <Table
          columns={columns}
          dataSource={data}
          pagination={false}
          rowClassName={(record) => (selectedRowKeys.includes(record.key) ? 'selected-row' : '')}
          expandable={{
            expandedRowRender,
            onExpand: handleExpand,
            expandedRowKeys: expandedKeys,
            expandIcon: ({ expanded, onExpand, record }) => (
              <span />
            ),
            expandIconColumnIndex: -1, /* 확장 아이콘 열을 제거 */
          }}
          onRow={(record) => ({
            onClick: () => onSelectChange(record.key),
          })}
        />
      </div>
      <div className="generate-button-container">
        <button
          className="generate-button"
          disabled={selectedRowKeys.length === 0}
          onClick={() => console.log('Selected:', selectedRowKeys)}
        >
          <RadarChartOutlined /> Generate
        </button>
      </div>
    </div>
  );
};

export default RootSelection;










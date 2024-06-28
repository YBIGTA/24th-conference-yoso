import React, { useState, useEffect, useMemo } from 'react';
import {useNavigate} from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { fetchGraphResult } from '../../features/graphSlice';
import Loader from '../../layout/Loader';
import { Table, Tag, Tooltip } from 'antd';
import { MinusOutlined, PlusOutlined, RadarChartOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import char from '../../char2.png';
import './RootSelection.style.css';

const RootSelection = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const initialData = useSelector((state) => state.root.data);
  const graphStatus = useSelector((state) => state.root.status);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [expandedKeys, setExpandedKeys] = useState([]);

  const handleGraph = () => {
    const num_nodes = 10;
    const root_id = selectedRowKeys[0];
    dispatch(fetchGraphResult({ num_nodes, root_id, mode: 'root' })).then((result) => {
      if (fetchGraphResult.fulfilled.match(result)) {
        navigate('/graph');
      } else {
        console.error(result);
      }
    });
  };

  const formattedData = useMemo(() => {
    return initialData.map((item) => ({
      key: item.id,
      title: item.title,
      authors: item.authors || ['Yiheng Xu', 'James', 'Sophie', 'John', 'Doe', 'Jane'],
      keywords: item.summary.keywords,
      citations: item.impact,
      year: item.published_year,
    }));
  }, [initialData]);


  const [data, setData] = useState(formattedData);

  useEffect(() => {
    setData(formattedData);
  }, [formattedData]);

  const onSelectChange = (selectedKey) => {
    setSelectedRowKeys([selectedKey]);
  };

  const handleExpand = (expanded, record) => {
    setExpandedKeys(expanded ? [record.key] : []);
  };

  const columns = [
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
      dataIndex: 'citations',
      key: 'citations',
      width: '10%', 
      sorter: {
        compare: (a, b) => a.citations - b.citations,
      },
    },
    {
      title: 'Keywords',
      dataIndex: 'keywords',
      key: 'keywords',
      width: '20%', 
      render: (keywords, record) => {
        if (!keywords || keywords.length === 0) {
          return null; // 키워드가 존재하지 않으면 렌더링하지 않음
        }
    
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
        compare: (a, b) => a.year - b.year
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
      {graphStatus === 'loading' ? (
        <Loader message='We are searching for similar prior papers for you !' />
      ) : (
      <>
      <div className="head">
        <img src={char} className="character" />
        <h2>Top 5 Similar Research</h2>
        <Tooltip 
          title={
            <div className="tooltip-content">
              <p>How were the researches selected?</p>
              <ul>
                <li>Researches were selected based on your inpur and prior study's domain, problem, solution.</li>
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
        Please select a paper that will be the center of prior study investigation.
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
            expandIconColumnIndex: -1, 
          }}
          onRow={(record) => ({
            onClick: () => onSelectChange(record.key),
            className: selectedRowKeys.includes(record.key) ? 'selected-row' : '',
          })}
        />
      </div>
      <div className="generate-button-container">
        <button
          className="generate-button"
          disabled={selectedRowKeys.length === 0}
          onClick={handleGraph}
        >
          <RadarChartOutlined /> Generate
        </button>
      </div>
      </>
      )}
    </div>
  );
};

export default RootSelection;












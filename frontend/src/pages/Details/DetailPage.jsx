import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import { fetchPaperSummary } from '../../features/detailSlice';
import { Card, Tag, Button, Collapse, Tabs, message } from 'antd';
import { BranchesOutlined, CloseOutlined, TeamOutlined, CalendarOutlined, ExportOutlined, IssuesCloseOutlined } from '@ant-design/icons';
import VerticalNavbar from '../../layout/Graphnav';
import './DetailPage.style.css';

const { Panel } = Collapse;

const DetailPage = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const detail = useSelector((state) => state.detail.data);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    dispatch(fetchPaperSummary(id));
  }, [dispatch, id]);

  const capitalizeFirstLetter = (string) => {
    if (!string) return ''; // string이 null이거나 undefined일 때 빈 문자열 반환
    return string.charAt(0).toUpperCase() + string.slice(1);
  };

  const renderPanelContent = (content) => {
    if (Array.isArray(content)) {
      return content.map((item, index) => (
        <div key={index}>
          {typeof item === 'string' ? <p>{item}</p> : (
            <>
              <h3>{item.name}</h3>
              <p>{item.caption}</p>
              <p>{item.summary}</p>
            </>
          )}
        </div>
      ));
    }
    return <p>{content}</p>;
  };

  const renderInnerTabs = (items, type) => (
    <Tabs tabPosition="left" style={{ maxHeight: '600px', overflowY: 'hidden' }}>
      <Tabs.TabPane tab="All" key="all">
        <div style={{ maxHeight: '600px', overflowY: 'scroll' }}>
          {items.map((item, index) => (
            <div key={index}>
              <h3>{capitalizeFirstLetter(item.name)}</h3>
              <p>{item.summary}</p>
              <br />
            </div>
          ))}
        </div>
      </Tabs.TabPane>
      {items.map((item, index) => (
        <Tabs.TabPane tab={capitalizeFirstLetter(item.name)} key={index}>
          <div style={{ maxHeight: '600px', overflowY: 'scroll' }}>
            <h3>{capitalizeFirstLetter(item.name)}</h3>
            <p>{item.summary}</p>
          </div>
        </Tabs.TabPane>
      ))}
    </Tabs>
  );

  if (!detail) {
    return <div>Loading...</div>;
  }

  return (
    <div className="detail-page">
      <VerticalNavbar className="vertical-navbar" />
      <div className="content">
        <Card
          title={
            <div className="card-title">
              <h2>{detail.responses.title}</h2>
              <div className="detail-meta">
                <span>
                  <TeamOutlined className="icon" />
                  {detail.responses.authors && detail.responses.authors.length > 3
                    ? `${detail.responses.authors.slice(0, 3).join(', ')}, et al`
                    : detail.responses.authors ? detail.responses.authors.join(', ') : 'Unknown Authors'}
                </span>
                <span><CalendarOutlined className="icon" />{detail.responses.published_year}</span>
                <span><IssuesCloseOutlined className="icon" /> {detail.responses.impact} Citations</span>
              </div>
  
              <button className="close-button" type="button" onClick={() => window.history.back()}>
                ✕
              </button>
              {/*<button className="open-graph" type="button" onClick={() => window.history.back()}>
                <BranchesOutlined className='icons'></BranchesOutlined>Open in Graph
              </button>*/}
            </div>
          }
          className="custom-card"
        >
          <div>
            <h4>Abstract</h4>
            <p>{detail.responses.abstract ? detail.responses.abstract : 'None'}</p>
            <h4>Keywords</h4>
            <div className="keywords">
              {detail.keywords?.map((keyword, index) => (
                <span className="keyword-tag" key={index}>{keyword}</span>
              ))}
            </div>
          </div>
        </Card>
        <Collapse>
          {detail.responses.figures && (
            <Panel header="Figures" key="figures">
              {renderInnerTabs(detail.responses.figures, 'figures')}
            </Panel>
          )}
          {detail.responses.tables && (
            <Panel header="Tables" key="tables">
              {renderInnerTabs(detail.responses.tables, 'tables')}
            </Panel>
          )}
          {detail.responses.reference && (
            <Panel header="References" key="references">
              {renderPanelContent(detail.responses.reference)}
            </Panel>
          )}
        </Collapse>
      </div>
    </div>
  );
};

export default DetailPage;











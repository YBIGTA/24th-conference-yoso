// src/components/Loader.jsx
import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { Progress } from 'antd';
import './Layout.style.css';
import char from '../char2.png';

const Loader = ({ message }) => {
  const status = useSelector((state) => state.root.status);
  const [percent, setPercent] = useState(0);

  useEffect(() => {
    let timer;
    if (status === 'loading') {
      setPercent(0);
      timer = setInterval(() => {
        setPercent((prev) => {
          if (prev >= 99) {
            clearInterval(timer);
            return prev;
          }
          return prev + 1;
        });
      }, 120); // 50ms에서 100ms로 조정하여 속도를 일치시킵니다.
    } else if (status === 'succeeded' || status === 'failed') {
      clearInterval(timer);
      setPercent(100);
    }
    return () => clearInterval(timer);
  }, [status]);

  return (
    <div className="progress-container">
      <div className="custom-progress-wrapper">
        <Progress
          percent={percent}
          showInfo={false}
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
          trailColor="#d9d9d9"
        />
        <div
          className="custom-progress-circle"
          style={{
            left: `${percent}%`,
            backgroundImage: `url(${char})`
          }}
        />
        <div className="tooltip" style={{ left: `${percent}%` }}>
          {percent}%
        </div>
      </div>
      <div className="loading-message">
        {status === 'loading' ? message : "Load complete!"}
      </div>
    </div>
  );
};

export default Loader;




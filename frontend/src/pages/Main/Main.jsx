import React from 'react';
import './Main.style.css';
import char from '../../char3.png';
import logo from '../../logo.png';
import { useNavigate } from 'react-router-dom';
import { SearchOutlined } from '@ant-design/icons';

const Main = () => {
  const navigate = useNavigate();

  const handleStartButtonClick = () => {
    navigate('/prompt');
  };
  return (
    <div>
    <div className='imgsec'>
        <img src={logo} alt="Logo" className="logo" />
      </div>
    <div className="homepage">
      <section className="main-section">
        <div className='semi-round'></div>
        <div className="content">
          <h1 className="main-title">You Only Search Once !</h1>
          <p className="main-subtitle">Organize prior research similar to mine in a single search</p>
          <button className="start-button" onClick={handleStartButtonClick}>Start for Free</button>
          <div className='char-body'>
            <img src={char} alt="Character" className="char-image"/>
          </div>
          <div className="tagged">
            <div className="tagg tag1"># Computer Vision</div>
            <div className="tagg tag2"># NLP</div>
            <div className="tagg tag3"># Psychology</div>
            <div className="tagg tag4"># Education</div>
            <div className="tagg tag5"># Business</div>
            <div className="tagg tag6"># Economics</div>
          </div>
          <div className='legs'>
            <div className='leg-right'></div>
            <div className='leg-left'></div>
          </div>
        </div>
      </section>
      <section className="why-choose-us">
        <div className="search-box">
          <span>Start your academic career with <span className="highlight">YOSO</span> now !</span>
          <SearchOutlined className="search-icon" />
        </div>
      </section>
    </div>
    </div>
  );
};

export default Main;




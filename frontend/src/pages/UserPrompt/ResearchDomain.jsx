import React, { useState, useEffect } from 'react';
import { DownOutlined, UpOutlined } from '@ant-design/icons';
import './UserPrompt.style.css';
import char from '../../char2.png';

const Domain = ({ title, subtitle, Input, setInput, examples, hasError }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleInputChange = (event) => {
    setInput(event.target.value);
  };

  const toggleAccordion = () => {
    setIsOpen(!isOpen);
  };

  useEffect(() => {
    setIsOpen(false);
  }, [title]);

  useEffect(() => {
    const stepsAction = document.querySelector('.steps-action');
    if (stepsAction) {
      if (isOpen) {
        stepsAction.classList.add('accordion-open');
      } else {
        stepsAction.classList.remove('accordion-open');
      }
    }
  }, [isOpen]);

  const renderInput = () => {
    const hasInput = Input.trim() !== '';
    const inputClass = `domain-input ${hasInput ? 'focused' : ''} ${hasError ? 'error' : ''}`;

    if (title === 'Research Problem' || title === 'Solution') {
      return (
        <textarea
          className={`${inputClass} textarea-input`}
          placeholder={`Input your ${title} in English`}
          value={Input}
          onChange={handleInputChange}
        />
      );
    }

    return (
      <input
        className={inputClass}
        type='text'
        placeholder={`Input your ${title} in English`}
        value={Input}
        onChange={handleInputChange}
      />
    );
  };

  const renderExample = () => {
    if (title === 'Research Domain') {
      return (
        <div className='example'>
          <span>Example |</span>
          {examples.map((example, index) => (
            <div key={index} className='tag'>{example}</div>
          ))}
        </div>
      );
    }

    return (
      <div className='accordion'>
        <div className='accordion-title' onClick={toggleAccordion}>
          Example {isOpen ? <UpOutlined className='toggle' /> : <DownOutlined className='toggle' />}
        </div>
        {isOpen && (
          <div className='accordion-item'>
            <ul>
              {examples.map((example, index) => (
                <li key={index}>{example}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="research-domain-container">
      <div className='head'>
        <img src={char} className='characters'/>
        <h1 className="title">{title}</h1>
      </div>
      <h2 className="subtitle">{subtitle}</h2>
      {renderInput()}
      {hasError && <div className='error-message'>This field is required.</div>}
      {renderExample()}
    </div>
  );
};

export default Domain;

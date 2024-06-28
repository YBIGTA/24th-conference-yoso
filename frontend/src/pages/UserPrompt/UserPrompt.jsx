// src/components/UserPrompt.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchRootResult } from '../../features/rootSlice';
import { Steps, Button } from 'antd';
import { ArrowLeftOutlined, ArrowRightOutlined, RadarChartOutlined } from '@ant-design/icons';
import Loader from '../../layout/Loader';
import './UserPrompt.style.css';
import Domain from './ResearchDomain';

const UserPrompt = () => {
  const [Input, setInput] = useState({
    domain: '',
    problem: '',
    solution: '',
  });

  const [error, setError] = useState({
    domain: false,
    problem: false,
    solution: false,
  });

  const handleInputChange = (field, newValue) => {
    setInput({
      ...Input,
      [field]: newValue,
    });
    setError((prevError) => ({
      ...prevError,
      [field]: false,
    }));
  };

  const handleInputError = (currentStep) => {
    const stepKey = steps[currentStep].key;
    const newError = {
      ...error,
      [stepKey]: !Input[stepKey].trim(),
    };
    setError(newError);
    return !Input[stepKey].trim();
  };

  // 버튼 설정 및 네비게이션
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const status = useSelector((state) => state.root.status);
  const [current, setCurrent] = useState(0);

  const next = async () => {
    if (!handleInputError(current)) {
      if (current === steps.length - 1) {
        const response = await dispatch(fetchRootResult(Input));
        if (fetchRootResult.fulfilled.match(response)) {
          navigate('/root');
        }
      } else {
        setCurrent(current + 1);
      }
    }
  };

  const prev = () => {
    setCurrent(current - 1);
  };

  const onChange = (nextStep) => {
    if (current === 0 && nextStep !== 1) return;
    if (nextStep < current || !handleInputError(current)) {
      setCurrent(nextStep);
    }
  };

  const steps = [
    {
      status: current > 0 ? 'finish' : 'process',
      title: 'Domain',
      key: 'domain',
      content: (
        <Domain
          title="Research Domain"
          desc="Please fill out the research domain you are interested in."
          Input={Input.domain}
          setInput={(value) => handleInputChange('domain', value)}
          examples={['Computer Vision', 'NLP', 'Financial Engineering']}
          hasError={error.domain}
        />
      ),
    },
    {
      status: current > 1 ? 'finish' : current === 1 ? 'process' : 'wait',
      key: 'problem',
      title: 'Problem',
      content: (
        <Domain
          title="Research Problem"
          desc="Please write the research problem you want to solve."
          Input={Input.problem}
          setInput={(value) => handleInputChange('problem', value)}
          examples={[
            'Lack of foundation model for image segmentation',
            'Computational overhead of transformer architecture leads processing high resolution visual data difficult',
          ]}
          hasError={error.problem}
        />
      ),
    },
    {
      status: current === 2 ? 'process' : 'wait',
      key: 'solution',
      title: 'Solution',
      content: (
        <Domain
          title="Solution"
          desc="Please write down a solution to the problem you have in mind."
          Input={Input.solution}
          setInput={(value) => handleInputChange('solution', value)}
          examples={[
            'Build largest dataset for image segmentation and design new model that trained to be promptable.',
            'Use specialized tokens as messengers for flexible exchange of visual information across regions and reduce computational complexity',
          ]}
          hasError={error.solution}
        />
      ),
    },
  ];

  return (
    <div className={`user-prompt-container ${current === 0 ? 'is-first-step' : ''}`}>
      <Steps
        size="large"
        current={current}
        onChange={onChange}
        className="site-navigation-steps"
        items={steps.map((step) => ({ status: step.status, title: step.title }))}
      />
      <div className="steps-content">{steps[current].content}</div>
      <div className="steps-action">
        {current > 0 && (
          <Button className="button-prev" style={{ margin: '0.8px' }} onClick={prev}>
            <ArrowLeftOutlined /> Previous
          </Button>
        )}
        {current < steps.length - 1 && (
          <Button
            className="button-next"
            style={{
              margin: '0.8px',
              backgroundColor: Input[steps[current].key] ? '#1A67F8' : '#E0F2FE',
              color: Input[steps[current].key] ? 'white' : '#006BBB',
              opacity: Input[steps[current].key] ? 1 : 0.6,
            }}
            onClick={next}
          >
            Next <ArrowRightOutlined />
          </Button>
        )}
        {current === steps.length - 1 && (
          <Button
            className="button-next"
            style={{
              margin: '0.8px',
              backgroundColor: Input[steps[current].key] ? '#1A67F8' : '#E0F2FE',
              color: Input[steps[current].key] ? 'white' : '#006BBB',
              opacity: Input[steps[current].key] ? 1 : 0.6,
            }}
            onClick={next}
          >
            Generate <RadarChartOutlined />
          </Button>
        )}
      </div>
    </div>
  );
};

export default UserPrompt;


const rawData = [
  { id: '1', title: 'Node 1', impact: 80, score: 90, year:2023 },
  { id: '2', title: 'Node 2', impact: 70, score: 85, year: 2018 },
  { id: '3', title: 'Node 3', impact: 60, score: 75, year: 2020 },
  { id: '4', title: 'Node 4', impact: 60, score: 65, year: 2021 },
  { id: '5', title: 'Node 5', impact: 50, score: 55, year: 2022 },
  { id: '6', title: 'Node 6', impact: 40, score: 72, year: 2020 },
  { id: '7', title: 'Node 7', impact: 60, score: 40, year:2018 },
  { id: '8', title: 'Node 8', impact: 86, score: 42, year: 2019 },
  { id: '9', title: 'Node 9', impact: 10, score: 31, year:2017 },
  { id: '10', title: 'Node 10', impact: 62, score: 70, year:2020 },
  { id: 'root', title: 'Root Node', impact: 90, score: 100, year:2018 },
];

const rootId = 'root';

// 데이터 가공 함수
const processData = (data, rootId) => {
  const nodes = data.map(item => ({
    id: item.id,
    title: item.title,
    impact: item.impact,
    score: item.score,
    year: item.year,
  }));

  const edges = data
    .filter(item => item.id !== rootId)
    .map(item => ({
      source: rootId,
      target: item.id,
    }));


  return { nodes, edges };
};

const mockData = processData(rawData, rootId);

export default mockData;


  
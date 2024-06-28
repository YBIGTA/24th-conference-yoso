import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { request } from '../app/axiosInstance.js';

export const fetchGraphResult = createAsyncThunk(
    'fetchGraphResult',
    async ({ num_nodes, root_id, mode }, { getState, rejectWithValue }) => {
        const state = getState();
        const query = state.root.query;
        let referenceData;

        if (mode === 'root') {
            referenceData = state.root.data;
        } else if (mode === 'new') {
            referenceData = state.graph.graphdata;
        } else {
            return rejectWithValue('Invalid mode');
        }
        
        const payload = {
            num_nodes,
            root_id,
            query,
            referenceData
        };

        try {
            const response = await request.post('api/v1/search/graph', payload);
            console.log(response.data);
            return { data: response.data, root_id, mode, referenceData }; 
        } catch (error) {
            return rejectWithValue(error.response ? error.response.data : error.message);
        }
    }
);

const processData = (data, rootId, rootItem, mode) => {
    const nodes = data.map(item => ({
        id: item.id,
        title: item.title,
        citations: item.impact,
        score: item.score,
        year: item.published_year,
        keywords: item.summary.keywords,
        author: item.authors || ['Yiheng Xu', 'James', 'Sophie', 'John', 'Doe', 'Jane']
    }));

    if (rootItem) {
        if (mode === 'new') {
            rootItem = { ...rootItem, published_year: rootItem.year};
            delete rootItem.year;
          }
        if (mode==='root') {
            rootItem = {...rootItem, citations: rootItem.impact, author: rootItem.authors};
            delete rootItem.impact;
            delete rootItem.authors;
        }
        nodes.push({
            ...rootItem,
            root: true,
            year: rootItem.published_year,
            score: rootItem.score,
            author: rootItem.authors
        });
    }

    const edges = data
        .filter(item => item.id !== rootId)
        .map(item => ({
            source: rootId,
            target: item.id,
        }));

    return { nodes, edges };
}

const graphSlice = createSlice({
    name: 'graph',
    initialState: {
        graphdata: { nodes: [], edges: [] },
        previousGraphData: [],
        status: 'idle',
        highlightedNode: null,
        error: null,
        mode: null,
        sortKey: 'title'
    },
    reducers: {
        highlightNode: (state, action) => {
            state.highlightedNode = action.payload;
        },
        getPreviousState: (state) => {
            if (state.previousGraphData.length > 1) {
                state.previousGraphData.pop();
                state.graphdata = state.previousGraphData[state.previousGraphData.length - 1];
            }
        },
        getFirstState: (state) => {
            if (state.previousGraphData.length > 0) {
                state.graphdata = state.previousGraphData[0];
            }
        },
        resetGraphData: (state) => {
            state.graphdata = { nodes: [], edges: [] };
            state.previousGraphData = [];
            state.highlightedNode = null;
            state.status = 'idle';
            state.mode = null;
            state.sortKey = 'title';
        },
        setRootNode: (state, action) => {
            const rootId = action.payload;
            state.graphdata.nodes.forEach(node => {
                node.root = node.id === rootId;
            });
        },
        sortNodes: (state, action) => {
            const sortKey = action.payload;
            state.graphdata.nodes = [...state.graphdata.nodes].sort((a,b)=> {
                if (sortKey === 'title') {
                    if (a.root) return -1;
                    if (b.root) return 1;
                    return a.title.localeCompare(b.title);
                }
                return b[sortKey] - a[sortKey];
            
            });
            state.sortKey = sortKey;
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchGraphResult.pending, (state, action) => {
                state.status = 'loading';
            })
            .addCase(fetchGraphResult.fulfilled, (state, action) => {
                const { data, root_id, mode, referenceData } = action.payload;
                let rootItem;
                
                if (mode === 'root') {
                    rootItem = referenceData.find(item => item.id === root_id);
                    state.mode = 'root';
                } else if (mode === 'new') {
                    rootItem = referenceData.nodes.find(item => item.id === root_id);
                    state.mode = 'new';
                }

                const processedData = processData(data, root_id, rootItem, state.mode);

                state.status = 'succeeded';
                state.graphdata = {
                    nodes: processedData.nodes,
                    edges: processedData.edges
                };

                if (!state.previousGraphData){
                    state.previousGraphData = [];
                }
                state.previousGraphData.push(JSON.parse(JSON.stringify(state.graphdata)));
                if (state.previousGraphData.length > 10) {
                    state.previousGraphData.splice(1, 1);
                }
            })
            .addCase(fetchGraphResult.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            });
    }
});

export const { highlightNode, getPreviousState, getFirstState, resetGraphData, setRootNode, sortNodes } = graphSlice.actions;

export default graphSlice.reducer;









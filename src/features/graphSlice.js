import {createSlice, createAsyncThunk} from '@reduxjs/toolkit';
import axios from 'axios';

export const fetchGraphResult = createAsyncThunk(
    'fetchGraphResult',
    async ({numNodes, rootId}, {getState, rejectWithValue }) => {
        const state = getState();
        const query = state.root.query;
        const payload={
            num_nodes: numNodes,
            root_id: rootId,
            query: query,
        };

        console.log(payload);
        
        try {
            const response = await axios.post('api/v1/search/graph', payload);
            console.log(response);
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response ? error.response.data : error.message);
        }
    });

//Define Slice
const graphSlice = createSlice({
    name: 'graph',
    initialState: {
        graphdata: { nodes: [], edges: [] },
        status: 'idle',
        highlightedNode: null,
        error: null
    },
    reducers: {
        mockdata: (state, action) => {
            state.graphdata =  action.payload;
            state.status = 'succeeded';
        },
        highlightNode: (state, action) => {
            state.highlightedNode = action.payload;
        }
    },
    extraReducers: (builder) => {
        builder
        .addCase(fetchGraphResult.pending, (state, action) => {
            state.status = 'loading';
        })
        .addCase(fetchGraphResult.fulfilled, (state, action) => {
            state.status = 'succeeded';
            state.data = action.payload;
        })
        .addCase(fetchGraphResult.rejected, (state, action) => {
            state.status = 'failed';
            state.error = action.error.message
            console.log(action.error.message);
        })
    }
});

export const {mockdata, highlightNode} = graphSlice.actions;

export default graphSlice.reducer;
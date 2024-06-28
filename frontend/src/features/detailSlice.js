import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { request } from '../app/axiosInstance.js';

export const fetchPaperSummary = createAsyncThunk(
  'detail/fetchPaperSummary',
  async (paperId, { getState, rejectWithValue }) => {
    const state = getState();
    const nodeData = state.graph.graphdata.nodes.find(node => node.id === paperId);
    console.log('node',nodeData)

    try {
      const response = await request.get(`api/v1/paper/item/${paperId}`);
      const responses = response.data;
      return { responses, keywords: nodeData.keywords  }; // 노드 데이터와 API 응답 데이터 통합
    } catch (error) {
      return rejectWithValue(error.response ? error.response.data : error.message);
    }
  }
);

const detailSlice = createSlice({
  name: 'detail',
  initialState: {
    data: null,
    status: 'idle',
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchPaperSummary.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchPaperSummary.fulfilled, (state, action) => {
        state.status = 'succeeded';
        console.log('here',action.payload);
        state.data = action.payload;
      })
      .addCase(fetchPaperSummary.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  },
});

export default detailSlice.reducer;


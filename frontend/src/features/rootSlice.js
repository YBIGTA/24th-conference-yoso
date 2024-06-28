import {createSlice, createAsyncThunk} from '@reduxjs/toolkit';
import {request} from '../app/axiosInstance.js';

export const fetchRootResult = createAsyncThunk(
    'fetchRootResult',
    async (data, {rejectWithValue}) => {
        try {
            const response = await request.post('/api/v1/search/query', 
                {domain : data.domain,
                problem : data.problem,
                solution : data.solution
                }
            );

            return { 
                query: {
                    domain: data.domain, 
                    problem: data.problem, 
                    solution: data.solution},
                data: response.data
            };
    } catch (error) {
        return rejectWithValue(error.response.data);
    }
    });

//Define Slice
const rootSlice = createSlice({
    name: 'root',
    initialState: {
        data: [],
        query: {
            domain: '',
            problem: '',
            solution: ''
        },
        status: 'idle',
        error: null
    },
    reducers: {},
    extraReducers: (builder) => {
        builder
        .addCase(fetchRootResult.pending, (state) => {
            state.status = 'loading';
        })
        .addCase(fetchRootResult.fulfilled, (state, action) => {
            state.status = 'succeeded';
            state.query = action.payload.query;
            state.data = action.payload.data;
        })
        .addCase(fetchRootResult.rejected, (state, action) => {
            state.status = 'failed';
            state.error = action.error.message;
        })
    }
});

export default rootSlice.reducer;
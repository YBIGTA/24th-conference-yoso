import { combineReducers } from '@reduxjs/toolkit';
import rootReducer from '../features/rootSlice';
import graphReducer from '../features/graphSlice';

const mainReducer = combineReducers({
  root: rootReducer,
  graph: graphReducer,
});

export default mainReducer;

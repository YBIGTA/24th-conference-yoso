import { combineReducers } from '@reduxjs/toolkit';
import rootReducer from '../features/rootSlice';
import graphReducer from '../features/graphSlice';
import detailReducer from '../features/detailSlice';

const mainReducer = combineReducers({
  detail: detailReducer,
  root: rootReducer,
  graph: graphReducer,
});

export default mainReducer;

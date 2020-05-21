import {
  SAVE_DATA_BEGIN,
  SAVE_DATA_SUCCESS,
  SAVE_DATA_FAILED,
  SAVE_VIEW_CONFIGS_BEGIN,
  SAVE_VIEW_CONFIGS_SUCCESS,
  SAVE_VIEW_CONFIGS_FAILURE,
} from '../actions/ActionConstants';

const initialSaveReducerState = {
  data: null,
  isFetching: false,
  error: false,
  message: '',
};

export const SaveDataReducer = (state = initialSaveReducerState, action) => {
  switch (action.type) {
    case SAVE_DATA_BEGIN:
      return Object.assign({}, state, {
        isFetching: action.isFetching,
        error: action.error,
      });
    case SAVE_DATA_SUCCESS:
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });
    case SAVE_DATA_FAILED:
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });
    default:
      return state;
  }
};

const initialSaveViewConfigReducerState = {
  data: null,
  isFetching: false,
  error: false,
  message: '',
};

export const SaveViewConfigReducer = (
  state = initialSaveViewConfigReducerState,
  action
) => {
  switch (action.type) {
    case SAVE_VIEW_CONFIGS_BEGIN:
      return Object.assign({}, state, {
        isFetching: action.isFetching,
        error: action.error,
      });
    case SAVE_VIEW_CONFIGS_SUCCESS:
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });
    case SAVE_VIEW_CONFIGS_FAILURE:
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });
    default:
      return state;
  }
};

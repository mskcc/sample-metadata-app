import * as constants from "../actions/ActionConstants";

const initialState = {
  data: null,
  isFetching: false,
  error: false,
  message: "",
};

const SearchReducer = (state = initialState, action) => {
  switch (action.type) {
    case constants.SEARCH_BEGIN:
      return Object.assign({}, state, {
        isFetching: action.isFetching,
        error: action.error,
      });
    case constants.SEARCH_SUCCESS:
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });
    case constants.SEARCH_FAILED:
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });
    case constants.SEARCH_INVALID:
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

export default SearchReducer;

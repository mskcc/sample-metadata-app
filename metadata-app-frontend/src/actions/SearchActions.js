import axios from "axios";
import { BASE_URL} from "../configs/react.configs";
import * as constants from './ActionConstants';

const searchdata_begin = () => {
    return {
      type: constants.SEARCH_BEGIN,
      isFetching: true,
      error:false
    };
  };
  
  const searchdata_success = data => {
    return {
      type: constants.SEARCH_SUCCESS,
      isFetching: false,
      error: false,
      data: data,
      message:data.message
    };
  };

  const searchdata_invalid = data => {
    return {
      type: constants.SEARCH_INVALID,
      isFetching:false,
      error:true,
      data: data,
      message:data.message,
  };
  }

  const searchdata_failed = err => {
    return {
      type: constants.SEARCH_FAILED,
      isFetching:false,
      error:true,
      data: null,
      message:err,
  };
  }
  
  
  export const searchdata = (params, headers) => {
    return dispatch => {
      dispatch(searchdata_begin());
      axios
        .post(BASE_URL + "search", params, headers)
        .then(res => {
          if (res.data.valid) {
            dispatch(searchdata_success(res.data));
          }
          if (!res.data.valid) {
            dispatch(searchdata_invalid(res.data));
          }
        })
        .catch(err => {
          dispatch(searchdata_failed(err));
        });
    };
  };
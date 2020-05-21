import axios from 'axios';
import { BASE_URL } from '../configs/react.configs';
import {
  SEARCH_BEGIN,
  SEARCH_SUCCESS,
  SEARCH_FAILED,
  SEARCH_INVALID,
} from './ActionConstants';
import { toast } from 'react-toastify';

//Redux actions for searching data.
const searchdata_begin = () => {
  return {
    type: SEARCH_BEGIN,
    isFetching: true,
    error: false,
  };
};

const searchdata_success = (data) => {
  return {
    type: SEARCH_SUCCESS,
    isFetching: false,
    error: false,
    data: data,
    message: data.message,
  };
};

const searchdata_invalid = (data) => {
  return {
    type: SEARCH_INVALID,
    isFetching: false,
    error: true,
    data: data,
    message: data.message,
  };
};

const searchdata_failed = (err) => {
  return {
    type: SEARCH_FAILED,
    isFetching: false,
    error: true,
    data: null,
    message: err,
  };
};

export const searchdata = (params, headers) => {
  return (dispatch) => {
    dispatch(searchdata_begin());
    axios
      .post(BASE_URL + 'search', params, headers)
      .then((res) => {
        if (res.data.success) {
          dispatch(searchdata_success(res.data));
        }
        if (!res.data.success) {
          dispatch(searchdata_invalid(res.data));
        }
      })
      .catch((err) => {
        dispatch(searchdata_failed(err));
        toast.error(err.message, { position: toast.POSITION.TOP_CENTER });
      });
  };
};

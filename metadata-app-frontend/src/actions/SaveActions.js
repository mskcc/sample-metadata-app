import axios from 'axios';
import { BASE_URL } from '../configs/react.configs';
import { toast } from 'react-toastify';

import {
  SAVE_DATA_BEGIN,
  SAVE_DATA_SUCCESS,
  SAVE_DATA_FAILED,
  SAVE_VIEW_CONFIGS_BEGIN,
  SAVE_VIEW_CONFIGS_SUCCESS,
  SAVE_VIEW_CONFIGS_FAILURE,
} from '../actions/ActionConstants';

//HAS TWO TYPE OF ACTIONS IN THIS FILE. ACTIONS TO SAVE DATA and ACTIONS TO SAVE 
//USER VIEW CONFIGURATIONS.
//Redux actions for saving data when users make data changes in data grid.
//Only edited rows are sent to backend for data saving and only editable
//column values from each row are updated in the database.
const saveDataBegin = () => {
  return {
    type: SAVE_DATA_BEGIN,
    isFetching: true,
    data: null,
    error: false,
    mesage: '',
  };
};

const saveDataSuccess = (data) => {
  return {
    type: SAVE_DATA_SUCCESS,
    isFetching: false,
    error: false,
    data: data,
    message: data.message,
  };
};

const saveDataFailed = (err) => {
  return {
    type: SAVE_DATA_FAILED,
    isFetching: false,
    error: true,
    data: null,
    message: err,
  };
};

export const saveChanges = (params, headers) => {
  return (dispatch) => {
    dispatch(saveDataBegin());
    axios
      .post(BASE_URL + 'save_data', params, headers)
      .then((res) => {
        if (res.data.success) {
          dispatch(saveDataSuccess(res.data));
          toast.success(res.data.message, {
            position: toast.POSITION.TOP_CENTER,
          });
        }
      })
      .catch((err) => {
        dispatch(saveDataFailed(err));
        toast.error(err.message, { position: toast.POSITION.TOP_CENTER });
      });
  };
};


//Redux actions for saving grid view configurations. If user hides some columns, they are 
//saved in the database for that user. This way different users can use different view configurations.
const saveViewConfigBegin = () => {
  return {
    type: SAVE_VIEW_CONFIGS_BEGIN,
    isFetching: true,
    data: null,
    error: false,
    mesage: '',
  };
};

const saveViewConfigSuccess = (data) => {
  return {
    type: SAVE_VIEW_CONFIGS_SUCCESS,
    isFetching: false,
    error: false,
    data: data,
    success: true,
    message: data.message,
  };
};

const saveViewConfigFailed = (err) => {
  return {
    type: SAVE_VIEW_CONFIGS_FAILURE,
    isFetching: false,
    error: true,
    data: null,
    message: err,
  };
};

export const saveViewConfigData = (params, headers) => {
  return (dispatch) => {
    dispatch(saveViewConfigBegin());
    axios
      .post(BASE_URL + 'save_view_configs', params, headers)
      .then((res) => {
        if (res.data.success) {
          dispatch(saveViewConfigSuccess(res.data));
          toast.success(res.data.message, {
            position: toast.POSITION.TOP_CENTER,
          });
        }
      })
      .catch((err) => {
        console.log(err);
        dispatch(saveViewConfigFailed(err));
        toast.error(err, { position: toast.POSITION.TOP_CENTER });
      });
  };
};

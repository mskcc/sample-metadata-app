import axios from 'axios';
import { BASE_URL, requestHeaders} from '../configs/react.configs';
import Swal from 'sweetalert2';
import { toast } from 'react-toastify';
import {
  LOGIN_USER_BEGIN,
  LOGIN_USER_SUCCESS,
  LOGIN_USER_INVALID,
  LOGIN_USER_FAILURE,
  LOGOUT_USER_BEGIN,
  LOGOUT_USER_SUCCESS,
  LOGOUT_USER_FAILURE,
  SESSION_END_BEGIN,
  SESSION_END_SUCCESS,
  SESSION_END_FAILURE,
} from '../actions/ActionConstants';

//HAS THREE TYPES OF ACTIONS IN THIS FILE. ACTIONS TO LOG IN, LOG-OUT and END-SESSION 
//Redux actions for user login.
const userLoginBegin = () => {
  return {
    type: LOGIN_USER_BEGIN,
    isFetching: true,
    error: false,
  };
};

const userLoginSuccess = (user) => {
  return {
    type: LOGIN_USER_SUCCESS,
    isFetching: false,
    error: false,
    data: user,
    message: user.message,
  };
};

const userLoginInvalid = (user) => {
  return {
    type: LOGIN_USER_INVALID,
    isFetching: false,
    error: true,
    data: user,
    message: user.message,
  };
};

const userLoginFailure = (error) => {
  return {
    type: LOGIN_USER_FAILURE,
    isFetching: false,
    error: true,
    data: null,
    message: error,
  };
};

// login method to make http call to login user
export const login = (data) => {
  return (dispatch) => {
    dispatch(userLoginBegin());
    axios
      .post(BASE_URL + 'login', data, requestHeaders)
      .then((res) => {
        if (res.data.success) {
          dispatch(userLoginSuccess(res.data));
          toast.success(res.data.message, {
            position: toast.POSITION.TOP_CENTER,
          });
        }
        if (!res.data.success) {
          dispatch(userLoginInvalid(res.data));
          toast.error(res.data.message, {
            position: toast.POSITION.TOP_CENTER,
          });
        }
      })
      .catch((err) => {
        dispatch(userLoginFailure(err));
        toast.error(
          'Server error. Try again later or contact ADMINS at zzPDL_SKI_IGO_DATA@mskcc.org',
          { position: toast.POSITION.TOP_CENTER }
        );
      });
  };
};

//Redux actions for user log-out.
const userLogOutBegin = () => {
  return {
    type: LOGOUT_USER_BEGIN,
    isFetching: true,
  };
};

const userLogOutSuccess = (user) => {
  return {
    type: LOGOUT_USER_SUCCESS,
    isFetching: false,
    error: false,
    data: user,
    message: user.message,
  };
};

const userLogOutFailure = (error) => {
  return {
    type: LOGOUT_USER_FAILURE,
    isFetching: false,
    error: true,
    message: error,
  };
};

//method to make http call to log-out user.
export const logout = (data, headers) => {
  return (dispatch) => {
    dispatch(userLogOutBegin());
    axios
      .post(BASE_URL + 'logout', data, headers)
      .then((res) => {
        if (res.data.success) {
          dispatch(userLogOutSuccess(res.data));
          localStorage.clear();
          localStorage.removeItem('persist:root');
          toast.success(res.data.message, {
            position: toast.POSITION.TOP_CENTER,
          });
        }
      })
      .catch((err) => {
        dispatch(userLogOutFailure(err));
        toast.error(
          'Server error. Try again later or contact ADMINS at zzPDL_SKI_IGO_DATA@mskcc.org',
          { position: toast.POSITION.TOP_CENTER }
        );
      });
  };
};


//Redux actions to end user session.
const endSessionBegin = () => {
  return {
    type: SESSION_END_BEGIN,
  };
};

const endSessionSuccess = (user) => {
  return {
    type: SESSION_END_SUCCESS,
    isError: '',
    data: user,
    error: '',
  };
};

const endSessionFailure = (error) => {
  return {
    type: SESSION_END_FAILURE,
    error: error,
  };
};

//method to make http call to end user session
export const endsession = (data, configs, history) => {
  return (dispatch) => {
    dispatch(endSessionBegin());
    axios
      .post(BASE_URL + 'logout', data, configs)
      .then((res) => {
        if (res.data.success) {
          dispatch(endSessionSuccess(res.data));
          localStorage.clear();
          localStorage.removeItem('persist:root');
          history.push("/");
          Swal.fire(
            'Session ended',
            'Session ended due to inactivity. Please log in again',
            'warning'
          );
        }
      })
      .catch((err) => {
        dispatch(endSessionFailure(err));
        Swal.fire(
          'Server error during endsession',
          'Try again later or contact ADMINS at zzPDL_SKI_IGO_DATA@mskcc.org',
          'error'
        );
      });
  };
};

import axios from "axios";
import { BASE_URL, requestHeaders, BASE_ROUTE } from "../configs/react.configs";

const user_login = () => {
  return {
    type: "LOGIN_USER_BEGIN",
    isFetching: true,
    error:false
  };
};

const user_login_success = user => {
  return {
    type: "LOGIN_USER_SUCCESS",
    isFetching: false,
    error: false,
    data: user,
    message:user.message
  };
};

const user_login_invalid = user => {
  return {
    type: "LOGIN_USER_INVALID",
    isFetching:false,
    error:true,
    data: user,
    message:user.message,
};
}

const user_login_failure = error => {
  return {
    type: "LOGIN_USER_FAILURE",
    isFetching:false,
    error:true,
    data: null,
    message: error
  };
};

export const login = (data) => {
  return dispatch => {
    dispatch(user_login());
    axios
      .post(BASE_URL + "login", data, requestHeaders)
      .then(res => {
        if (res.data.valid) {
          dispatch(user_login_success(res.data));
        }
        if (!res.data.valid) {
          dispatch(user_login_invalid(res.data));
        }
      })
      .catch(err => {
        dispatch(user_login_failure(err));
      });
  };
};

const user_logout = () => {
  return {
    type: "LOGOUT_USER_BEGIN",
    isFetching:true,
  };
};

const user_logout_success = user => {
  return {
    type: "LOGOUT_USER_SUCCESS",
    isFetching:false,
    error:true,
    data: user,
    message:user.message,
  };
};

const user_logout_failure = error => {
  return {
    type: "LOGOUT_USER_FAILURE",
    isFetching:false,
    error:true,
    message:error,
  };
};

export const logout = (data, headers) => {
  return dispatch => {
    dispatch(user_logout());
    axios
      .post(BASE_URL + "logout", data, headers)
      .then(res => {
        if (res.data.success) {
          console.log(res.data);
          dispatch(user_logout_success(res.data));
          localStorage.clear();
          localStorage.removeItem("persist:root");
        }
      })
      .catch(err => {
        dispatch(user_logout_failure(err));
      });
  };
};

const session_end = () => {
  return {
    type: "SESSION_END_BEGIN"
  };
};

const session_end_success = user => {
  return {
    type: "SESSION_END_SUCCESS",
    isError: "",
    data: user,
    error: ""
  };
};

const session_end_failure = error => {
  return {
    type: "SESSION_END_FAILURE",
    error: error
  };
};

export const endsession = (data, configs, history) => {
  return dispatch => {
    dispatch(session_end());
    axios
      .post(BASE_URL + "logout", data, configs)
      .then(res => {
        if (res.data.success) {
          dispatch(session_end_success(res.data));
          localStorage.clear();
          localStorage.removeItem("persist:root");
          history.push(`${BASE_ROUTE}/`);
        }
      })
      .catch(err => {
        dispatch(session_end_failure(err));
      });
  };
};

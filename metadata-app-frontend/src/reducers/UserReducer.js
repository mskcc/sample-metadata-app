const initialState = {
  data: null,
  isFetching: false,
  error: false,
  message: "",
};

const UserReducer = (state = initialState, action) => {
  switch (action.type) {
    case "LOGIN_USER_BEGIN":
      return Object.assign({}, state, {
        isFetching: action.isFetching,
        error: action.error,
      });
    case "LOGIN_USER_SUCCESS":
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });
    case "LOGIN_USER_FAILURE":
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });
    case "LOGIN_USER_INVALID":
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });

    // Users actions for Logout Logic
    case "LOGOUT_USER_BEGIN":
      return Object.assign({}, state, {
        isFetching: true,
        error: false,
      });
    case "LOGOUT_USER_SUCCESS":
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });
    case "LOGOUT_USER_FAILURE":
      return Object.assign({}, state, {
        data: action.data,
        isFetching: action.isFetching,
        error: action.error,
        message: action.message,
      });
    case "SESSION_END_SUCCESS":
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
export default UserReducer;

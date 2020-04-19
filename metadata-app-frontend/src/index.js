import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import * as serviceWorker from "./serviceWorker";
import {Provider} from 'react-redux';
import {store}  from './store/Store';
// import {persistor, store}  from './store/Store';
// import { PersistGate } from 'redux-persist/integration/react'
// import {Spinner} from './components/Spinner';

ReactDOM.render(
  <Provider store={store}>
    {/* <PersistGate loading={Spinner} persistor={persistor}> */}
        <App />
    {/* </PersistGate> */}
  </Provider>,

  document.getElementById("root")
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
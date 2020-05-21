import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import * as serviceWorker from "./serviceWorker";
import { Provider } from "react-redux";
import { store, persistor } from "./store/Store";
import "handsontable/dist/handsontable.full.css";
import { PersistGate } from 'redux-persist/integration/react'
import { ToastContainer} from 'react-toastify';

  import 'react-toastify/dist/ReactToastify.css';

ReactDOM.render(
  <Provider store={store}>
    <PersistGate persistor={persistor}>
      <ToastContainer autoClose={3000}/>
      <App/>
    </PersistGate>
  </Provider>,
  document.getElementById("root")
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();

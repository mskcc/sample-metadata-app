import { createStore, applyMiddleware} from "redux";
import RootReducer from "../reducers/RootReducer";
import thunk from "redux-thunk";
import { persistStore, persistReducer } from "redux-persist";
import autoMergeLevel2 from "redux-persist/lib/stateReconciler/autoMergeLevel2";
import storage from "redux-persist/lib/storage";
// import {compose} from "redux";

const persistConfig = {
  key: "root",
  storage: storage,
  stateReconciler: autoMergeLevel2,
  blacklist: ["searchResults"], // see "Merge Process" section for details.
};

const pReducer = persistReducer(persistConfig, RootReducer);
//Following two lines are to support redux devtools extension in browser. This is mostly done for troubleshooting 
//during development. It is advised to turn it off for production build.

//const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose; 
//export const store = createStore(pReducer, composeEnhancers(applyMiddleware(thunk)));

//Comment out the following line if two lines above are uncommented to suppor redux devtools extension in browser.
//It is advised to comment out the two lines above and keep this line uncommented for production builds.
export const store = createStore(pReducer, applyMiddleware(thunk));

//this is persistor to persist redux state on page refreshes.
export const persistor = persistStore(store);

import { createStore, applyMiddleware, compose } from 'redux';
import RootReducer from '../reducers/RootReducer';
import thunk from 'redux-thunk';
// import DevTools from '../components/devtools';
import { persistStore, persistReducer } from 'redux-persist';
import autoMergeLevel2 from 'redux-persist/lib/stateReconciler/autoMergeLevel2';
import storage from 'redux-persist/lib/storage';

const persistConfig = {
    key: 'root',
    storage: storage,
    stateReconciler: autoMergeLevel2,
    blacklist: ['searchResult', 'saveResult'] // see "Merge Process" section for details.
   };

const pReducer = persistReducer(persistConfig, RootReducer);
export const store = createStore(pReducer,undefined, compose(applyMiddleware(thunk)), window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__());
// , DevTools.instrument()));
//export const store = createStore(rootReducer,undefined, compose(applyMiddleware(thunk), DevTools.instrument()));
export const persistor = persistStore(store);
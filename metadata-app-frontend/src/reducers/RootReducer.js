import { combineReducers } from "redux";
import UserReducer from "./UserReducer";
import SearchReducer from "./SearchReducer";
import {SaveDataReducer, SaveViewConfigReducer} from "./SaveDataReducer";

const RootReducer = combineReducers({
  user: UserReducer,
  searchResults: SearchReducer,
  saveDataResults: SaveDataReducer,
  savedUserConfigResults: SaveViewConfigReducer
});

export default RootReducer;

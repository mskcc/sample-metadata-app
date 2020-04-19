import { combineReducers} from 'redux';
import UserReducer from './UserReducer';
import SearchReducer from './SearchReducer';

const RootReducer = combineReducers({
    user: UserReducer,
    searchresults : SearchReducer
});

export default RootReducer;
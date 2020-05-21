import React, { Component } from 'react';
import NavBar from '../components/NavBar';
import Home from '../components/Home';
import IdleTimer from 'react-idle-timer';
import { connect } from 'react-redux';
import { endsession } from '../actions/UserActions';
import { withRouter } from 'react-router';

class HomeView extends Component {
    constructor(props) {
        super(props);
        this.idleTimer = React.createRef();
      }
    onIdle = (e) => {
        console.log('user is idle', e);
        console.log(this.props.user);
        var config = {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            Authorization: 'Bearer ' + this.props.user.access_token,
          },
        };
        this.props.user &&
          this.props.user.access_token &&
          this.props.endsession(this.props.user, config, this.props.history);
      };

  render() {
    return (
      <div>
        {/*IdleTimer is user to track the idle time to end user session if Idle for more than 20 minutes*/}
        <IdleTimer
          ref={this.idleTimer}
          element={document}
          onIdle={this.onIdle}
          debounce={250}
          timeout={1000 * 60 * 20} //define idle time for session timeout. Here it is set to 20 minutes.
        />
        <NavBar />
        <Home />
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  state: state,
  user: state.user.data,
});

const mapDispatchToProps = (dispatch) => ({
  endsession: (data, configs, token) =>
    dispatch(endsession(data, configs, token)),
});

export default withRouter(
  connect(mapStateToProps, mapDispatchToProps)(HomeView)
);

import React from 'react';
import Backdrop from '@material-ui/core/Backdrop';
import CircularProgress from '@material-ui/core/CircularProgress';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  backdrop: {
    zIndex: theme.zIndex.drawer + 1,
    color: '#fff',
  },
}));

//this component is not being used right now in any of the components.
//But this might be useful in future. So, leaving it in the code.
const BackDrop = (props) => {
  const classes = useStyles();
  const isFetching = props;
  return (
    <div>
      <Backdrop className={classes.backdrop} open={isFetching}>
        <CircularProgress color="inherit" />
      </Backdrop>
    </div>
  );
};

export default BackDrop;

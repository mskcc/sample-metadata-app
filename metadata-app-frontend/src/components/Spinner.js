import React from "react";
import CircularProgress from "@material-ui/core/CircularProgress";
import Grid from "@material-ui/core/Grid";

//Componed to display a spinner to indicate data loading/fetching state in components.
class Spinner extends React.Component {
render(){
  return (
    <Grid container justify="center" spacing={3}>
      <CircularProgress />
    </Grid>
  );
}
};

export default Spinner;

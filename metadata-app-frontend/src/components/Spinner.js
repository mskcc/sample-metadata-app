import React from "react";
import CircularProgress from "@material-ui/core/CircularProgress";
import Grid from "@material-ui/core/Grid";

//Componed to display a spinner to indicate data loading/fetching state in components.
class Spinner extends React.Component {
render(){
  return (
    <Grid container justify="center" spacing={3}>
      <Grid
            container
            direction="row"
            justify="center"
            alignItems="flex-end"
          >
      <CircularProgress />
      </Grid>

      <Grid
            container
            direction="row"
            justify="center"
            alignItems="flex-end"
          >
        Fetching large dataset, please be patient.
      </Grid>
    </Grid>
  );
}
};

export default Spinner;

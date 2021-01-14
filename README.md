# covid-data

A dash app to display covid data pulled from an XPrize supplied csv file which is updated daily.

Live as of January 2021 at: https://violet-covid-data.herokuapp.com/

Built with Pandas, Plotly, and Dash in a Flask app.
Deployed to Heroku.

Inspired by participation in the XPrize Covid Response competition of 2020-2021 via team Lavender Spiral.

## Created by

Josh [@Caellwyn](https://github.com/Caellwyn) - Data Scientist

Layla [@laylar](https://github.com/laylar) - DevOps, Front End Developer

## How to Use

Make your selections at the top and a new graph will appear, displaying up-to-date data below!

![Checkboxes and a graph](/img/Screenshot3Lines2021-01-08.png)

## Some Story About Our Process

We started this in a Jupyter Notebook, even got as far as building a prediction model with 99+% accuracy for the United stats between 12/01 and 1/01 using statsmodels SARIMAX. We experimented with fbprophet, too, but didn't have as much success.

Data and displays are useless if no one can see them, however! So we decided to deploy it live.

First, we had to decide which tool to use - React (Dash plays well with React as a component!) or Flask (Flask embraces Python ). Layla has built apps and websites with React before, so why not learn a new framework? We went with Flask.

After some learning curve, trial and error, and a bit of luck, we got a basic Flask app live on Heroku.

From there, we added bit by bit of code on the deploy_branch, testing that it didn't break things by temporarily deploying that branch on Heroku before we pushed to the main branch, which Heroku automatically deploys from.

Unfortunately, we found that the predictive model took too long for Heroku and would timeout before displaying the graph. So we have modified this site to display current data based on user selected criteria, which does not require the predictive modeling to work.

To experience the predictive modeling as it worked locally on 12/07, you can run from git commit c12aa65c9a9dcf69a144efaf5eaf4642dc16d654, "Merge branch 'deploy_model' of https://github.com/Violet-Spiral/covid-predict into deploy_model" on main branch.

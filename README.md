# Strava Run Analyzer

### Motivation
I use Strava (www.strava.com) to log my runs. I've recently survived two marathons. For both I've followed the same training plan.
And both I've finished in roughly the same time. While Strava is a great tool to log and analyze each workout, I was curious to see to what extend the two training seasons leading up to the marathons differed.

Running in Manhattan, I noticed that the velocity Stava calculates for some of my run intervals is sometimes extremely unrealistic. 
As an example, the recorded velocity for some splits for a recent run exceed 17m/s ~ 38 mph. This _must_ be wrong - I am clearly not that fast.

<img src='https://github.com/StofAle/Strava_Speed_Correction/blob/master/img/inst_velo_sample_run.png' width=400px>

I suspect the reason for this to be GPS location issues. These data quality issues will be taken into account when re-evaluating the velocities for the runs.

Note: Only recently (05/20/2020), Strava has restricted the 'training log' (dashboard that shows for each day of the past weeks the workout type and length) as well as the interval stats for each run or bike ride to premium users only. Non-premium users like me will simply no longer have access to these dashboards.

### Overview and Results
The script gives an example on how to download Strava data from their API and remove unwanted irregularities in the time/distance data from it.
As an example and illustration of the recorded data, I've analyzed and compared my running data for two marathon training seasons. A comparison between the two marathon training seasons can be summarized in the following plots which show:

1. Histogram of run distances (x-axis in meter)
<img src='https://github.com/StofAle/Strava_Speed_Correction/blob/master/img/distance_histogram.png' width=400px>

2. A comparison of the average velocities of the runs in both training seasons
<img src='https://github.com/StofAle/Strava_Speed_Correction/blob/master/img/ave_velocities_comparison.png' width=400px>

3.  A comparison of the average standard deviation of the velocities of the runs in both training seasons
<img src='https://github.com/StofAle/Strava_Speed_Correction/blob/master/img/ave_std_comparison.png' width=400px>

### Setup
The analysis is contained in the Jupyter Notebook Strava_analyzer_vXYZ.ipynb. The structure of the respository is as follows:


```
├── README.md          <- The README 
├── src
│   ├── ToolBox.py     <- Collection of custom functions used throughout the  analysis
│
├── img                <- A few images visualizing the raw and processed Strava run data
│

```

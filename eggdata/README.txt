Notes: 
=====
a) Missing values in raw data and summary statistics are marked as -999. This can happen when an Egg reports bad data such as 0 out of 200 trials per second.
b) utime is Unix Epoch time in seconds, i.e., time in seconds since 01-Jan-1970. Multiply this by 1000 if your computer program expects Epoch time in milliseconds. 
c) To convert utime into normal date-time in spreadsheets use the formula '=<utime>/86400+25569' and format the cell(s) to display date and time. The formula is equivalent to '=<utime>/(24*60*60)+DATE(1970;1;1)' in Microsft Excel and '=<utime>/(24*60*60)+DATEVALUE("1/1/1970")' in OpenOffice/LibreOffic Calc.


Exported Data
=============

The "gcp_eggdata.csv" file consists of raw trial and summary data under the following sections:

1) Start Time: Start time for this data analysis as Unix Epoch Time in seconds and human readable UTC time string (i.e., GMT timezone)

2) End Time:  End time for this data analysis as Unix Epoch Time in seconds and human readable UTC time string (i.e., GMT timezone)

3) List of EggIDs : A list of IDs for the REG devices for which the data is available for each one-minute time period. This list rarely changes, but can change sometimes as new Eggs are added and old ones get decomissioned or their data is not avialable for some reason.
Contains fields:
- utime at start of minute: Unix Epoch time in seconds for which the data exists.
- EggID1, EggID2, EggID3...: List of IDs for individual Eggs that reported data for the minute starting at specified utime.

4) Per minute summation of raw trial data for each Egg: This is the per-minute and per-Egg summation of raw trial data. This is almost always for 60 seconds and hence out of 1200 trials (at 200 trials/second), but on very rare occasions an Egg may report bad data for a few seconds. Please cross-check against per second data further below. If some of the per second data values are -999 then the number of bad seconds needs to be accounted for while using per minute summation.
Contains fields:
- utime at start of minute: Unix Epoch time in seconds for which the data exists.
- EggID1, EggID2, EggID3...: Per minute summation of trials for Eggs. The sequence of EggIDs being the same as in the List of EggIDs section above for the corresponding minute.

5) Per minute Z-scores for each Egg: These are the per-minute Z-Scores computed for each egg. This is almost always for 60 seconds and hence out of 1200 trials (at 200 trials/second), but on very rare occasions an Egg may report bad data for a few seconds. Please cross-check against per second data further below. The Z-score computation ignores all seconds for which the egg data is -999.
Contains fields:
- utime at start of minute: Unix Epoch time in seconds for which the data exists.
- EggID1, EggID2, EggID3...: Per minute Z-scores for Eggs. The sequence of EggIDs being the same as in the List of EggIDs section above for the corresponding minute.

6) Per minute CumSum(Z^2 - 1) for each Egg: This is the accumulating Z-Squared sum per-minute for each egg. 
Contains fields:
- utime at start of minute: Unix Epoch time in seconds for which the data exists.
- EggID1, EggID2, EggID3...: Accumulating CumSum(Z^2-1) for each Egg. The sequence of EggIDs being the same as in the List of EggIDs section above for the corresponding minute.

7) Per minute CumSum(Z^2 - 1) for entire network: Accumulating sum of Squared Stouffer Z Score for the entire network of eggs taken as a whole for the given minute.
Contains fields:
- utime at start of minute: Unix Epoch time in seconds for which the data exists.
- Cumulative Sum: Accumulating CumSum(Z^2 - 1) at the given minute.

8) Per second raw trial data for each Egg: Raw per-second traial data for each egg (out of 200 trials/second). A value of -999 indicates that the Egg reported bad data for the second and this should be removed during analysis.Contains fields:
- utime for the second: Unix Epoch time in seconds for which the data exists.
- EggID1, EggID2, EggID3...: Per second trial data for the Eggs. The sequence of EggIDs being the same as in the List of EggIDs section above for the corresponding minute.

9) Per second Z-score for each Egg: These are the per-second Z-Scores computed for each egg. A value of -999 for any Egg indicates that the Egg reported bad data for that second.
Contains fields:
- utime for the second: Unix Epoch time in seconds for which the data exists.
- EggID1, EggID2, EggID3...: Per second Z-scores for Eggs. The sequence of EggIDs being the same as in the List of EggIDs section above for the corresponding minute.

10) Per second CumSum(Z^2 - 1) for each Egg and : This is the accumulating Z-Squared sum per-second for each egg. 
Contains fields:
- utime for the second: Unix Epoch time in seconds for which the data exists.
- EggID1, EggID2, EggID3...: Accumulating CumSum(Z^2-1) for each Egg. The sequence of EggIDs being the same as in the List of EggIDs section above for the corresponding minute.

11) Per second Stouffer Z and CumSum(Z^2 - 1) for entire network: Stouffer Z and accumulating sum of Squared Stouffer Z Score for the entire network of eggs taken as a whole for the given second.
Contains fields:
- utime for the second: Unix Epoch time in seconds for which the data exists.
- Stouffer Z: Stouffer Z score for the enitire network for the second (ignoring bad eggs).
- CumSum(Z^2 - 1): Per second accumulating sum of squared Stouffer Z-Score for the entire network.

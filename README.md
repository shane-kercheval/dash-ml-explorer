# dash-ml-explorer




## Folder Structure

- `projects`
    - each folder within the `projects` folder contains all information for a single dataset (e.g. a single classification dataset)
- each folder within the `projects` folder contains
    - all runs (a.k.a experiments) for a single model (e.g. Random Forest), which includes the resulting `.yaml` files
        - each `.yaml` files contains the cross validation rusults for a single run i.e. single execution of a `SearchCV` object (e.g. ....)
    - `Final Model.yaml` ????? which contains information about the final model selected from all of the Runs (e.g. the final Random Forest model selected)



## Notes

- Summary
    - comparison of all final models
        - classification:
        - roc
        - etc.
        - scores
    - highlight the best model/score/parameters

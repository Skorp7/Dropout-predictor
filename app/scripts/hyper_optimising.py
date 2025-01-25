import optuna
from optuna.logging import set_verbosity, WARNING
import xgboost as xgb
import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import make_scorer, fbeta_score

# Global variables
X            = None
y            = None
beta         = None
fixed_params = {}

def fbeta_scorer(y_true, y_pred):
    return fbeta_score(y_true, y_pred, beta=beta)

def objective(trial):
    # Define the hyperparameters to tune
    param = {
        'scale_pos_weight': trial.suggest_float('scale_pos_weight', 0.1, 5),
        'eta': trial.suggest_float('eta', 0.01, 0.3),
        'max_depth': trial.suggest_int('max_depth', 3, 18),
        'min_child_weight': trial.suggest_int('min_child_weight', 0, 10),
        'gamma': trial.suggest_float('gamma', 0, 0.2),
    }
    # Add fixed parameters, which are same for all trials
    param.update(fixed_params)

    # Create custom scorer using fbeta_score with beta
    scorer = make_scorer(fbeta_scorer, greater_is_better=True)

    # 5-fold cross-validation
    skf    = StratifiedKFold(n_splits=5, shuffle=True, random_state=40)
    f_beta = cross_val_score(xgb.XGBClassifier(**param), X, y, cv=skf, scoring=scorer).mean()

    return f_beta

"""
Find best hyperparameters for model. F-score is used as the objective (to be maximised).
data - the training data
target - the target data
b - the beta value to use in the F-score
"""
def find_best_params(data: pd.DataFrame, target: pd.DataFrame, b: float, fixed_params_dict: dict, trials: int):
    global X, y, beta, fixed_params
    # Set globals
    X            = data
    y            = target
    beta         = b
    fixed_params = fixed_params_dict

    # Set verbosity to WARNING to avoid too much output
    set_verbosity(WARNING)

    # Create the study and optimize the objective function
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=trials, show_progress_bar=True)

    # Get the best hyperparameters
    return study.best_params

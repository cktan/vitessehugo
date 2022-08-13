---
#layout: post

date: "2019-03-18"

author: Eric Lam

categories: ["machine learning"]

title: Introduction to Machine Learning with Tensorflow and Deepgreen Transducer
description: "Example of tensorflow with deepgreen transducer"
keywords: Tensorflow, Transducer, Python, SQL

headline: Blog
subheadline:
type: "post"

---

Today, we will show you how to build machine learning models with tensorflow and transducer.


Deepgreen Transducer is the scripting relational database engine that is tightly integrated with relation engine, including
query optimizer, query executor and can be executed in parallel with other query operators.  With transducer, we
can efficiently execute queries that are very difficult to express in SQL. See [Scripting Relational Database Engine Using Transducer](https://www.researchgate.net/publication/325118009_Scripting_Relational_Database_Engine_Using_Transducer).

<!--more-->

---

The great thing about transducer is that you don't have to export the data from Deepgreen to model it.  You
can create your model where the data is.

We will walk you through the process of training, evaluating and testing machine learning models using Deepgreen
Transducer, using publicy available datasets.

Let's get started.

Assume you have tensorflow and python3 installed.  We now install the [Deepgreen Python transducer API](https://github.com/vitesse-ftian/dgnb).

```
% git clone https://github.com/vitesse-ftian/dgnb
% cd dgnb/py
% python3 setup.py install --user
```

This example uses the [saturn training data](https://raw.githubusercontent.com/jasonbaldridge/try-tf/master/simdata/saturn_data_train.csv) and [saturn evaluate data](https://raw.githubusercontent.com/jasonbaldridge/try-tf/master/simdata/saturn_data_eval.csv) for training and evaluating the models.  The data contains three columns [tag, x, y].

First, we load the data from external CSV files to Deepgreen table.  Create the Python script load.py as below.

```
#!/usr/bin/env python
# coding: utf-8

# As usural, we open a database connection.   
import dg.conn
import dg.xtable
from dg.dsutil.csv import CsvXt

con = dg.conn.Conn(user="ericlam", database="template1")
con.conn.autocommit = True

# Load training data into a table
# Just run this once
saturn_train = CsvXt('https://raw.githubusercontent.com/jasonbaldridge/try-tf/master/simdata/saturn_data_train.csv')
saturn_train.add_col('tag', 'int')
saturn_train.add_col('x', 'float4')
saturn_train.add_col('y', 'float4')
xt = saturn_train.xtable(con)
xt.ctas('saturn_train')

saturn_eval = CsvXt('https://raw.githubusercontent.com/jasonbaldridge/try-tf/master/simdata/saturn_data_eval.csv')
saturn_eval.add_col('tag', 'int')
saturn_eval.add_col('x', 'float4')
saturn_eval.add_col('y', 'float4')
xt = saturn_eval.xtable(con)
xt.ctas('saturn_eval')
```

Run the load.py to create and load the table.  It will create two tables with the data in the csv files.
```
$ python3 load.py
```

To check the data exist in the database, 
```
% psql template1
template1=# select * from saturn_train limit 1;
 tag |    x     |    y     
-----+----------+----------
   1 | -7.12397 | -5.05176
(1 row)

template1=# select * from saturn_eval limit 1;
 tag |    x     |    y     
-----+----------+----------
   0 | -2.95364 | 0.424072
(1 row)
```

To train and evaluate the model, a python script is written to generate Transducer SQL and submit to the Deepgreen database for execution.  Create the Python script train_evaluate.py as follow:

```
#!/usr/bin/env python
# coding: utf-8

# As usural, we open a database connection.   
import dg.conn
import dg.xtable
from dg.dsutil.csv import CsvXt

con = dg.conn.Conn(user="ericlam", database="template1")
con.conn.autocommit = True

# Load data from table
xt1 = dg.xtable.fromTable(con, 'saturn_train')
xt2 = dg.xtable.fromTable(con, 'saturn_eval')

# Build estimator:
import dg.tf.estimator
e = dg.tf.estimator.Estimator()
e.add_out_col('loss', 'float4')
e.add_out_col('accuracy_baseline', 'float4')
e.add_out_col('global_step', 'float4')
e.add_out_col('recall', 'float4')
e.add_out_col('auc', 'float4')
e.add_out_col('prediction_mean', 'float4')
e.add_out_col('precision', 'float4')
e.add_out_col('label_mean', 'float4')
e.add_out_col('average_loss', 'float4')
e.add_out_col('auc_precision_recall', 'float4')
e.add_out_col('accuracy', 'float4')

# adding input. idx 0 = saturn_train, idx 1 = saturn_eval
e.tfinput.add_xt(xt1, repeat=10)
e.tfinput.add_xt(xt2)

# Tensorflow code.   Build columns, estimator are both trivial.
# Just hook up the estimator with table input.

tfcode = """
def build_model_columns():
    x = tf.feature_column.numeric_column('x')
    y = tf.feature_column.numeric_column('y')
    return [x, y]
    
def build_estimator():
    cols = build_model_columns()
    hidden_units = [10, 10]
    run_config = tf.estimator.RunConfig().replace(
        session_config=tf.ConfigProto(device_count={'GPU': 0})
    )
    
    return tf.estimator.DNNClassifier(
        model_dir='/tmp/saturn_dnn',
        feature_columns = cols,
        hidden_units = hidden_units,
        config = run_config
    )
    
def input_fn(ii, cache_rs=False):
    features = sql_input_fn(ii, cache_rs)
    label = features.pop('tag')
    return features, tf.equal(label, 1)

def main(unused_args):
    model = build_estimator()
# input_fn(0) is the saturn_train
    model.train(input_fn=lambda: input_fn(0))
    sql_clear_cached_rs()

# input_fn(1) is saturn_eval.
    eval_result = model.evaluate(input_fn=lambda: input_fn(1))
    sys.stderr.write(str(eval_result))
    sql_clear_cached_rs()
    rec = []
    rec.append(eval_result['loss'])
    rec.append(eval_result['accuracy_baseline'])
    rec.append(eval_result['global_step'])
    rec.append(eval_result['recall'])
    rec.append(eval_result['auc'])
    rec.append(eval_result['prediction/mean'])
    rec.append(eval_result['precision'])
    rec.append(eval_result['label/mean'])
    rec.append(eval_result['average_loss'])
    rec.append(eval_result['auc_precision_recall'])
    rec.append(eval_result['accuracy'])
    vitessedata.phi.WriteOutput(rec)
    vitessedata.phi.WriteOutput(None)

"""

# If previous transaction failed, the con transaction state is active, but failed.
# Any further query will fail.   Just rollback ...
con.conn.commit()
e.add_tf_code(tfcode)
ext = e.build_xt(con)
print(ext.show())

```

To take a closer look of the transducer code, we can separate the code into four parts.

The first part is to declare the data source from the external table saturn_train and saturn_eval.

```
con = dg.conn.Conn(user="ericlam", database="template1")
con.conn.autocommit = True

# Load data from table
xt1 = dg.xtable.fromTable(con, 'saturn_train')
xt2 = dg.xtable.fromTable(con, 'saturn_eval')

```

The second part is to declare the input and output of transducer.  For input, transducer needs 
two type of inputs: data source and tensorflow python code.  We pass both ```saturn_train``` 
and ```saturn_eval``` data source to estimator for data loading.  We also set the 
output columns as output format.

```
import dg.tf.estimator
e = dg.tf.estimator.Estimator()
e.add_out_col('loss', 'float4')
e.add_out_col('accuracy_baseline', 'float4')
e.add_out_col('global_step', 'float4')
e.add_out_col('recall', 'float4')
e.add_out_col('auc', 'float4')
e.add_out_col('prediction_mean', 'float4')
e.add_out_col('precision', 'float4')
e.add_out_col('label_mean', 'float4')
e.add_out_col('average_loss', 'float4')
e.add_out_col('auc_precision_recall', 'float4')
e.add_out_col('accuracy', 'float4')

# Adding input
e.tfinput.add_xt(xt1, repeat=10)
e.tfinput.add_xt(xt2)

```

The third part is the tensorflow python script in string format which will be embedded into the SQL for execution.  Here, we use ```DNNClassifier``` to classify the saturn data.  This example is copied from the tensorflow example and only modified the ```input_fn``` for data loading.

```
tfcode = """
def build_model_columns():
    x = tf.feature_column.numeric_column('x')
    y = tf.feature_column.numeric_column('y')
    return [x, y]
    
def build_estimator():
    cols = build_model_columns()
    hidden_units = [10, 10]
    run_config = tf.estimator.RunConfig().replace(
        session_config=tf.ConfigProto(device_count={'GPU': 0})
    )
    
    return tf.estimator.DNNClassifier(
        model_dir='/tmp/saturn_dnn',
        feature_columns = cols,
        hidden_units = hidden_units,
        config = run_config
    )
    
def input_fn(ii, cache_rs=False):
    features = sql_input_fn(ii, cache_rs)
    label = features.pop('tag')
    return features, tf.equal(label, 1)

def main(unused_args):
    model = build_estimator()
# input_fn(0) is the saturn_train
    model.train(input_fn=lambda: input_fn(0))
    sql_clear_cached_rs()

# input_fn(1) is saturn_eval.
    eval_result = model.evaluate(input_fn=lambda: input_fn(1))
    sys.stderr.write(str(eval_result))
    sql_clear_cached_rs()
    rec = []
    rec.append(eval_result['loss'])
    rec.append(eval_result['accuracy_baseline'])
    rec.append(eval_result['global_step'])
    rec.append(eval_result['recall'])
    rec.append(eval_result['auc'])
    rec.append(eval_result['prediction/mean'])
    rec.append(eval_result['precision'])
    rec.append(eval_result['label/mean'])
    rec.append(eval_result['average_loss'])
    rec.append(eval_result['auc_precision_recall'])
    rec.append(eval_result['accuracy'])
    vitessedata.phi.WriteOutput(rec)
    vitessedata.phi.WriteOutput(None)

"""
```

The last part is to add the tensorflow code to the transducer with ```e.add_tf_code``` function and execute the transducer code and print out the result.

```
con.conn.commit()
e.add_tf_code(tfcode)
ext = e.build_xt(con)
print(ext.show())
```

Run the train_evaluate.py to train and evaluate the model.  The model will be saved in ```/tmp/saturn_dnn``` directory.  

The output columns are the result from the tensorflow function ```tf.estimator.DNNClassifier.evaluate```.  It returns

* A dict containing the evaluation metrics specified in model_fn keyed by name, as well as an entry global_step which contains the value of the global step for which this evaluation was performed. For canned estimators, the dict contains the loss (mean loss per mini-batch) and the average_loss (mean loss per sample). Canned classifiers also return the accuracy. Canned regressors also return the label/mean and the prediction/mean.



```
% python3 train_evaluate.py

+---------+---------------------+---------------+----------+-------+-------------------+-------------+--------------+----------------+------------------------+------------+
|    loss |   accuracy_baseline |   global_step |   recall |   auc |   prediction_mean |   precision |   label_mean |   average_loss |   auc_precision_recall |   accuracy |
|---------+---------------------+---------------+----------+-------+-------------------+-------------+--------------+----------------+------------------------+------------|
| 11.8054 |                0.52 |            50 |        1 |     1 |          0.572856 |    0.981132 |         0.52 |       0.118054 |                      1 |       0.99 |
+---------+---------------------+---------------+----------+-------+-------------------+-------------+--------------+----------------+------------------------+------------+

```


To predict the data, the script is similar to ```train_evaluate.py``` except use ```tf.estimator.DNNClassifier.predict``` function to predict the data and output the columns of the prediction results. Create the python script predict.py as below.


```
#!/usr/bin/env python
# coding: utf-8

# As usural, we open a database connection.   
import dg.conn
import dg.xtable
from dg.dsutil.csv import CsvXt

con = dg.conn.Conn(user="ericlam", database="template1")
con.conn.autocommit = True


# Load data from table
xt2 = dg.xtable.fromTable(con, 'saturn_eval')

# Build estimator:
import dg.tf.estimator
e = dg.tf.estimator.Estimator()
e.add_out_col('data_tag', 'int')
e.add_out_col('data_x', 'float4')
e.add_out_col('data_y', 'float4')
e.add_out_col('prediction', 'int')

# Adding input
e.tfinput.add_xt(xt2)

# Tensorflow code.   Build columns, estimator are both trivial.
# Just hook up the estimator with table input.

tfcode = """
def build_model_columns():
    x = tf.feature_column.numeric_column('x')
    y = tf.feature_column.numeric_column('y')
    return [x, y]
    
def build_estimator():
    cols = build_model_columns()
    hidden_units = [10, 10]
    run_config = tf.estimator.RunConfig().replace(
        session_config=tf.ConfigProto(device_count={'GPU': 0})
    )
    
    return tf.estimator.DNNClassifier(
        model_dir='/tmp/saturn_dnn',
        feature_columns = cols,
        hidden_units = hidden_units,
        config = run_config
    )
def input_fn(ii, cache_rs=False):
    features = sql_input_fn(ii, cache_rs)
    label = features.pop('tag')
    return features, tf.equal(label, 1)

def main(unused_args):
    model = build_estimator()

# input_fn(0) is the saturn_eval
    results = model.predict(input_fn=lambda: input_fn(0, cache_rs=True))

    data = sql_cached_rs()
    idx = 0
    for res in results:
        resval = res['class_ids'][0]
        rec = data[idx][:]
        rec.append(resval)
        vitessedata.phi.WriteOutput(rec)
        idx += 1
    vitessedata.phi.WriteOutput(None)
"""

# If previous transaction failed, the con transaction state is active, but failed.
# Any further query will fail.   Just rollback ...
con.conn.commit()
e.add_tf_code(tfcode)
ext = e.build_xt(con)
print(ext.show())

```

Run the predict.py to predict the data.

```
% python3 predict.py 
+------------+--------------+-------------+--------------+
|   data_tag |       data_x |      data_y |   prediction |
|------------+--------------+-------------+--------------|
|          0 |  -2.95364    |   0.424072  |            0 |
|          1 |   9.05324    |   3.83323   |            1 |
|          1 |  -9.41899    |  -5.15292   |            1 |
|          0 |   0.0259142  |   0.013177  |            0 |
|          1 |  -5.98582    |   9.74873   |            1 |
|          1 |  -7.49102    |  -5.48394   |            1 |
|          1 |   8.6591     |  -2.32603   |            1 |
|          1 |   8.26922    |  -6.56763   |            1 |
|          0 |   2.40183    |   1.10657   |            0 |
|          0 |  -0.465756   |  -0.807678  |            0 |
|          1 |  10.2847     |   0.828401  |            1 |
|          0 |   1.88927    |  -3.06093   |            0 |
... more
+------------+--------------+-------------+--------------+
```

